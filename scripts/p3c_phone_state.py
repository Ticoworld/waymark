"""Phone-only reset, public state/security observations and frozen audit captures."""
import argparse
import datetime
import json
import uuid
import h02_package as p
from h02_device import ROOT,APP,REMOTE_ROOT
from p3c_phone_ui import BASE,device,event
from b2r2_observe import native

def save(path,result):
    p.require(not path.exists(),'evidence-output-exists')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:f.write(p.encode(result))

def security(d):
    local=BASE/'security-helper/helper.jar'
    remote='/data/local/tmp/h02-phone-security.jar'
    d.call('push',str(local),remote);d.shell('chmod','444',remote)
    p.require(d.shell('sha256sum',remote).decode().split()[0]==p.sha(local),'security-helper-digest')
    raw=d.sandbox('env','CLASSPATH='+remote,'/system/bin/app_process','/system/bin','h02.H02PhoneSecurity')
    matches=[s.split(b'=',1)[1] for s in raw.splitlines() if s.startswith(b'H02_PHONE_SECURITY_JSON=')]
    p.require(len(matches)==1,'security-metadata-refused')
    result=json.loads(matches[0]);result['helperSha256']=p.sha(local)
    return result

def reset(role):
    p.require((BASE/'pre-destructive-check.json').is_file(),'custody-precheck-required')
    output=BASE/role/'fresh-state.json'
    p.require(not output.exists(),'role-already-reset')
    if role=='candidate':
        accepted=p.read_json(BASE/'control/result.json')
        p.require(accepted['result']=='PASS','control-not-accepted')
        seal=p.read_json(BASE/'control/evidence-manifest.json')
        for row in seal['files']:p.require(p.sha(ROOT/row['path'])==row['sha256'],'control-evidence-unsealed')
    d=device()
    old_security=security(d)
    event(role,'pocket_only_reset_begin')
    d.shell('am','force-stop','--user','0',APP)
    d.shell('pm','enable','--user','0',APP)
    result=d.shell('pm','clear','--user','0',APP)
    p.require(result.strip()==b'Success','pocket-reset-refused')
    d.stopped()
    checks={}
    for name,path in {'room':'databases/pocket_node.db','nativeTestnet':'files/data/testnet/store.db',
                      'nativeMainnet':'files/data/mainnet/store.db','preferences':'shared_prefs/ckb_wallet_prefs.xml',
                      'keyBackups':'files/key_backups','restoreJournal':'files/h02-restore-journal.json'}.items():
        d.sandbox('test','!','-e',path);checks[name+'Absent']=True
    after=security(d)
    p.require(not after['pocket_node_key_material']['present'] and not after['pocket_node_key_material_v2']['present'],
              'old-pocket-keystore-key-survived-clear')
    result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':role,'result':'PASS',
            'phoneSerial':d.serial,'resetScope':APP+' user 0 only','oldSecurityMetadata':old_security,
            'freshSecurityMetadata':after,'checks':checks,'PocketRunning':False,'H2Activated':False,
            'unrelatedDataTouched':False,'factoryReset':False}
    save(output,result);event(role,'fresh_empty_sandbox_and_keystore_verified')
    print('FRESH_POCKET_STATE_PASS; wallet/Room/native/preferences/key-backups/journal/Keystore absent')

def capture(role,label):
    out=BASE/role/label
    p.require(not out.exists(),'observation-exists')
    out.mkdir(parents=True)
    d=device();keymeta=security(d)
    d.freeze();d.deploy()
    remote=REMOTE_ROOT+'/files/h02-inspect-'+uuid.uuid4().hex[:16]
    d.helper('observe',remote)
    for name in ('app.json','native.sqlite','public.json'):
        raw=d.get(remote+'/'+name)
        if name!='native.sqlite':p.secret_gate(raw)
        (out/name).write_bytes(raw)
    app=p.read_json(out/'app.json');scripts=p.validate_app(app,destination=True)
    wallets=sorted(app['wallets'],key=lambda w:w['accountIndex'])
    accounts=[]
    expected={0:'bc5882c4309431ee23ad7bbad4b5c3325539eebd',1:'2da024570462b0e2421d87abcbfebd4567d52ad5'}
    for w in wallets:
        args=scripts[w['walletId']][-40:]
        p.require(args==expected[w['accountIndex']],'owned-script-identity')
        item=native(out/'native.sqlite',args);item['wallet']=w
        p.require(scripts[w['walletId']]+':0' in item['registrations'],'missing-owned-registration')
        accounts.append(item)
    n={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accounts':accounts,'wallets':wallets,
       'progress':app['progress'],'prefs':app['prefs'],'room':p.read_json(out/'public.json'),
       'discoveryCandidateCount':len(app['candidates']),
       'discoveryStates':{state:sum(c['state']==state for c in app['candidates']) for state in set(c['state'] for c in app['candidates'])}}
    save(out/'summary.json',n);save(out/'security.json',keymeta)
    event(role,'frozen_public_observation_saved',label=label)
    print('PHONE_PUBLIC_CAPTURE_COMPLETE; Pocket remains disabled')
    return out

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['reset','capture','security'])
    parser.add_argument('role',choices=['control','candidate']);parser.add_argument('--label')
    args=parser.parse_args()
    try:
        if args.action=='reset':reset(args.role)
        elif args.action=='capture':capture(args.role,args.label)
        else:save(BASE/args.role/(args.label+'.json'),security(device()));print('PUBLIC_KEYSTORE_METADATA_SAVED')
    except Exception as e:
        print('PHONE_STATE_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''))
        raise SystemExit(2)
