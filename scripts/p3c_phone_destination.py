"""Separate Samsung destination policy. R1 CLI validates only; no activation CLI.

Future PM-authorized P-B may call stage/activate/enable with an explicit execution
flag. Original emulator Device and source-package validator remain unchanged.
"""
import argparse
import hashlib
import json
import re
import uuid
from pathlib import Path
import h02_device as emulator
import h02_package as policy
from p3c_r1_audit import SOURCE_APK, TRUST, GENESIS, PACKAGE, audit

SERIAL = 'R5CW6127VPR'
SIGNER = 'bb4cbddbe25b03a1bac59f9c139f845b15869d0507198a9271103f3a64c96b9a'
ROOT = emulator.ROOT
APP = emulator.APP
REMOTE_ROOT = emulator.REMOTE_ROOT
RECEIPT = ROOT/'runs/wo3c-r1/phone-artifact.json'
AUDIT = ROOT/'runs/wo3c-r1/cross-abi-audit.json'

def compatibility(receipt_digest, audit_digest):
    policy.require(policy.sha(RECEIPT) == receipt_digest, 'phone-artifact-receipt-digest')
    policy.require(policy.sha(AUDIT) == audit_digest, 'phone-audit-digest')
    artifact = policy.read_json(RECEIPT)
    policy.require(artifact['pocketCommit'] == policy.PIN and artifact['nativeTree'] == policy.LC_TREE,
                   'phone-source-provenance')
    policy.require(artifact['package'] == APP and artifact['versionName'] == '1.8.5' and artifact['versionCode'] == 27,
                   'phone-version')
    policy.require(artifact['certificate']['signatureVerified'] and artifact['certificate']['certificateSha256'] == SIGNER,
                   'phone-signer')
    policy.require(artifact['debuggable'] is True and 'arm64-v8a' in artifact['abis']
                   and artifact['requiredArm64JniPresent'] is True, 'phone-abi-or-transport')
    policy.require(artifact['roomSchema'] == 17 and artifact['roomIdentity'] == policy.IDENTITY
                   and artifact['nativeSchema'] == policy.NATIVE_SCHEMA, 'phone-schema')
    policy.require(artifact['network'] == 'TESTNET' and artifact['genesis'] == GENESIS, 'phone-network')
    path = (ROOT/ artifact['apkPath']).resolve()
    policy.require(path.is_relative_to((ROOT/'runs/wo3c-r1').resolve()) and path.is_file()
                   and not path.is_symlink(), 'phone-artifact-path')
    policy.require(policy.sha(path) == artifact['apkSha256'], 'phone-artifact-hash')
    policy.require(json.loads(policy.encode(audit())) == policy.read_json(AUDIT), 'phone-compatibility-audit-changed')
    # Source provenance is ALWAYS validated with its source hash, never destination hash.
    manifest, source = policy.validate(PACKAGE, TRUST, SOURCE_APK, GENESIS)
    return artifact, manifest, source

class PhoneDevice(emulator.Device):
    def __init__(self, serial, artifact, execute=False):
        policy.require(serial == SERIAL, 'phone-serial-not-allowlisted')
        self.serial = serial
        self.apk_hash = artifact['apkSha256']
        self.execute = execute
        import os
        self.adb = str(Path(os.environ['LOCALAPPDATA'])/'Android/Sdk/platform-tools/adb.exe')
        policy.require(self.shell('getprop','ro.product.model').strip() == b'SM-S9180', 'phone-model')
        policy.require(self.shell('getprop','ro.kernel.qemu').strip() != b'1', 'emulator-not-phone')
        policy.require(self.shell('getprop','ro.build.version.sdk').strip() == b'36'
                       and self.shell('getprop','ro.product.cpu.abi').strip() == b'arm64-v8a', 'phone-profile')
        info = self.shell('dumpsys','package',APP).decode()
        policy.require(re.search(r'versionName=1\.8\.5(?:\s|$)',info)
                       and re.search(r'versionCode=27\b',info) and 'DEBUGGABLE' in info, 'phone-installed-build')
        paths = self.shell('pm','path',APP).decode().strip().splitlines()
        policy.require(len(paths)==1 and paths[0].startswith('package:/data/app/'), 'phone-apk-path')
        policy.require(self.shell('sha256sum',paths[0][8:]).decode().split()[0] == self.apk_hash,
                       'phone-installed-apk-hash')
        self.helper_path = ROOT/'runs/wo3b2-r2/state-helper/helper.jar'
        policy.require(policy.sha(self.helper_path) == policy.read_json(AUDIT)['helperSha256'], 'phone-helper-hash')

    def mutation_gate(self):
        policy.require(self.execute is True, 'phone-activation-not-authorized-in-r1')

    def freeze(self):
        self.mutation_gate()
        super().freeze()

    def deploy(self):
        self.mutation_gate()
        self.sandbox('mkdir','-p',REMOTE_ROOT+'/files')
        self.jar = REMOTE_ROOT+'/files/h02-helper-'+uuid.uuid4().hex[:16]+'.jar'
        self.put(self.jar,self.helper_path.read_bytes())
        self.sandbox('chmod','400',self.jar)

    def helper(self, *args):
        self.mutation_gate()
        return super().helper(*args)

    def put(self, *args, **kwargs):
        self.mutation_gate()
        return super().put(*args, **kwargs)

def stage(receipt_digest, audit_digest, execute=False):
    policy.require(execute is True, 'phone-stage-not-authorized-in-r1')
    artifact, manifest, _ = compatibility(receipt_digest,audit_digest)
    device = PhoneDevice(SERIAL,artifact,execute=True)
    device.freeze(); device.deploy()
    raw, destination = device.inspect(manifest['format'])
    # Strict normal-recovery identity matching and destination UUID remapping.
    plan = policy.restore_plan(PACKAGE,TRUST,SOURCE_APK,GENESIS,destination)
    token = uuid.uuid4().hex[:16]
    remote = REMOTE_ROOT+'/files/h02-stage-'+token
    device.sandbox('mkdir','-m','700',remote)
    encoded = policy.encode(plan)
    device.put(remote+'/plan.json',encoded)
    device.put(remote+'/destination.json',raw)
    device.put(remote+'/native.sqlite',(PACKAGE/'native.sqlite').read_bytes())
    device.helper('stage',remote,hashlib.sha256(encoded).hexdigest())
    return token

def activate(token, receipt_digest, audit_digest, action='commit', execute=False):
    policy.require(execute is True, 'phone-activation-not-authorized-in-r1')
    policy.require(action in ('commit','rollback') and re.fullmatch('[0-9a-f]{16}',token), 'phone-stage-token')
    artifact, _, _ = compatibility(receipt_digest,audit_digest)
    device = PhoneDevice(SERIAL,artifact,execute=True)
    device.freeze(); device.deploy()
    device.helper(action,REMOTE_ROOT+'/files/h02-stage-'+token)

def enable(receipt_digest,audit_digest,execute=False):
    policy.require(execute is True, 'phone-enable-not-authorized-in-r1')
    artifact, _, _ = compatibility(receipt_digest,audit_digest)
    device = PhoneDevice(SERIAL,artifact,execute=True); device.stopped()
    device.sandbox('test','!','-e',REMOTE_ROOT+'/files/h02-restore-journal.json')
    device.shell('pm','enable','--user','0',APP)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt-trust',required=True)
    parser.add_argument('--audit-trust',required=True)
    parser.add_argument('--check-installed',action='store_true')
    args = parser.parse_args()
    artifact, _, _ = compatibility(args.receipt_trust,args.audit_trust)
    if args.check_installed: PhoneDevice(SERIAL,artifact)
    print('PHONE_DESTINATION_COMPATIBILITY_PASS; no state activation or wallet recovery')

if __name__ == '__main__':
    try: main()
    except (policy.Refused,ValueError,KeyError,TypeError,OSError):
        print('PHONE_DESTINATION_REFUSED'); raise SystemExit(2)
