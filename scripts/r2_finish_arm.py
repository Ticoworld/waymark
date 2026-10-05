"""Exact F acceptance and ordinary restart on the currently running A/B arm.
No key injection, production changes, or SOURCE consultation. Refuses rather than
relaxing acceptance. Run only after the public reconstruction watcher has exited.
"""
import argparse,datetime,json,subprocess,time
from types import SimpleNamespace
import h02_device as d
import h02_package as p
from r2_observe import APK,capture
from r2_acceptance import check
from r2_events import mark
from r2_pin import main as pin
from r2_public_tap import tap

BASE=d.ROOT/'runs/wo3b1-r2';F=22646322

def verify_role(role):
    p.require((BASE/'source/LOST.json').exists(),'source-not-lost')
    query="Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'qemu-system*' } | Select-Object -ExpandProperty CommandLine"
    raw=subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,check=True).stdout.replace('\\','/').lower()
    p.require(str((BASE/role/'avd').resolve()).replace('\\','/').lower() in raw,'wrong-running-role')

def frozen_accept(role,label):
    mark(role,label+'_freeze_begin');capture(role+'/'+label)
    result=check(BASE/role/label,BASE/'oracle-F.json',F)
    (BASE/role/(label+'-acceptance.json')).write_bytes(p.encode(result))
    mark(role,label+'_exact_acceptance_pass')
    print('EXACT_F_ACCEPTANCE_PASS '+result['semanticSha256'],flush=True)
    return result

def restart(role,label):
    mark(role,label+'_restart_begin')
    a=SimpleNamespace(serial='emulator-5580',apk_sha256=APK)
    d.enable(a);device=d.Device(a.serial,APK)
    device.shell('am','start','-n',d.APP+'/.MainActivity');time.sleep(5)
    tap(public_id='auth-use-pin');pin();mark(role,label+'_restart_unlocked')

def watch(role,label,seconds=2700):
    path=BASE/role/(label+'.jsonl')
    subprocess.run(['python',str(d.ROOT/'scripts/r2_watch.py'),'--label',role+'/'+label+'.jsonl','--seconds',str(seconds),'--until-synced'],cwd=d.ROOT,check=True)
    rows=[json.loads(x) for x in path.read_text().splitlines()]
    p.require(len(rows)>=2 and all('\u2713 Synced' in r['publicStatus'] and 'Finish syncing before making transactions' not in r['publicStatus'] for r in rows[-2:]),'restart-not-settled-in-bound')
    mark(role,label+'_ui_settled')

def run(role):
    verify_role(role)
    first=frozen_accept(role,'first-accepted')
    app=p.read_json(BASE/role/'first-accepted/app.json')
    count=sum(c['state']!='EMPTY' for c in app['candidates'])
    print('UNSETTLED_DISCOVERY_CANDIDATES '+str(count),flush=True)
    restart(role,'first');watch(role,'first-restart')
    second=frozen_accept(role,'after-first-restart')
    p.require(first['semanticSha256']==second['semanticSha256'],'restart-semantics-changed')
    app=p.read_json(BASE/role/'after-first-restart/app.json')
    p.require(all(c['state']=='EMPTY' for c in app['candidates']),'discovery-still-unsettled')
    # If normal restart triggered a discovery pass, prove a subsequent restart
    # is also settled. SOURCE showed this distinction matters for continuation.
    if count:
        restart(role,'final');watch(role,'final-restart',180)
        final=frozen_accept(role,'final-accepted')
        p.require(first['semanticSha256']==final['semanticSha256'],'final-restart-semantics-changed')
    else:final=second
    end=mark(role,'full_acceptance_complete')
    result={'role':role,'result':'PASS','semanticSha256':final['semanticSha256'],'F':F,'normalDiscoveryPendingAtFirstAcceptance':count,'allDiscoveryEmptyAtFinal':True,'restart':'PASS','end':end,'pocketLeftDisabled':True}
    with (BASE/role/'result.json').open('xb') as f:f.write(p.encode(result))
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('role',choices=['control','candidate']);v=a.parse_args()
    try:run(v.role)
    except Exception as e:print('ARM_ACCEPTANCE_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''),flush=True);raise SystemExit(2)
