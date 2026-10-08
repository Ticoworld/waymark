"""Synthetic policy tests: never calls adb or opens historical databases."""
import copy
import json
import sqlite3
import struct
import unittest
import uuid
from contextlib import closing
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import state_package as p

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'runs/synthetic-state-packages'
APK='ab'*32
GENESIS='cd'*32

def address(args,hrp):
    b=bytes.fromhex('00'+p.CODE_HASH+'01'+args);acc=bits=0;v=[]
    for x in b:
        acc=(acc<<8)|x;bits+=8
        while bits>=5:bits-=5;v.append((acc>>bits)&31)
    if bits:v.append((acc<<(5-bits))&31)
    mod=1
    for x in [ord(c)>>5 for c in hrp]+[0]+[ord(c)&31 for c in hrp]+v+[0]*6:
        top=mod>>25;mod=((mod&0x1ffffff)<<5)^x
        for i,g in enumerate([0x3b6a57b2,0x26508e6d,0x1ea119fa,0x3d4233dd,0x2a1462b3]):
            if (top>>i)&1:mod ^= g
    mod^=0x2bc830a3
    v += [(mod>>(5*(5-i)))&31 for i in range(6)]
    return hrp+'1'+''.join('qpzry9x8gf2tvdw0s3jn54khce6mua7l'[x] for x in v)

def app_fixture():
    ids=[str(uuid.uuid4()),str(uuid.uuid4())]
    a=dict(schema=17,identity=p.IDENTITY,wallets=[],progress=[],candidates=[],prefs={'selected_network':'TESTNET','sync_strategy':'ALL_WALLETS','active_wallet_id':ids[0]},migrationReady=True,pendingFree=True,keysPresent=True)
    for i,ident in enumerate(ids):
        arg=('%02x'%(i+1))*20
        a['wallets'].append(dict(walletId=ident,type='mnemonic',derivationPath="m/44'/309'/%d'/0/0"%i,parentWalletId=None if i==0 else ids[0],accountIndex=i,mainnetAddress=address(arg,'ckb'),testnetAddress=address(arg,'ckt')))
        a['progress'].append(dict(walletId=ident,network='TESTNET',lightStartBlockNumber=10,localSavedBlockNumber=100,updatedAt=123))
        a['prefs'][ident+'_testnet_sync_mode']='CUSTOM';a['prefs'][ident+'_testnet_custom_block_height']=10
    a['candidates']=[dict(parentWalletId=ids[0],derivationPath="m/44'/309'/2'/0/0",accountIndex=2,scriptArgs='03'*20,state='PENDING',createdAt=123,registeredFromBlock=10)]
    return a

def native_fixture(file,app,profile=p.FORMAT):
    d=sqlite3.connect(file);d.execute('CREATE TABLE kv(key BLOB PRIMARY KEY,value BLOB)')
    rows=[(b'\xe0GENESIS_BLOCK',bytes.fromhex(GENESIS)),(b'\xe0LAST_STATE',b'\0'*240),(b'\xe0LAST_N_HEADERS',b''),(b'\xe0MAX_CHECK_POINT_INDEX',b'\0'*4),(b'\xe0MIN_FILTERED_NUMBER',(100).to_bytes(8,'little')),(b'\xd0'+b'\0'*4,b'\0'*32)]
    for i,script in enumerate(p.validate_app(app,profile=profile).values()):
        rows.append((b'\xe0FILTER_SCRIPTS'+bytes.fromhex(script)+b'\0',(100).to_bytes(8,'big')))
        fake_hash=bytes([i+1])*32
        rows.extend([(b'\0'+fake_hash,b'\0'*12+struct.pack('<I',4)),(b'\x20'+bytes.fromhex(script)+b'\0'*16,fake_hash),(b'\x60'+bytes.fromhex(script)+b'\0'*17,fake_hash)])
    rows.append((b'\xa0'+bytes.fromhex(GENESIS),b'\0'*208))
    d.executemany('INSERT INTO kv VALUES (?,?)',rows);d.commit();d.close()

def fixture(kind='synthetic'):
    directory=BASE/uuid.uuid4().hex;directory.mkdir(parents=True)
    app=app_fixture();(directory/'app.json').write_bytes(p.encode(app));native_fixture(directory/'native.sqlite',app)
    digest=p.seal(directory,APK,GENESIS,100,'ef'*32,{w['walletId']:10 for w in app['wallets']},kind)
    return directory,digest,app

def resign(directory):
    m=p.read_json(directory/'manifest.json')
    for name in ('app.json','native.sqlite'):m['files'][name]={'bytes':(directory/name).stat().st_size,'sha256':p.sha(directory/name)}
    (directory/'manifest.json').write_bytes(p.encode(m));return p.sha(directory/'manifest.json')

class PackageTests(unittest.TestCase):
    def setUp(self):self.d,self.digest,self.app=fixture()
    def check(self):return p.validate(self.d,self.digest,APK,GENESIS,True)
    def refused(self):
        with self.assertRaises((p.Refused,ValueError,KeyError,TypeError,sqlite3.Error)):self.check()
    def edit_app(self,f):
        f(self.app);(self.d/'app.json').write_bytes(p.encode(self.app));self.digest=resign(self.d)
    def test_manifest_and_hashes(self):self.check()
    def test_trusted_digest_required(self):self.digest='00'*32;self.refused()
    def test_corrupt_bit(self):
        b=bytearray((self.d/'native.sqlite').read_bytes());b[-1]^=1;(self.d/'native.sqlite').write_bytes(b);self.refused()
    def test_partial_member(self):(self.d/'app.json').unlink();self.refused()
    def test_unsupported_version(self):
        m=p.read_json(self.d/'manifest.json');m['versionName']='1.8.6';(self.d/'manifest.json').write_bytes(p.encode(m));self.digest=p.sha(self.d/'manifest.json');self.refused()
    def test_wrong_network(self):
        m=p.read_json(self.d/'manifest.json');m['network']='MAINNET';(self.d/'manifest.json').write_bytes(p.encode(m));self.digest=p.sha(self.d/'manifest.json');self.refused()
    def test_wrong_native_genesis_with_valid_hashes(self):
        with closing(sqlite3.connect(self.d/'native.sqlite')) as db, db:db.execute('UPDATE kv SET value=? WHERE key=?',(b'\1'*32,b'\xe0GENESIS_BLOCK'))
        self.digest=resign(self.d);self.refused()
    def test_room_schema(self):self.edit_app(lambda a:a.update(schema=18));self.refused()
    def test_native_schema_version(self):
        with closing(sqlite3.connect(self.d/'native.sqlite')) as db, db:db.execute('PRAGMA user_version=1')
        self.digest=resign(self.d);self.refused()
    def test_native_recent_headers_shape(self):
        with closing(sqlite3.connect(self.d/'native.sqlite')) as db, db:db.execute('UPDATE kv SET value=? WHERE key=?',(b'\0',b'\xe0LAST_N_HEADERS'))
        self.digest=resign(self.d);self.refused()
    def test_native_progress_manifest(self):
        m=p.read_json(self.d/'manifest.json');m['nativeProgress']={};(self.d/'manifest.json').write_bytes(p.encode(m));self.digest=p.sha(self.d/'manifest.json');self.refused()
    def test_unsupported_abi(self):
        m=p.read_json(self.d/'manifest.json');m['abi']='arm64-v8a';(self.d/'manifest.json').write_bytes(p.encode(m));self.digest=p.sha(self.d/'manifest.json');self.refused()
    def test_apk_version(self):
        with self.assertRaises(p.Refused):p.validate(self.d,self.digest,'00'*32,GENESIS,True)
    def test_key_material_record(self):self.edit_app(lambda a:a.update(key_material=[{'encryptedPrivateKey':'WALLET_STATE_TEST_SECRET'}]));self.refused()
    def test_secret_column(self):self.edit_app(lambda a:a['wallets'][0].update(encryptedMnemonic='WALLET_STATE_TEST_SECRET'));self.refused()
    def test_pin_record(self):self.edit_app(lambda a:a['prefs'].update(pin_hash='WALLET_STATE_TEST_SECRET'));self.refused()
    def test_backup_blob(self):(self.d/'wallet.enc').write_bytes(b'PNBK\x02synthetic');self.refused()
    def test_keystore_file(self):(self.d/'test.jks').write_bytes(bytes.fromhex('feedfeed'));self.refused()
    def test_mnemonic_sequence(self):
        with self.assertRaises(p.Refused):p.secret_gate(('abandon '*11+'about').encode())
    def test_private_key_material(self):
        for b in (b'-----BEGIN PRIVATE KEY-----',b'{"privateKey":"WALLET_STATE_TEST_SECRET"}',b'WALLET_STATE_TEST_SECRET',b'PNBK\2',bytes.fromhex('feedfeed')):
            with self.assertRaises(p.Refused):p.secret_gate(b)
    def test_native_secret_payload(self):
        with closing(sqlite3.connect(self.d/'native.sqlite')) as db, db:db.execute('INSERT INTO kv VALUES(?,?)',(b'\0'+b'\5'*32,b'WALLET_STATE_TEST_SECRET'))
        self.digest=resign(self.d);self.refused()
    def test_native_key_table(self):
        with closing(sqlite3.connect(self.d/'native.sqlite')) as db, db:db.execute('CREATE TABLE key_material(secret BLOB)')
        self.digest=resign(self.d);self.refused()
    def test_no_wal_member(self):(self.d/'native.sqlite-wal').write_bytes(b'junk');self.refused()
    def test_unexpected_member(self):(self.d/'prefs.xml').write_bytes(b'<map/>');self.refused()
    def test_missing_script_progress(self):self.edit_app(lambda a:a['progress'].pop());self.refused()
    def test_missing_native_transaction_dataset(self):
        m=p.read_json(self.d/'manifest.json');m['kind']='candidate';(self.d/'manifest.json').write_bytes(p.encode(m))
        with closing(sqlite3.connect(self.d/'native.sqlite')) as db, db:db.execute('DELETE FROM kv WHERE substr(key,1,1)=?',(b'\0',))
        self.digest=resign(self.d);self.refused()
    def test_overstated_cursor(self):self.edit_app(lambda a:a['progress'][0].update(localSavedBlockNumber=101));self.refused()
    def test_mismatched_address(self):self.edit_app(lambda a:a['wallets'][0].update(testnetAddress=address('99'*20,'ckt')));self.refused()
    def test_duplicate_json_key(self):
        (self.d/'app.json').write_text('{"schema":17,"schema":18}');self.digest=resign(self.d);self.refused()
    def test_synthetic_never_device_restore(self):
        with self.assertRaises(p.Refused):p.restore_plan(self.d,self.digest,APK,GENESIS,app_fixture())
    def test_restore_map_and_no_secrets(self):
        # Policy unit test only; synthetic origin is explicitly changed to
        # exercise plan construction, never sent to an actual Pocket sandbox.
        m=p.read_json(self.d/'manifest.json');m['kind']='candidate';(self.d/'manifest.json').write_bytes(p.encode(m));self.digest=p.sha(self.d/'manifest.json')
        destination=app_fixture();plan=p.restore_plan(self.d,self.digest,APK,GENESIS,destination)
        self.assertEqual({r['walletId'] for r in plan['progress']},{w['walletId'] for w in destination['wallets']})
        p.secret_gate(p.encode(plan));self.assertNotIn(b'key_material',p.encode(plan))
    def test_physical_serial_refused_before_adb(self):
        from pocket_sandbox import Device
        with self.assertRaises(p.Refused):Device('SYNTHETIC_PHONE_SERIAL',APK)
    def test_wrong_destination_script_refused(self):
        m=p.read_json(self.d/'manifest.json');m['kind']='candidate';(self.d/'manifest.json').write_bytes(p.encode(m));self.digest=p.sha(self.d/'manifest.json')
        destination=app_fixture();destination['wallets'][1]['testnetAddress']=address('99'*20,'ckt');destination['wallets'][1]['mainnetAddress']=address('99'*20,'ckb')
        with self.assertRaises(p.Refused):p.restore_plan(self.d,self.digest,APK,GENESIS,destination)

if __name__=='__main__':unittest.main(verbosity=2)
