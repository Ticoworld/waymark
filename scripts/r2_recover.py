"""Timed normal Pocket recovery on an already provisioned fresh emulator arm.
No app DB/key injection. Stop on any UI refusal; no hierarchy reads during phrase input.
"""
import argparse,subprocess,time
from h02_device import Device,ROOT,APP
from r2_public_tap import tap,APK
from r2_pin import main as pin
from r2_events import mark

def run(role):
    if role not in ('control','candidate'):raise ValueError()
    # Operator must separately verify this role's launch registry and pristine install.
    launch=ROOT/'runs/wo3b1-r2'/role/'boot/launch.json'
    import json
    if json.loads(launch.read_text(encoding='utf-8-sig'))['role']!=role:raise ValueError()
    d=Device('emulator-5580',APK)
    # No existing key database means no accidental rerun over recovered state.
    probe=d.sandbox('sh','-c','test ! -e databases/pocket_node.db && echo PRISTINE')
    if probe.strip()!=b'PRISTINE':raise ValueError()
    if (ROOT/'runs/wo3b1-r2'/role/'events.jsonl').exists():raise ValueError()
    mark(role,'first_launch_begin');d.shell('am','start','-n',APP+'/.MainActivity');time.sleep(5)
    tap(public_id='onboarding-recover');tap(public_id='onboarding-no-lock-continue')
    command=[str(ROOT/'runs/wo3-setup/venv/Scripts/python.exe'),str(ROOT/'scripts/p3_fill_phrase.py'),'--serial','emulator-5580','--apk-sha256',APK,'--helper','runs/wo3b1-r2/ui-helper-actions/helper.jar']
    subprocess.run(command,check=True,cwd=ROOT)
    tap(public_id='import-submit');tap(public_id='sync-sheet-apply')
    tap(public_id='pin-intro-continue');pin();time.sleep(1);pin();time.sleep(8)
    tap(public_id='bg-sync-optin-skip');mark(role,'normal_keys_and_security_complete')
    time.sleep(3)
    # Only now, after phrase/PIN forms have closed, inspect public Settings nodes.
    from p3b1_ui import nodes
    if any(n.attrib.get('text')=='Got it' for n in nodes(d)):tap(public_text='Got it')
    tap(public_text='Settings')
    for _ in range(5):
        if any(n.attrib.get('text')=='Current Network' for n in nodes(d)):break
        d.shell('input','swipe','540','1830','540','720','500');time.sleep(1)
    else:raise ValueError()
    tap(public_text='Current Network');tap(public_text='Switch & Restart');time.sleep(6)
    tap(public_id='auth-use-pin');pin();time.sleep(8)
    # Current screen after restart is Home. Dismiss only the known public tooltip.
    if any(n.attrib.get('text')=='Got it' for n in nodes(d)):tap(public_text='Got it')
    tap(public_text='Settings');tap(public_text='Sync Options');tap(public_text='From a specific date');tap(public_text='Block Height')
    d.shell('input','text','22369937');d.shell('input','keyevent','4');tap(public_id='sync-sheet-apply')
    mark(role,'testnet_custom_registration_requested');tap(public_text='Wallet')
    print('NORMAL_RECOVERY_UI_COMPLETE; public/native identity still requires independent acceptance')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('role',choices=['control','candidate']);a=parser.parse_args()
    try:run(a.role)
    except Exception as e:print('NORMAL_RECOVERY_AUTOMATION_REFUSED '+type(e).__name__+'; inspect safe state; no recovery conclusion');raise SystemExit(2)
