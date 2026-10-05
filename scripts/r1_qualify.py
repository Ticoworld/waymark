"""WO-3B1-R1 emulator diagnostics only. No secret access, wallet recovery or signing.
Every device command targets emulator-5580. Outputs live under runs/wo3b1-r1.
Actions are staged: Android qualification precedes any separate Pocket launch.
"""
import argparse,ctypes,datetime,hashlib,json,os,re,shlex,subprocess,time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'runs/wo3b1-r1'
SDK=Path(os.environ['LOCALAPPDATA'])/'Android/Sdk'
ADB=str(SDK/'platform-tools/adb.exe')
SERIAL='emulator-5580';APP='com.rjnr.pocketnode'
APK_SHA='903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f'

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def call(*args,timeout=30,check=True):
    p=subprocess.run([ADB,'-s',SERIAL,*args],capture_output=True,timeout=timeout)
    if check and p.returncode:raise RuntimeError('ADB command failed: '+args[0])
    text=p.stdout.decode('utf-8',errors='replace')
    if not check and p.returncode:text+='\n[command exit '+str(p.returncode)+']\n'+p.stderr.decode('utf-8',errors='replace')
    return text
def shell(*args,timeout=30,check=True):return call('shell','-T',shlex.join(args),timeout=timeout,check=check)
def processpid(name,timeout=12):
    value=shell('pidof',name,timeout=timeout,check=False).strip()
    if not value or value=='[command exit 1]':return ''
    if not re.fullmatch(r'\d+(?:\s+\d+)*',value):raise RuntimeError('PID query failed')
    return value
def guard():
    if shell('getprop','ro.kernel.qemu').strip()!='1':raise RuntimeError('not emulator')
    if not call('emu','avd','name').splitlines()[0].startswith('H02_'):raise RuntimeError('wrong AVD')
def outdir(name):
    if not re.fullmatch('[a-zA-Z0-9_-]+',name):raise ValueError()
    p=BASE/name;p.mkdir(parents=True,exist_ok=True);return p
def save(folder,name,data):
    f=folder/name
    # Every observation gets a unique path; never overwrite an earlier capture.
    with f.open('x',encoding='utf-8') as stream:
        stream.write(data if isinstance(data,str) else json.dumps(data,indent=2))
def hostmemory():
    class MEMORY(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in ['total','avail','page','apage','virt','avirt','extended']]
    m=MEMORY();m.length=ctypes.sizeof(m);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return {'loadPercent':m.load,'totalMiB':m.total//2**20,'availableMiB':m.avail//2**20,'commitAvailableMiB':m.apage//2**20}

def bootwatch(folder):
    t=time.monotonic();seen=False;log=None
    try:
        while time.monotonic()-t<660:
            try:
                boot=shell('getprop','sys.boot_completed',timeout=12).strip()
                if not seen:
                    guard();seen=True
                    stream=(folder/'boot-logcat.txt').open('xb')
                    log=subprocess.Popen([ADB,'-s',SERIAL,'logcat','-b','all','-v','threadtime'],stdout=stream,stderr=subprocess.DEVNULL)
                    stream.close()
                pid=processpid('system_server')
                row={'utc':utc(),'elapsed':round(time.monotonic()-t,2),'boot':boot,'system_server':pid,'host':hostmemory()}
            except (RuntimeError,subprocess.TimeoutExpired):row={'utc':utc(),'elapsed':round(time.monotonic()-t,2),'boot':'unavailable','host':hostmemory()}
            with (folder/'boot-observations.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            print(json.dumps(row),flush=True)
            if row['boot']=='1':
                save(folder,'boot-complete.json',row);return
            time.sleep(10)
        raise RuntimeError('boot did not finish within bound')
    finally:
        if log:log.terminate();log.wait(timeout=10)

def ui(folder,label):
    path='/data/local/tmp/h02-r1-ui.xml'
    shell('uiautomator','dump',path,timeout=35)
    raw=shell('cat',path);shell('rm','-f',path)
    root=ET.fromstring(raw);nodes=list(root.iter('node'))
    # No recovery input is allowed in R1. Refuse to emit editable contents anyway.
    if any(n.attrib.get('class')=='android.widget.EditText' and n.attrib.get('text','').strip() for n in nodes):raise RuntimeError('nonempty edit field; no diagnostic dump allowed')
    arr=[{k:n.attrib.get(k,'') for k in ['text','content-desc','resource-id','class','bounds','clickable']} for n in nodes if any(n.attrib.get(k) for k in ['text','content-desc','resource-id'])]
    save(folder,label+'-ui.json',arr)
    titles=[n['text'] or n['content-desc'] for n in arr if n['text'] or n['content-desc']]
    print(json.dumps({'ui':label,'labels':titles}),flush=True)
    if any("isn't responding" in s for s in titles):raise RuntimeError('ANR dialog')
    return nodes

def capture(folder,label):
    commands={
      'crash':('logcat','-d','-b','crash'),
      'events':('logcat','-d','-b','events'),
      'logcat':('logcat','-d','-b','main','-b','system'),
    }
    for name,args in commands.items():save(folder,label+'-'+name+'.txt',call(*args,timeout=45,check=False))
    for name,args in {
      'lastanr':('dumpsys','activity','lastanr'), 'meminfo':('cat','/proc/meminfo'),
      'pressure-memory':('cat','/proc/pressure/memory'),
      'pressure-cpu':('cat','/proc/pressure/cpu'),
      'pressure-io':('cat','/proc/pressure/io'),
      'cpu':('dumpsys','cpuinfo'), 'exitinfo':('dumpsys','activity','exit-info',APP),
      'disk':('df','-k','/data'), 'processes':('ps','-A','-o','PID,NAME'),
      'tombstones':('ls','-l','/data/tombstones'), 'dropbox':('dumpsys','dropbox'),
      'kernel':('dmesg',),
    }.items():
        try:save(folder,label+'-'+name+'.txt',shell(*args,timeout=35,check=False))
        except subprocess.TimeoutExpired:save(folder,label+'-'+name+'.txt','TIMEOUT')
    save(folder,label+'-host.json',{'utc':utc(),'memory':hostmemory()})

def interact(folder,label):
    shell('input','keyevent','KEYCODE_WAKEUP');shell('input','keyevent','KEYCODE_HOME');time.sleep(2)
    ui(folder,label+'-launcher-before')
    launch=shell('am','start','-W','-a','android.settings.SETTINGS',timeout=45)
    save(folder,label+'-settings-launch.txt',launch);time.sleep(2)
    nodes=ui(folder,label+'-settings')
    if not any(n.attrib.get('package')=='com.android.settings' for n in nodes):raise RuntimeError('Settings not visible')
    shell('input','keyevent','KEYCODE_BACK');shell('input','keyevent','KEYCODE_HOME');time.sleep(2)
    nodes=ui(folder,label+'-launcher-after')
    if not any(n.attrib.get('package')=='com.android.launcher3' for n in nodes):raise RuntimeError('launcher not visible')

def observe(folder,label,seconds):
    guard();start=time.monotonic();rows=[]
    while True:
        row={'utc':utc(),'elapsed':round(time.monotonic()-start,2),
             'system_server':processpid('system_server'),
             'pocketPid':processpid(APP),
             'host':hostmemory()}
        rows.append(row);print(json.dumps(row),flush=True)
        if row['elapsed']>=seconds:break
        time.sleep(min(20,seconds-row['elapsed']))
    save(folder,label+'-observations.json',rows)
    capture(folder,label)
    if len({r['system_server'] for r in rows})!=1 or not rows[0]['system_server']:raise RuntimeError('system_server restarted')

def pocket(folder,label):
    guard();info=shell('dumpsys','package',APP)
    if 'versionName=1.8.5' not in info or 'versionCode=27' not in info or 'DEBUGGABLE' not in info:raise RuntimeError('wrong APK')
    path=shell('pm','path',APP).strip().removeprefix('package:')
    if shell('sha256sum',path).split()[0]!=APK_SHA:raise RuntimeError('APK digest mismatch')
    shell('pm','enable','--user','0',APP)
    launch=shell('am','start','-W','-n',APP+'/.MainActivity',timeout=60)
    save(folder,label+'-launch.txt',launch);time.sleep(4);ui(folder,label+'-start')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['bootwatch','interact','observe','capture','pocket','ui']);p.add_argument('--run',required=True);p.add_argument('--label',default='sample');p.add_argument('--seconds',type=int,default=180);a=p.parse_args();folder=outdir(a.run)
    if a.action=='bootwatch':bootwatch(folder)
    else:
        guard()
        if a.action=='observe':observe(folder,a.label,a.seconds)
        else:globals()[a.action](folder,a.label)

if __name__=='__main__':
    try:main()
    except Exception as e:print('R1_CHECK_FAILED '+type(e).__name__+': '+str(e));raise SystemExit(2)
