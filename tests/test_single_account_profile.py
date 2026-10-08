"""Single-account policy tests. Synthetic secrets are nonsigning canaries."""
import copy,sqlite3,unittest,uuid
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import state_package as p
from test_state_package import app_fixture,native_fixture,APK,GENESIS,ROOT

def one():
    a=app_fixture();removed=a['wallets'].pop()['walletId'];a['progress'].pop()
    a['prefs']={k:v for k,v in a['prefs'].items() if not k.startswith(removed)}
    # Normal Pocket import creates discovery rows. They are not added wallets.
    return a

class SingleAccountProfile(unittest.TestCase):
    def test_one_wallet_accepted(self):self.assertEqual(len(p.validate_app(one(),profile=p.SINGLE_ACCOUNT_FORMAT)),1)
    def test_two_account_profile_requires_two(self):
        with self.assertRaises(p.Refused):p.validate_app(one())
    def test_single_account_refuses_two_wallets(self):
        with self.assertRaises(p.Refused):p.validate_app(app_fixture(),profile=p.SINGLE_ACCOUNT_FORMAT)
    def test_single_account_refuses_populated_discovery(self):
        a=one();a['candidates'][0]['state']='FOUND'
        with self.assertRaises(p.Refused):p.validate_app(a,profile=p.SINGLE_ACCOUNT_FORMAT)
    def test_secret_projection_refused(self):
        a=one();a['wallets'][0]['key_material']='WALLET_STATE_TEST_SECRET'
        with self.assertRaises(p.Refused):p.validate_app(a,profile=p.SINGLE_ACCOUNT_FORMAT)
    def test_state_package_manifest(self):
        a=one();d=ROOT/'runs/synthetic-single-account'/uuid.uuid4().hex;d.mkdir(parents=True)
        (d/'app.json').write_bytes(p.encode(a));native_fixture(d/'native.sqlite',a,p.SINGLE_ACCOUNT_FORMAT)
        digest=p.seal(d,APK,GENESIS,100,'ef'*32,{a['wallets'][0]['walletId']:10},'synthetic',p.SINGLE_ACCOUNT_FORMAT)
        self.assertEqual(p.validate(d,digest,APK,GENESIS,True)[0]['format'],p.SINGLE_ACCOUNT_FORMAT)
        with self.assertRaises(p.Refused):p.restore_plan(d,digest,APK,GENESIS,one())

if __name__=='__main__':unittest.main(verbosity=2)
