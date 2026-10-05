"""Click a public Pocket selector without dumping a secret-bearing screen.
Do not pass PINs, phrases or other private values as selectors.
"""
import argparse,hashlib,uuid,re,base64
from pathlib import Path
from h02_device import Device,ROOT

APK='903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f'
JAR=ROOT/'runs/wo3b1-r2/ui-helper-actions/helper.jar'

def tap(public_id=None,public_text=None,state=False):
    d=Device('emulator-5580',APK)
    remote='/data/local/tmp/h02-public-tap-'+uuid.uuid4().hex[:16]+'.jar'
    try:
        d.call('push',str(JAR),remote)
        if d.shell('sha256sum',remote).decode().split()[0]!=hashlib.sha256(JAR.read_bytes()).hexdigest():raise ValueError()
        args=['uiautomator','runtest',remote,'/system/framework/android.test.base.jar','-c','h02.H02FillPhrase#'+('testPublicState' if state else 'testPublicTap')]
        if not state:args+=['-e','publicId',public_id] if public_id else ['-e','publicTextB64',base64.b64encode(public_text.encode()).decode()]
        raw=d.shell(*args)
        if state:
            print('\n'.join(x.decode() for x in re.findall(rb'H02_(?:PUBLIC_STATE_\d+|IMPORT_ENABLED|IMPORT_DISABLED)',raw)))
        if (b'H02_PUBLIC_STATE_OK' if state else b'H02_PUBLIC_TAP_OK') not in raw or b'FAILURES' in raw:
            print('SAFE_ACTION_STAGE='+','.join(x.decode() for x in re.findall(rb'STAGE=(foreground|exists|enabled|click)',raw)))
            raise ValueError()
        print('PUBLIC_UI_ACTION_PASS')
    finally:
        d.shell('rm','-f',remote)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--id');g.add_argument('--text');g.add_argument('--state',action='store_true');a=p.parse_args()
    try:tap(a.id,a.text,a.state)
    except Exception:print('PUBLIC_UI_ACTION_REFUSED; no raw runner output');raise SystemExit(2)
