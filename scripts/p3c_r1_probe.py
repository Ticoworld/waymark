"""Explicitly allowlisted, read-only Samsung public/security projection."""
import argparse
import json
import os
import subprocess
from pathlib import Path
import h02_package as p
from h02_device import ROOT, APP

SERIAL = 'R5CW6127VPR'
REMOTE = '/data/local/tmp/h02-phone-readonly-r1.jar'

def adb(*args):
    result = subprocess.run([str(Path(os.environ['LOCALAPPDATA'])/'Android/Sdk/platform-tools/adb.exe'),
                             '-s', SERIAL, *args], capture_output=True, timeout=60)
    p.require(result.returncode == 0, 'phone-probe-adb-refused')
    return result.stdout.decode('utf-8', errors='replace')

def probe(action):
    args = ['env', 'CLASSPATH='+REMOTE, '/system/bin/app_process', '/system/bin',
            'h02.H02PhoneReadOnly', action]
    if action == 'app':
        args = ['run-as', APP, *args]
    raw = adb('shell', *args)
    lines = [line.split('=', 1)[1] for line in raw.splitlines() if line.startswith('H02_PHONE_PUBLIC_JSON=')]
    p.require(len(lines) == 1, 'phone-projection-refused')
    return json.loads(lines[0])

def main():
    a = argparse.ArgumentParser(); a.add_argument('label'); args = a.parse_args()
    p.require(args.label in ('before-overwrite', 'after-overwrite', 'after-restart'), 'probe-label')
    out = ROOT/'runs/wo3c-r1'/('phone-'+args.label+'.json')
    p.require(not out.exists(), 'output-exists')
    p.require(adb('shell', 'getprop', 'ro.product.model').strip() == 'SM-S9180', 'wrong-phone')
    p.require(adb('shell', 'getprop', 'ro.product.cpu.abi').strip() == 'arm64-v8a', 'wrong-abi')
    local = ROOT/'runs/wo3c-r1/phone-helper/helper.jar'
    adb('push', str(local), REMOTE)
    adb('shell', 'chmod', '444', REMOTE)
    p.require(adb('shell', 'sha256sum', REMOTE).split()[0] == p.sha(local), 'probe-digest')
    result = {'label': args.label, 'serial': SERIAL, 'helperSha256': p.sha(local)}
    result['app'] = probe('app')
    # Android API access may be restricted. Do not replace refusal with a lock dump.
    try:
        result['security'] = probe('security')
    except p.Refused:
        result['security'] = {'status': 'UNKNOWN_API_PROBE_REFUSED'}
    result['appDataCleared'] = False
    result['credentialAccessed'] = False
    result['authBypass'] = False
    out.write_bytes(p.encode(result))
    print('PHONE_READ_ONLY_PROJECTION_SAVED '+str(out.relative_to(ROOT)))
    print('WALLET_COUNT', len(result['app']['wallets']))
    print('KDF_VERSIONS', sorted({r['kdfVersion'] for r in result['app']['keyMetadata']}))
    print('SECURITY', json.dumps(result['security']))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('PHONE_PROBE_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''))
        raise SystemExit(2)
