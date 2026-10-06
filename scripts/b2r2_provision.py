"""Provision a fresh isolated arm without launching Pocket or starting its timer."""
import argparse,datetime,json,subprocess,time
import h02_package as p
from h02_device import ROOT,Device,APP
from r2_observe import APK
from r1_qualify import shell,call,hostmemory

def run(role,attempt="boot"):
    import re
    if not re.fullmatch(r"boot(?:-[a-z0-9]+)?",attempt):raise ValueError()
    out=ROOT/'runs/wo3b2'/role/attempt
    p.require(not (out/'provision.json').exists(),'already-provisioned')
    command="Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'qemu-system*' } | Select-Object -ExpandProperty CommandLine"
    raw=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True).stdout.replace('\\','/').lower()
    p.require(str((out.parent/'avd').resolve()).replace('\\','/').lower() in raw and '-gpu host' in raw,'wrong-live-role')
    started=time.monotonic()
    while time.monotonic()-started<300:
        try:ready=shell('getprop','sys.boot_completed',timeout=10).strip()=='1'
        except Exception:ready=False
        if ready:break
        print('Waiting for isolated '+role+' Android boot',flush=True);time.sleep(10)
    else:raise p.Refused('boot-timeout')
    p.require(shell('getprop','ro.build.version.sdk').strip()=='36','api')
    p.require(shell('getprop','ro.product.cpu.abi').strip()=='x86_64','abi')
    shell('input','keyevent','KEYCODE_WAKEUP');shell('input','keyevent','KEYCODE_HOME')
    before=shell('pidof','system_server').strip()
    settings=shell('am','start','-W','-a','android.settings.SETTINGS')
    p.require('Status: ok' in settings,'settings-start')
    time.sleep(3)
    p.require('com.android.settings' in shell('dumpsys','activity','activities'),'settings-response')
    shell('input','keyevent','KEYCODE_BACK');shell('input','keyevent','KEYCODE_HOME')
    time.sleep(3)
    p.require('com.android.launcher3' in shell('dumpsys','activity','activities'),'launcher-response')
    p.require(before==shell('pidof','system_server').strip(),'system-restart')
    events=call('logcat','-d','-b','events')
    anrs=[x for x in events.splitlines() if 'am_anr' in x or 'am_crash' in x]
    if anrs:
        qualification=json.loads((out/'pre-pocket/stability.json').read_text())
        p.require(qualification['PASS'] is True and qualification['priorBootAnrs']==anrs and qualification['observations'][-1]['elapsed']>=180,'unresolved-android-instability')
        p.require(all(x['newAnrsOrCrashes']==0 and x['systemServerUnchanged'] for x in qualification['observations']),'instability-after-boot-settled')

    apk=ROOT/'runs/wo2/gradle/app/outputs/apk/debug/app-debug.apk'
    p.require(p.sha(apk)==APK,'host-apk-digest')
    p.require(not shell('pm','path',APP,check=False).startswith('package:'),'not-fresh-install')
    p.require('Success' in call('install',str(apk),timeout=180),'apk-install')
    device=Device('emulator-5580',APK);device.stopped()
    p.require(device.sandbox('sh','-c','test ! -e databases/pocket_node.db && test ! -e files/data/testnet/store.db && test ! -e shared_prefs/ckb_wallet_prefs.xml && test ! -e files/key_backups && echo PRISTINE').strip()==b'PRISTINE','not-pristine')
    result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':role,'apkSha256':APK,'api':36,'abi':'x86_64','graphics':'host','androidResponsive':True,'priorBootAnrCount':len(anrs),'settledAndroidQualification':bool(anrs),'freshInstallation':True,'pocketLaunched':False,'emptySandboxChecks':['Room database absent','native TESTNET store absent','Pocket preferences absent','key_backups absent'],'guestBootId':shell('cat','/proc/sys/kernel/random/boot_id').strip(),'systemServerPid':before,'host':hostmemory()}
    with (out/'provision.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('role',choices=['source','control','candidate']);parser.add_argument('--attempt',default='boot');a=parser.parse_args()
    try:run(a.role,a.attempt)
    except Exception as e:print('PROVISION_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''));raise SystemExit(2)
