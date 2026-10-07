"""Qualify the pinned ARM debug artifact without installing or launching it."""
import json
import os
import re
import struct
import subprocess
import zipfile
from pathlib import Path
import h02_package as p
from h02_device import ROOT, APP
from p3c_preflight import certificate
from p3c_r1_audit import GENESIS

def main():
    source = ROOT/'repos/pocket-node'
    p.require(subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==p.PIN, 'source-pin')
    p.require(not subprocess.check_output(['git','-C',str(source),'status','--porcelain=v1'],text=True).strip(), 'source-dirty')
    apk = ROOT/'runs/wo3c-r1/gradle/app/outputs/apk/debug/app-debug.apk'
    cert = certificate(apk)
    p.require(cert['certificateSha256']=='bb4cbddbe25b03a1bac59f9c139f845b15869d0507198a9271103f3a64c96b9a', 'debug-signer-mismatch')
    sdk = Path(os.environ['LOCALAPPDATA'])/'Android/Sdk'
    badging = subprocess.check_output([str(sdk/'build-tools/36.0.0/aapt.exe'),'dump','badging',str(apk)],text=True)
    package = re.search(r"package: name='([^']+)' versionCode='([^']+)' versionName='([^']+)'",badging)
    p.require(package and package.groups()==(APP,'27','1.8.5'), 'apk-version')
    p.require("sdkVersion:'26'" in badging and "targetSdkVersion:'36'" in badging and 'application-debuggable' in badging,'apk-sdk-debug')
    libraries = {}
    with zipfile.ZipFile(apk) as archive:
        for name in archive.namelist():
            if name.startswith('lib/') and name.endswith('.so'):
                data = archive.read(name)
                p.require(data[:4]==b'\x7fELF','native-not-elf')
                machine = struct.unpack('<H',data[18:20])[0]
                expected = {'arm64-v8a':(2,183), 'armeabi-v7a':(1,40)}.get(name.split('/')[1])
                p.require(expected is not None and (data[4],machine)==expected and data[5]==1,
                          'native-library-architecture')
                libraries[name] = {'bytes':len(data),'sha256':__import__('hashlib').sha256(data).hexdigest(),
                                   'elfClass':data[4],'elfEndian':data[5],'elfMachine':machine}
        abis = sorted({name.split('/')[1] for name in libraries})
        for abi, machine in [('arm64-v8a',183)]:
            for lib in ['libckb_light_client_lib.so','libsecp256k1-jni.so']:
                p.require(libraries.get(f'lib/{abi}/{lib}',{}).get('elfMachine')==machine,'required-jni-architecture')
        p.require(abis==['arm64-v8a'],'unexpected-artifact-abis')
        dexes = [archive.read(name) for name in archive.namelist() if re.fullmatch(r'classes\d*\.dex',name)]
        p.require(any(b'b28979d' in data for data in dexes),'debug-git-sha-not-present')
    hashes = {}
    for path in [source/'external/ckb-light-client/Cargo.lock',source/'external/ckb-light-client/build-android-jni.sh',
                 source/'external/ckb-light-client/rust-toolchain',source/'android/app/build.gradle.kts',
                 source/'android/ci/debug.keystore',ROOT/'scripts/p3c_r1_build_arm.ps1',ROOT/'scripts/p3c-r1-build.init.gradle',
                 ROOT/'runs/wo3c-r1/arm-build.log']:
        hashes[str(path.relative_to(ROOT)).replace('\\','/')] = p.sha(path)
    receipt = {'apkPath':str(apk.relative_to(ROOT)).replace('\\','/'),'apkSha256':p.sha(apk),'bytes':apk.stat().st_size,
               'package':APP,'versionName':'1.8.5','versionCode':27,'minSdk':26,'targetSdk':36,'debuggable':True,
               'pocketCommit':p.PIN,'nativeTree':p.LC_TREE,'certificate':cert,'abis':abis,'libraries':libraries,
               'requiredArm64JniPresent':True,'roomSchema':17,'roomIdentity':p.IDENTITY,'nativeSchema':p.NATIVE_SCHEMA,
               'network':'TESTNET','genesis':GENESIS,'productionSourceModified':False,'buildInputsAndLog':hashes,
               'build':{'rust':'1.92.0-x86_64-pc-windows-msvc','ndk':'27.0.12077973','nativeApi':21,
                        'features':['jni-bridge','portable'],'cargoLocked':True,'BUILD_X86_64':'unset',
                        'signing':'repository ci/debug.keystore alias smokedebug',
                        'hostAdaptation':'Windows compiler/host CRT setup; same pinned Cargo ARM64 target/features/stubs; output isolation and ARM64-only Gradle test packaging; unchanged application logic and stable debug signer'}}
    out = ROOT/'runs/wo3c-r1/phone-artifact.json'
    with out.open('xb') as stream:stream.write(p.encode(receipt))
    (ROOT/'runs/wo3c-r1/debug-badging.txt').write_text(badging)
    print('PHONE_ARTIFACT_QUALIFIED',receipt['apkSha256'])
    print('ARTIFACT_RECEIPT_SHA256',p.sha(out))

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('PHONE_ARTIFACT_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''))
        raise SystemExit(2)
