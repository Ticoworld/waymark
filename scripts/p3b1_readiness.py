"""Nonsecret, bounded read-only readiness checks on the designated emulator."""
import concurrent.futures,datetime,json,os,subprocess
from pathlib import Path
adb=str(Path(os.environ['LOCALAPPDATA'])/'Android/Sdk/platform-tools/adb.exe')
checks={'avd':['emu','avd','name'],'boot':['shell','getprop','sys.boot_completed'],
        'bootanim':['shell','getprop','init.svc.bootanim'],'activity':['shell','service','check','activity'],
        'package':['shell','pm','path','com.rjnr.pocketnode'],'qemu':['shell','getprop','ro.kernel.qemu']}
def run(item):
    name,args=item
    try:
        p=subprocess.run([adb,'-s','emulator-5580']+args,capture_output=True,timeout=20)
        return name,{'exit':p.returncode,'output':p.stdout.decode(errors='replace').strip()[:500]}
    except subprocess.TimeoutExpired:return name,{'timeout':True}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    result=dict(pool.map(run,checks.items()))
result['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
print(json.dumps(result,indent=2))
