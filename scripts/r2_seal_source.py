"""Stop and seal SOURCE once; never read it after the loss declaration."""
import datetime,json,stat,subprocess,time
from pathlib import Path
import h02_device as d
import h02_package as p
from r2_observe import APK,GENESIS,SCRIPT

root=d.ROOT/'runs/wo3b1-r2'
marker=root/'source/LOST.json'
p.require(not marker.exists(),'already-lost')
receipt=p.read_json(root/'source/package-receipt.json')
p.validate(root/'package-H-immutable',receipt['manifestSha256'],APK,GENESIS)
o=p.read_json(root/'oracle-F.json')
tx='0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7'
u={'tx_hash':'0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894','index':'0x0'}
t=o['transactionDetails'][tx]
p.require(t['tx_status']['status']=='committed' and int(t['tx_status']['block_number'],16)>receipt['H'],'post-H-confirmation')
p.require([i['previous_output'] for i in t['transaction']['inputs']]==[u],'one-U-input')
p.require(all(c['lock']==SCRIPT for c in t['transaction']['outputs']),'owned-replacement')
p.require(o['spentU']['outPoint']==u and o['spentU']['result']['status']!='live','U-still-live')
p.require(len(o['liveCells'])==4 and o['capacity']==1999999998000,'final-oracle')
avd=d.ROOT/'runs/wo2/avd/H02_P0_API36_X64.avd'
device=d.Device('emulator-5580',APK);device.freeze();device.call('emu','kill')
query="Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'qemu-system*' -or $_.Name -eq 'emulator.exe' } | Select-Object -ExpandProperty CommandLine"
for _ in range(30):
    raw=subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,check=True).stdout
    if 'H02_P0_API36_X64' not in raw:break
    time.sleep(1)
else:raise p.Refused('source-process-still-running')
files={}
for path in sorted(avd.rglob('*')):
    if path.is_file():
        files[str(path.relative_to(avd))]={'bytes':path.stat().st_size,'sha256':p.sha(path)}
        path.chmod(stat.S_IREAD)
preloss={str(f.relative_to(root)):{'bytes':f.stat().st_size,'sha256':p.sha(f)} for f in sorted((root/'source').rglob('*')) if f.is_file()}
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceStopped':True,'sourceAvd':'runs/wo2/avd/H02_P0_API36_X64.avd','seal':'SHA256 inventory and read-only files; no later source reads permitted','sourceFiles':files,'publicEvidenceFiles':preloss,'packageManifest':receipt['manifestSha256'],'F':int(o['tip']['number'],16),'FHash':o['tip']['hash'],'U':u,'postHTx':tx,'confirmationHeight':int(t['tx_status']['block_number'],16),'allowedInputsAfterLoss':['private fixture','immutable package','previously recorded public oracle','public chain observations']}
with marker.open('xb') as f:f.write(p.encode(result))
marker.chmod(stat.S_IREAD)
print(json.dumps({k:v for k,v in result.items() if k not in ('sourceFiles','publicEvidenceFiles')},indent=2))
