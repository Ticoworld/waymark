"""Resume a frozen inspected B2 emulator via normal Pocket authentication."""
import time
from h02_device import Device,APP,enable
from r2_public_tap import APK,tap
from r2_pin import main as pin
from types import SimpleNamespace
def resume():
    d=Device('emulator-5580',APK)
    enable(SimpleNamespace(serial=d.serial,apk_sha256=APK))
    d.shell('am','start','-n',APP+'/.MainActivity');time.sleep(6)
    tap(public_id='auth-use-pin');pin();time.sleep(6)
    print('B2_NORMAL_RESUME_COMPLETE')
if __name__=='__main__':resume()
