"""Verify local destination Keystore/key continuity; public challenge and signatures only."""
import argparse,hashlib,json,secrets,uuid
from coincurve import PublicKey
from h02_device import Device,ROOT,REMOTE_ROOT
from r2_public_tap import APK
from h02_package import require,encode
from b2r2_chain import ARGS,ckb_hash
def check(label):
    out=ROOT/'runs/wo3b2'/label;require(not out.exists(),'signing-output-exists')
    d=Device('emulator-5580',APK);d.freeze()
    jar=ROOT/'runs/wo3b2-r2/sign-helper/helper.jar';remote=REMOTE_ROOT+'/files/h02-sign-'+uuid.uuid4().hex[:16]+'.jar'
    d.put(remote,jar.read_bytes());d.sandbox('chmod','400',remote)
    apk=d.shell('pm','path','com.rjnr.pocketnode').decode().strip()[8:]
    challenge=hashlib.sha256(b'H02 B2 local signing readiness, NOT a transaction\0'+secrets.token_bytes(32)).hexdigest()
    raw=d.sandbox('env','CLASSPATH='+remote,'/system/bin/app_process','/system/bin','h02.H02Sign',apk,REMOTE_ROOT,challenge)
    # Parse only the expected public result. No arbitrary stdout/error is emitted.
    result=json.loads(raw);require(set(result)=={'challenge','accounts'} and result['challenge']==challenge,'challenge-result')
    require(len(result['accounts'])==2,'signing-account-count')
    for i,row in enumerate(result['accounts']):
        require(set(row)=={'walletId','accountIndex','publicKey','signature'} and row['accountIndex']==i,'signing-account-map')
        pub=bytes.fromhex(row['publicKey']);sig=bytes.fromhex(row['signature'])
        recovered=PublicKey.from_signature_and_message(sig,bytes.fromhex(challenge),hasher=None).format(compressed=True)
        require(pub==recovered and ckb_hash(pub)[:20].hex()==ARGS[i],'signing-identity-mismatch')
    result.update({'result':'PASS','apkSha256':APK,'helperSha256':hashlib.sha256(jar.read_bytes()).hexdigest(),'scope':'V1 emulator keys, local Keystore decryption plus shipped Pocket signer; no transaction or V2 claim'})
    out.write_bytes(encode(result));print('TWO_ACCOUNT_LOCAL_SIGNING_PASS; Pocket remains disabled')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('label');a=p.parse_args()
    try:check(a.label)
    except Exception as e:print('SIGNING_CHECK_REFUSED '+type(e).__name__+'; no raw diagnostics');raise SystemExit(2)
