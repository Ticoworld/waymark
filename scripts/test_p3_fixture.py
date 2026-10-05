"""Synthetic crypto/refusal checks only; never reads the real private fixture."""
import hashlib, json, unittest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw,Type
from p3_fixture import pub,address,identity,decrypt_backup,validate_words,ROOT

class FixtureChecks(unittest.TestCase):
    def test_public_secp256k1_vector(self):
        self.assertEqual(pub((1).to_bytes(32,'big')).hex(),'0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798')

    def test_network_encoding_and_identity(self):
        k=(2).to_bytes(32,'big')
        w={'walletId':'synthetic','derivationPath':"m/44'/309'/0'/0/0",'mainnetAddress':address(k,'ckb'),'testnetAddress':address(k,'ckt')}
        self.assertEqual(identity(k,w)['result'],'MATCH')
        with self.assertRaises(ValueError):identity((3).to_bytes(32,'big'),w)

    def test_bip39_checksum(self):
        words=(ROOT/'scripts/bip39-english.txt').read_text().split()
        validate_words(' '.join([words[0]]*11+[words[3]]))
        with self.assertRaises(ValueError):validate_words(' '.join([words[0]]*12))

    def test_pnbk_formats_authentication_and_rejection(self):
        salt=b'\x01'*16;iv=b'\x02'*12;pin='synthetic-only';data={'test':'non-wallet'}
        for version in (1,2):
            key=hashlib.pbkdf2_hmac('sha256',pin.encode(),salt,600000,32) if version==1 else hash_secret_raw(pin.encode(),salt,3,65536,4,32,Type.ID,19)
            blob=b'PNBK'+bytes([version])+salt+iv+AESGCM(key).encrypt(iv,json.dumps(data).encode(),None)
            self.assertEqual(decrypt_backup(blob,pin),data)
            for bad,credential in [(blob,'wrong-synthetic'),(blob[:-1],pin),(blob[:-1]+bytes([blob[-1]^1]),pin),(blob[:4]+b'\x03'+blob[5:],pin),(b'junk',pin)]:
                with self.assertRaises(Exception):decrypt_backup(bad,credential)

if __name__=='__main__':unittest.main()
