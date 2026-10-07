"""Read-only R1A public/native observations; no UI text or credential access."""
import argparse
import datetime
import json
import re
import struct
import zipfile
from pathlib import Path

import h02_package as p
from h02_device import ROOT, APP
from p3c_r1_probe import adb, probe


def mappings(pid):
    receipt = p.read_json(ROOT/'runs/wo3c-r1/phone-artifact.json')
    apk = ROOT/receipt['apkPath']
    raw = adb('shell', 'run-as', APP, 'cat', f'/proc/{pid}/maps')
    mapped = []
    for line in raw.splitlines():
        fields = line.split(None, 5)
        if len(fields) == 6 and 'x' in fields[1]:
            lo, hi = (int(n, 16) for n in fields[0].split('-'))
            mapped.append((int(fields[2], 16), hi-lo, fields[5]))
    result = {}
    with zipfile.ZipFile(apk) as archive, apk.open('rb') as stream:
        for name in ('lib/arm64-v8a/libckb_light_client_lib.so',
                     'lib/arm64-v8a/libsecp256k1-jni.so'):
            info = archive.getinfo(name)
            stream.seek(info.header_offset)
            header = stream.read(30)
            nlen, xlen = struct.unpack_from('<HH', header, 26)
            data_offset = info.header_offset+30+nlen+xlen
            elf = archive.read(name)
            phoff = struct.unpack_from('<Q', elf, 32)[0]
            phsize, phnum = struct.unpack_from('<HH', elf, 54)
            executable = []
            for index in range(phnum):
                kind, flags, offset, _, _, size, _, _ = struct.unpack_from(
                    '<IIQQQQQQ', elf, phoff+index*phsize)
                if kind == 1 and flags & 1:
                    executable.append((data_offset+offset, data_offset+offset+size))
            hits = []
            for offset, size, path in mapped:
                named = path.endswith('/'+Path(name).name)
                zipped = info.compress_type == zipfile.ZIP_STORED and path.endswith('/base.apk') and any(
                    offset < end and offset+size > start for start, end in executable)
                if named or zipped:
                    hits.append({'mappingFileOffset':offset, 'mappingBytes':size,
                                 'method':'named-library' if named else 'APK-ELF-executable-segment-overlap'})
            result[Path(name).name] = {'executableMappingPresent':bool(hits),
                                     'elfMachine':struct.unpack_from('<H',elf,18)[0],
                                     'zipDataOffset':data_offset, 'mappings':hits}
    return result


def lifecycle(pid):
    # Only lifecycle/error tags; never auth/UI/key-material tags. Retain enums only.
    raw = adb('logcat', '-d', '--pid='+pid, '-v', 'brief',
              'NodeLifecycle:D', 'System.err:E', 'AndroidRuntime:E', '*:S')
    phrases = {
        'testnetInitialization':'Initializing embedded node for TESTNET',
        'testnetStartSucceeded':'Node started successfully on TESTNET',
        'nativeInitReturnedFalse':'nativeInit returned false',
        'nativeStartReturnedFalse':'nativeStart returned false',
        'setupError':'Setup error during node initialization',
        'unsatisfiedLinkError':'UnsatisfiedLinkError',
        'nativeLoadSkipped':'LightClientNative: loadLibrary skipped',
        'fatalJavaException':'FATAL EXCEPTION',
        'roomMigrationError':'Migration didn',
        'invalidKeyException':'KeyPermanentlyInvalidatedException',
        'userNotAuthenticatedException':'UserNotAuthenticatedException',
    }
    return {key:sum(phrase in line for line in raw.splitlines()) for key, phrase in phrases.items()}


def observe():
    pid = adb('shell','pidof', APP).strip()
    p.require(re.fullmatch(r'[0-9]+',pid) is not None,'single-pocket-process-required')
    state = probe('app')
    baseline = p.read_json(ROOT/'runs/wo3c-r1/phone-after-overwrite.json')['app']
    coherent = state['wallets'] == baseline['wallets'] and state['keyMetadata'] == baseline['keyMetadata']
    p.require(coherent,'existing-wallet-or-key-metadata-changed')
    p.require(state['roomVersion']==17 and state['roomIdentity']==baseline['roomIdentity'],'room-schema-changed')
    registrations = state.get('nativeRegistrations',[])
    progress = [{'keyHex':r['keyHex'],'blockNumber':int(r['valueHex'],16)} for r in registrations]
    return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'pid':int(pid),
            'devicePageSize':int(adb('shell','getconf','PAGESIZE').strip()),
            'app':state, 'walletMetadataCoherent':coherent, 'nativeProgress':progress,
            'nativeMappings':mappings(pid), 'lifecycleEvents':lifecycle(pid),
            'credentialAccessed':False, 'credentialLogged':False, 'authBypassed':False,
            'H2Activated':False, 'appDataCleared':False, 'transactionsCreated':False, 'D2Used':False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('label',choices=['pre-unlock','unlocked','after-restart','after-restart-settled'])
    args = parser.parse_args()
    out = ROOT/'runs/wo3c-r1a'/('phone-'+args.label+'.json')
    p.require(not out.exists(),'observation-exists')
    result = observe()
    result['label']=args.label
    out.parent.mkdir(exist_ok=True)
    with out.open('xb') as stream:stream.write(p.encode(result))
    print(json.dumps({k:result[k] for k in ('pid','devicePageSize','walletMetadataCoherent','nativeProgress',
                                          'nativeMappings','lifecycleEvents')}))


if __name__=='__main__':
    try:main()
    except Exception as e:
        print('R1A_OBSERVATION_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''))
        raise SystemExit(2)
