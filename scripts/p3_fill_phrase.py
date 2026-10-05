"""Future emulator-only UI phrase entry. Fills normal Pocket fields; never submits.
Call only when normal v1.8.5 recovery screen is ready. Not run in WO-3 setup.
No phrase in argv, shell history, clipboard, screenshots or retained transport logs.
"""
import argparse, base64, hashlib, json, uuid
from h02_device import Device, ROOT, REMOTE_ROOT
from p3_fixture import FIXTURE, verify

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--serial',required=True);p.add_argument('--apk-sha256',required=True);a=p.parse_args()
    # Exact AVD/API/ABI/app-version/APK checks, including physical-device refusal.
    d=Device(a.serial,a.apk_sha256)
    fixture=json.loads(FIXTURE.read_text(encoding='utf-8'));verify(fixture)
    words=fixture['wallets'][0]['mnemonic']
    if len(words.split())!=12:raise ValueError()
    jar=ROOT/'runs/wo3-setup/ui-helper/helper.jar'
    remotejar='/data/local/tmp/h02-fill-'+uuid.uuid4().hex[:16]+'.jar'
    d.call('push',str(jar),remotejar)
    if d.shell('sha256sum',remotejar).decode().split()[0]!=hashlib.sha256(jar.read_bytes()).hexdigest():raise ValueError()
    path=REMOTE_ROOT+'/files/h02-phrase-'+uuid.uuid4().hex[:16]+'.json'
    try:
        d.put(path,json.dumps({'mnemonic':words}).encode())
        d.sandbox('chmod','600',path)
        raw=d.shell('uiautomator','runtest',remotejar,'-c','h02.H02FillPhrase','-e','fixture',path)
        if b'H02_PHRASE_FIELDS_FILLED; NOT_SUBMITTED' not in raw or b'FAILURES' in raw:raise ValueError()
        print('PHRASE_FILLED_NOT_SUBMITTED; no recovery claim')
    finally:
        # Exact generated paths only. No recursive deletion or wildcard cleanup.
        d.sandbox('rm','-f',path)
        d.shell('rm','-f',remotejar)

if __name__=='__main__':
    try:main()
    except Exception:
        print('PHRASE_ENTRY_REFUSED; UI may contain partial private input; do not capture it');raise SystemExit(2)
