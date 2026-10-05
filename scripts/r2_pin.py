"""Normal emulator Pocket PIN entry. Private local input, fixed public output only."""
import hashlib,json,secrets,uuid
from h02_device import Device,ROOT,REMOTE_ROOT
from r2_public_tap import APK,JAR

def main():
    d=Device('emulator-5580',APK)
    stored=ROOT/'private/wo3b1-r2/emulator-security.json'
    stored.parent.mkdir(exist_ok=True)
    if not stored.exists():
        with stored.open('x',encoding='utf-8') as f:json.dump({'purpose':'H02 emulator-only disposable PIN; never physical phone','pin':str(100000+secrets.randbelow(900000))},f)
    secret=json.loads(stored.read_text(encoding='utf-8'))['pin']
    path=REMOTE_ROOT+'/files/h02-pin-'+uuid.uuid4().hex[:16]+'.json'
    jar='/data/local/tmp/h02-pin-ui-'+uuid.uuid4().hex[:16]+'.jar'
    try:
        d.call('push',str(JAR),jar)
        if d.shell('sha256sum',jar).decode().split()[0]!=hashlib.sha256(JAR.read_bytes()).hexdigest():raise ValueError()
        d.put(path,json.dumps({'pin':secret}).encode());d.sandbox('chmod','600',path)
        raw=d.shell('uiautomator','runtest',jar,'/system/framework/android.test.base.jar','-c','h02.H02FillPhrase#testEnterPrivatePin','-e','fixture',path)
        if b'H02_PRIVATE_PIN_ENTERED' not in raw or b'FAILURES' in raw:raise ValueError()
        print('PRIVATE_PIN_ENTERED; no value emitted')
    finally:
        d.sandbox('rm','-f',path);d.shell('rm','-f',jar)

if __name__=='__main__':
    try:main()
    except Exception:print('PRIVATE_PIN_ENTRY_REFUSED; no raw diagnostics');raise SystemExit(2)
