"""Candidate-only timed invocation of existing validated stage/activate tooling.
Normal key recovery must already have completed. Never consults SOURCE state.
"""
import argparse,json,time
from pathlib import Path
from types import SimpleNamespace
import h02_device as d
import h02_package as p
from r2_observe import APK,GENESIS
from b2_events import mark
from r2_public_tap import tap
from r2_pin import main as pin

def run(package,trust):
    root=d.ROOT/'runs/wo3b2';role='candidate'
    p.require((root/'source/LOST.json').is_file(),'source-not-declared-lost')
    launch=json.loads((root/role/'boot/launch.json').read_text(encoding='utf-8-sig'))
    p.require(launch['role']==role,'wrong-role-record')
    device=d.Device('emulator-5580',APK)
    # Candidate must be the currently running emulator process's own registry.
    # A read-only host process query verifies it without contacting SOURCE.
    import subprocess
    command="(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'qemu-system*' } | Select-Object -ExpandProperty CommandLine)"
    raw=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True).stdout
    # QEMU argv can resolve paths with either slash convention.
    expected=str((root/role/'avd').resolve()).replace('\\','/').lower()
    p.require(expected in raw.replace('\\','/').lower(),'running-role-registry-not-candidate')
    a=SimpleNamespace(package=str(package),trust=trust,apk_sha256=APK,genesis=GENESIS,serial='emulator-5580')
    d.HELPER=d.ROOT/'runs/wo3b2-r2/state-helper/helper.jar'
    event=lambda name:mark(role,name)
    event('package_restore_begin');token=d.stage(a,event)
    a.token=token;a.action='commit';event('activation_begin');d.activate(a);event('activation_complete')
    manifest=p.read_json(Path(package)/'manifest.json')
    digest=device.sandbox('sha256sum',d.REMOTE_ROOT+'/files/data/testnet/store.db').decode().split()[0]
    p.require(digest==manifest['files']['native.sqlite']['sha256'],'activated-native-digest-mismatch')
    receipt={'packageManifest':trust,'activatedNativeDigest':digest,'stageToken':token,'normalDestinationKeysPreservedByHelper':True}
    with (root/role/'activation-receipt.json').open('x') as f:json.dump(receipt,f,indent=2)
    d.enable(a);event('package_restore_complete');event('light_client_launch_requested')
    device.shell('am','start','-n',d.APP+'/.MainActivity');time.sleep(5)
    tap(public_id='auth-use-pin');pin();event('restored_app_unlocked')
    print('CANDIDATE_ACTIVATED_AND_LAUNCHED; catch-up/acceptance not yet claimed')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('package',type=Path);a.add_argument('--trust',required=True);v=a.parse_args()
    try:run(v.package,v.trust)
    except Exception as e:print('CANDIDATE_RESTORE_REFUSED '+type(e).__name__);raise SystemExit(2)
