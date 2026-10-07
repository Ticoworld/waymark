"""Offline refusal checks for the new boundary and unchanged emulator policy."""
import copy
import json
import tempfile
from pathlib import Path
import h02_package as p
import h02_device as e
import p3c_phone_destination as phone
from p3c_r1_audit import SOURCE_APK, TRUST, GENESIS, PACKAGE

def refused(name, fn, code, results):
    try:
        fn()
    except p.Refused as error:
        p.require(str(error)==code, 'wrong-refusal-'+name)
        results.append({'case':name,'result':'PASS','reason':code})
    else:
        raise p.Refused('accepted-invalid-'+name)

def main():
    original = phone.RECEIPT
    digest = p.sha(original); abi_digest = p.sha(phone.AUDIT)
    artifact = p.read_json(original); results = []
    phone.compatibility(digest,abi_digest)
    results.append({'case':'qualified-source-destination-pair','result':'PASS'})
    refused('emulator-rejects-phone',lambda:e.Device(phone.SERIAL,SOURCE_APK),'physical-device-refused',results)
    refused('source-validator-does-not-accept-destination-hash',
            lambda:p.validate(PACKAGE,TRUST,artifact['apkSha256'],GENESIS),'apk-mismatch',results)
    refused('R1-stage-gate-before-any-ADB',lambda:phone.stage(digest,abi_digest),
            'phone-stage-not-authorized-in-r1',results)
    refused('wrong-receipt-digest',lambda:phone.compatibility('0'*64,abi_digest),
            'phone-artifact-receipt-digest',results)
    with tempfile.TemporaryDirectory(prefix='phone-policy-',dir=phone.ROOT/'runs/wo3c-r1') as tmp:
        for name,change,code in [
            ('wrong-signer',lambda a:a['certificate'].update(certificateSha256='0'*64),'phone-signer'),
            ('wrong-source',lambda a:a.update(pocketCommit='0'*40),'phone-source-provenance'),
            ('wrong-network',lambda a:a.update(network='MAINNET'),'phone-network'),
            ('wrong-schema',lambda a:a.update(roomSchema=16),'phone-schema'),
            ('no-arm64',lambda a:a.update(abis=['x86_64']),'phone-abi-or-transport')]:
            altered=copy.deepcopy(artifact);change(altered)
            path=Path(tmp)/(name+'.json');path.write_bytes(p.encode(altered));phone.RECEIPT=path
            refused(name,lambda:phone.compatibility(p.sha(path),abi_digest),code,results)
    phone.RECEIPT=original
    phone.compatibility(digest,abi_digest)
    out=phone.ROOT/'runs/wo3c-r1/policy-checks.json'
    with out.open('xb') as stream:stream.write(p.encode({'results':results,'result':'PASS','deviceOperationsExecuted':False}))
    print('PHONE_POLICY_REFUSAL_CHECKS_PASS',len(results))

if __name__=='__main__':main()
