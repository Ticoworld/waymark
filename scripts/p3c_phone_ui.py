"""Explicit Samsung normal UI driver. Secrets only through protected temporary input.

No authentication bypass, screenshots, clipboard, raw UI/log output or DB edits.
The original emulator drivers/validators are not changed.
"""
import base64
import datetime
import json
import re
import time
import uuid
import xml.etree.ElementTree as ET
import h02_package as p
from h02_device import ROOT, APP, REMOTE_ROOT
from p3c_phone_destination import PhoneDevice, SERIAL, RECEIPT
from p3_fixture import FIXTURE, verify

BASE=ROOT/'runs/wo3c/phone-ab'
INPUT=ROOT/'private/wo3c/automation-input.json'
UIJAR=ROOT/'runs/wo3b1-r2/ui-helper-actions/helper.jar'


def device():
    return PhoneDevice(SERIAL,p.read_json(RECEIPT),execute=True)


def event(role,name,**public):
    p.require(role in ('control','candidate'),'invalid-role')
    out=BASE/role
    out.mkdir(parents=True,exist_ok=True)
    row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'monotonic':time.monotonic(),'event':name,**public}
    p.secret_gate(p.encode(row))
    with (out/'events.jsonl').open('ab') as f:f.write(p.encode(row)+b'\n')
    print(name,flush=True)
    return row


def nodes(d=None):
    d=d or device()
    raw=d.call('exec-out','uiautomator','dump','/dev/tty').decode(errors='replace')
    start=raw.find('<?xml');end=raw.find('</hierarchy>',start)
    p.require(start>=0 and end>=start,'ui-stream-unavailable')
    return list(ET.fromstring(raw[start:end+12]).iter('node'))


def system_auth(ns):
    return any(n.get('package') in ('com.android.systemui','com.samsung.android.biometrics.app.setting')
               and any(x in (n.get('resource-id','')+' '+n.get('content-desc','')).lower()
                       for x in ('biometric','fingerprint','credential','pinentry','passwordentry')) for n in ns)


def safe_view():
    ns=nodes(); fixture=json.loads(FIXTURE.read_text(encoding='utf-8'))
    words=set(fixture['wallets'][0]['mnemonic'].split())
    pin=json.loads(INPUT.read_text())['pin']
    def redact(text):
        text=text.replace(pin,'[PRIVATE REDACTED]')
        return re.sub(r'[A-Za-z]+',lambda m:'[PRIVATE REDACTED]' if m[0].lower() in words else m[0],text)
    result=[]
    for n in ns:
        a=n.attrib
        if not any(a.get(k) for k in ('text','content-desc','resource-id')):continue
        text='[EDITABLE REDACTED]' if a.get('class')=='android.widget.EditText' or a.get('password')=='true' else redact(a.get('text',''))
        # System auth UI: omit all text and keypad IDs/values.
        if a.get('package')!=APP:
            continue
        result.append({'text':text,'description':redact(a.get('content-desc','')),
                       'id':a.get('resource-id',''),'bounds':a.get('bounds',''),
                       'class':a.get('class','')})
    print(json.dumps({'systemAuthVisible':system_auth(ns),'publicPocketNodes':result}),flush=True)


def center(n):
    coords=list(map(int,re.findall(r'\d+',n.get('bounds',''))))
    p.require(len(coords)==4,'ui-bounds')
    return str((coords[0]+coords[2])//2),str((coords[1]+coords[3])//2)


def tap(text=None,public_id=None,description=None):
    d=device()
    if description:
        matches=[n for n in nodes(d) if n.get('package')==APP and n.get('content-desc')==description]
        p.require(len(matches)==1,'ambiguous-public-description')
        d.shell('input','tap',*center(matches[0]));time.sleep(.7);return
    remote='/data/local/tmp/h02-phone-ui-'+uuid.uuid4().hex[:16]+'.jar'
    try:
        d.call('push',str(UIJAR),remote)
        p.require(d.shell('sha256sum',remote).decode().split()[0]==p.sha(UIJAR),'ui-helper-hash')
        args=['uiautomator','runtest',remote,'/system/framework/android.test.base.jar','-c','h02.H02FillPhrase#testPublicTap']
        if public_id:args+=['-e','publicId',public_id]
        else:
            p.require(text is not None,'public-selector-required')
            args+=['-e','publicTextB64',base64.b64encode(text.encode()).decode()]
        raw=d.shell(*args)
        if not (b'H02_PUBLIC_TAP_OK' in raw and b'FAILURES' not in raw):
            print('PUBLIC_ACTION_STAGE='+','.join(x.decode() for x in re.findall(rb'STAGE=(foreground|exists|enabled|click)',raw)))
        p.require(b'H02_PUBLIC_TAP_OK' in raw and b'FAILURES' not in raw,'public-ui-action-refused')
    finally:d.shell('rm','-f',remote)


def private_input(kind):
    p.require(kind in ('phrase','pin'),'private-input-kind')
    d=device()
    if kind=='phrase':
        fixture=json.loads(FIXTURE.read_text(encoding='utf-8'));verify(fixture)
        data={'mnemonic':fixture['wallets'][0]['mnemonic']}
        action='testFillOnly';marker=b'H02_PHRASE_FIELDS_FILLED; NOT_SUBMITTED'
    else:
        data={'pin':json.loads(INPUT.read_text())['pin']}
        action='testEnterPrivatePin';marker=b'H02_PRIVATE_PIN_ENTERED'
    path=REMOTE_ROOT+'/files/h02-'+kind+'-'+uuid.uuid4().hex[:16]+'.json'
    remote='/data/local/tmp/h02-phone-private-ui-'+uuid.uuid4().hex[:16]+'.jar'
    try:
        d.call('push',str(UIJAR),remote)
        p.require(d.shell('sha256sum',remote).decode().split()[0]==p.sha(UIJAR),'ui-helper-hash')
        d.put(path,p.encode(data));d.sandbox('chmod','600',path)
        raw=d.shell('uiautomator','runtest',remote,'/system/framework/android.test.base.jar',
                    '-c','h02.H02FillPhrase#'+action,'-e','fixture',path)
        p.require(marker in raw and b'FAILURES' not in raw,'protected-private-ui-refused')
    finally:
        d.sandbox('rm','-f',path);d.shell('rm','-f',remote)
    print('PROTECTED_'+kind.upper()+'_INPUT_COMPLETE; no value emitted',flush=True)


def back():device().shell('input','keyevent','KEYCODE_BACK')

def nav(text):
    ns=nodes()
    height=max((int(re.findall(r'\d+',n.get('bounds','[0,0][0,0]'))[-1]) for n in ns),default=0)
    matches=[n for n in ns if n.get('package')==APP and n.get('text')==text and int(center(n)[1])>=height*.85]
    p.require(len(matches)==1,'bottom-navigation-selector')
    device().shell('input','tap',*center(matches[0]));time.sleep(1)

def select_account(index):
    tap(description='Switch')
    tap(text='ckt1qzda0c...7rmyth' if index==0 else 'Phone Account 1')
    time.sleep(3)
    p.require(any(n.get('text')=='ckt1qz...'+('myth' if index==0 else 'pweu') for n in nodes()),'selected-public-account-identity')

def reconcile(role,label):
    ns=nodes()
    if any(n.get('text')=='Got it' for n in ns):tap(text='Got it')
    nav('Wallet');observations=[]
    for index in (0,1):
        select_account(index)
        texts=[n.get('text','') for n in nodes()]
        p.require('CKB Testnet' in texts,'selected-network')
        balances=[t for t in texts if re.fullmatch(r'[\d,]+\.\d+ CKB',t)]
        nav('Activity');time.sleep(2);nav('DAO');time.sleep(5)
        texts=[n.get('text','') for n in nodes() if n.get('class')!='android.widget.EditText']
        allowed=[t for t in texts if re.fullmatch(r'(?:[\d,]+\.\d+ CKB|[+~]?[\d,.]+ CKB|Deposited|Locked|Unlockable|Withdrawing|Active|Completed|No deposits yet|Deposit|Withdraw|Unlock|Nervos DAO|.*epochs?.*|.*CKB locked.*)',t,re.I)]
        observations.append({'accountIndex':index,'homeBalances':balances,'daoLabels':allowed})
        nav('Wallet')
    out=BASE/role/(label+'-ui.json');p.require(not out.exists(),'reconcile-evidence-exists')
    with out.open('xb') as f:f.write(p.encode({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'method':'Normal per-account Wallet/Activity/DAO navigation; no transaction', 'observations':observations}))
    event(role,'per_account_app_reconciliation_complete',label=label)

def ack_page_warning(role):
    ns=nodes()
    if not any(n.get('package')=='android' and n.get('text')=='Android app compatibility' for n in ns):return False
    buttons=[n for n in ns if n.get('package')=='android' and n.get('resource-id')=='android:id/button2' and n.get('text')=='OK']
    p.require(len(buttons)==1,'known-page-warning-button')
    device().shell('input','tap',*center(buttons[0]))
    event(role,'known_16kb_warning_acknowledged_once',pageSize=4096)
    time.sleep(1)
    return True

def unlock(role):
    ack_page_warning(role)
    for _ in range(15):
        ns=nodes()
        if system_auth(ns):
            event(role,'SYSTEM_AUTH_WAITING');return False
        if any(n.get('resource-id')=='home-balance-row' for n in ns):return True
        if any(n.get('resource-id')=='auth-use-pin' for n in ns):
            tap(public_id='auth-use-pin');private_input('pin');event(role,'normal_pocket_pin_unlock_complete')
        time.sleep(1)
    raise p.Refused('normal-home-unlock-not-observed')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['view','tap','phrase','pin','back'])
    parser.add_argument('--text');parser.add_argument('--id');parser.add_argument('--description')
    args=parser.parse_args()
    try:
        if args.action=='view':safe_view()
        elif args.action=='tap':tap(args.text,args.id,args.description)
        elif args.action in ('phrase','pin'):private_input(args.action)
        else:back()
    except Exception as e:
        print('PHONE_UI_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else '')+'; no raw diagnostics')
        raise SystemExit(2)
