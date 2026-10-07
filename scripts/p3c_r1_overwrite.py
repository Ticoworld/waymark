"""Authorized R1 signature-compatible overwrite only. Never clears app data."""
import datetime
import json
import os
import subprocess
import time
from pathlib import Path
import h02_package as p
from h02_device import ROOT, APP
from p3c_r1_probe import SERIAL, adb
from p3c_phone_destination import compatibility, RECEIPT, AUDIT, SIGNER, PhoneDevice

def main():
    out = ROOT/'runs/wo3c-r1/overwrite.json'
    p.require(not out.exists(), 'overwrite-result-exists')
    artifact, _, _ = compatibility(p.sha(RECEIPT),p.sha(AUDIT))
    before = p.read_json(ROOT/'runs/wo3c-r1/phone-before-overwrite.json')
    wallets = before['app']['wallets']
    p.require(len(wallets)==1 and wallets[0]['accountIndex']==0 and
              p.script_from_address(wallets[0]['testnetAddress'],'TESTNET')[-40:] ==
              'bc5882c4309431ee23ad7bbad4b5c3325539eebd','existing-wallet-identity')
    p.require(before['app']['keyMetadata']==[{'walletId':wallets[0]['walletId'],'kdfVersion':2}],
              'existing-security-state-changed')
    baseline = p.read_json(ROOT/'runs/wo3c/preflight/result.json')
    official = p.read_json(ROOT/'runs/wo3c-r1/official-result.json')
    p.require(official['certificate']['certificateSha256']!=SIGNER,'official-artifact-priority')
    p.require(baseline['currentPocket']['certificate']['certificateSha256']==SIGNER,
              'baseline-signer')
    paths=adb('shell','pm','path',APP).strip().splitlines()
    p.require(len(paths)==1 and paths[0].startswith('package:/data/app/'),'existing-apk-path')
    p.require(adb('shell','sha256sum',paths[0][8:]).split()[0]==baseline['currentPocket']['apkSha256'],
              'installed-pocket-changed-before-overwrite')
    apk=ROOT/artifact['apkPath']
    start=time.monotonic()
    command=[str(Path(os.environ['LOCALAPPDATA'])/'Android/Sdk/platform-tools/adb.exe'),
             '-s',SERIAL,'install','-r','--no-streaming',str(apk)]
    result=subprocess.run(command,capture_output=True,text=True,timeout=300)
    success=result.returncode==0 and 'Success' in result.stdout
    receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'serial':SERIAL,
             'attempted':True,'succeeded':success,'durationSeconds':time.monotonic()-start,
             'flags':['-r','--no-streaming'],'apkSha256':artifact['apkSha256'],'signerSha256':SIGNER,
             'appDataCleared':False,'uninstallAttempted':False,'H2Activated':False,'transactionsCreated':False,
             'artifactReceiptSha256':p.sha(RECEIPT),'compatibilityAuditSha256':p.sha(AUDIT)}
    with out.open('xb') as stream:stream.write(p.encode(receipt))
    p.require(success,'signature-compatible-overwrite-failed')
    PhoneDevice(SERIAL,artifact)
    print('PHONE_OVERWRITE_SUCCESS; no clear, uninstall, launch, recovery, or transaction')

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('PHONE_OVERWRITE_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''))
        raise SystemExit(2)
