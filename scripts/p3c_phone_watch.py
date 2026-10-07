"""Bounded read-only per-Script/Room watch; fixed public fields only."""
import argparse
import datetime
import json
import time
from p3c_phone_ui import BASE
from p3c_r1_probe import probe
import h02_package as p

def convergence():
    from p3c_phone_ui import device
    local=BASE/'progress-helper/helper.jar'
    d=device();remote='/data/local/tmp/h02-phone-ab-readonly.jar'
    d.call('push',str(local),remote);d.shell('chmod','444',remote)
    p.require(d.shell('sha256sum',remote).decode().split()[0]==p.sha(local),'progress-helper-digest')
    raw=d.sandbox('env','CLASSPATH='+remote,'/system/bin/app_process','/system/bin','h02.H02PhoneABReadOnly')
    rows=[x.split(b'=',1)[1] for x in raw.splitlines() if x.startswith(b'H02_PHONE_AB_PUBLIC_JSON=')]
    p.require(len(rows)==1,'public-convergence-projection-refused')
    result=json.loads(rows[0]);result['minFiltered']=int.from_bytes(bytes.fromhex(result.pop('minimumFilteredLittleEndianHex')),'little')
    result['helperSha256']=p.sha(local);return result

def row():
    app=probe('app')
    regs=app.get('nativeRegistrations',[])
    owned=[]
    for args in ('bc5882c4309431ee23ad7bbad4b5c3325539eebd','2da024570462b0e2421d87abcbfebd4567d52ad5'):
        matches=[r for r in regs if r['keyHex'].lower().endswith(args+'00')]
        owned.append(int(matches[0]['valueHex'],16) if len(matches)==1 else None)
    return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'accountCount':len(app['wallets']),
        'convergence':convergence(),
        'ownedScriptProgress':owned,'registrationCount':len(regs),
        'minimumRegistrationProgress':min((int(r['valueHex'],16) for r in regs),default=None),
        'RoomProgress':[r for r in app['progress'] if r['network']=='TESTNET'],
        'balances':[{'walletId':r['walletId'],'capacity':r['capacity'],'blockNumber':r['blockNumber']} for r in app['balances'] if r['network']=='TESTNET'],
        'daoCount':len(app['dao']),'dao':[{'txHash':r['txHash'],'index':r['index'],'walletId':r['walletId'],'status':r['status']} for r in app['dao']],
        'keyMetadata':app['keyMetadata']}

def watch(role,label,seconds,minimum):
    path=BASE/role/(label+'.jsonl');p.require(not path.exists(),'watch-exists')
    end=time.monotonic()+seconds;settled=0
    while True:
        sample=row()
        with path.open('ab') as f:f.write(p.encode(sample)+b'\n')
        print(json.dumps(sample),flush=True)
        c=sample['convergence']
        ready=(c['minFiltered']>=minimum and c['matchedWorkRows']==0 and not any(c['discoveryStates'].get(s,0) for s in ('PENDING','FOUND')) and sample['accountCount']==2 and sample['daoCount']==1 and all(x is not None and x>=minimum for x in sample['ownedScriptProgress']) and
               sample['minimumRegistrationProgress'] is not None and sample['minimumRegistrationProgress']>=minimum and
               len(sample['RoomProgress'])==2 and all(r['localSavedBlockNumber']>=minimum for r in sample['RoomProgress']))
        settled=settled+1 if ready else 0
        if settled>=2:print('PHONE_WATCH_READY_FOR_EXACT_CANONICAL_GATE',flush=True);return
        if time.monotonic()>=end:print('PHONE_WATCH_NOT_YET_SETTLED',flush=True);return
        time.sleep(min(20,max(0,end-time.monotonic())))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('role',choices=['control','candidate']);parser.add_argument('label')
    parser.add_argument('--seconds',type=int,default=600);parser.add_argument('--minimum',type=int,required=True)
    args=parser.parse_args()
    try:watch(args.role,args.label,args.seconds,args.minimum)
    except Exception as e:
        print('PHONE_WATCH_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''))
        raise SystemExit(2)
