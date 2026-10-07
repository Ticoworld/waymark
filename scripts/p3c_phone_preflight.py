"""Fail-closed pre-reset custody/input checks; no credential output."""
import json
import hashlib
import datetime
import h02_package as p
from h02_device import ROOT
from p3_fixture import FIXTURE,verify,derive,pub
from p3c_phone_ui import BASE,INPUT,UIJAR
from p3c_phone_destination import compatibility,PhoneDevice,SERIAL

def check():
    artifact,manifest,_=compatibility(
        'd0f69fd873008f4ec528ddfe1427f4cfac43535f5b10177b4ff7de1bc77ea8ee',
        'b9adf7b0e47e86191808615d05d05b154311f00e1191bcb56c18b4d5cca26b05')
    PhoneDevice(SERIAL,artifact,execute=True)
    p.require(FIXTURE.is_file(),'private-fixture-missing')
    fixture=json.loads(FIXTURE.read_text(encoding='utf-8'));verify(fixture)
    paths=["m/44'/309'/0'/0/0","m/44'/309'/1'/0/0"]
    args=[hashlib.blake2b(pub(derive(fixture['wallets'][0]['mnemonic'],path)),digest_size=32,
          person=b'ckb-default-hash').digest()[:20].hex() for path in paths]
    p.require(args==['bc5882c4309431ee23ad7bbad4b5c3325539eebd','2da024570462b0e2421d87abcbfebd4567d52ad5'],'fixture-two-identities')
    evidence=['runs/wo3b2/oracle-H2.json','runs/wo3b2/oracle-F2.json','runs/wo3b2/final-boundary.json',
              'runs/wo3b2/control/result.json','runs/wo3b2/candidate/result.json','runs/wo3c-r1a/qualification-result.json']
    for rel in evidence:p.require((ROOT/rel).is_file(),'required-public-evidence-missing')
    p.require(manifest['boundary']==22652549 and manifest['boundaryHash'].removeprefix('0x')==
        '3f96acadbf4ef0d847db36468ca13feb37630fd5a156a5540713897c0dd4e3ee','H2-boundary')
    p.require(UIJAR.is_file(),'protected-ui-helper-missing')
    BASE.mkdir(parents=True,exist_ok=True)
    legacy=BASE/'original-preflight-reports';legacy.mkdir(exist_ok=True)
    for name in ['P3C_PHONE_CONTROL.md','P3C_PHONE_CANDIDATE.md','P3C_PHONE_COMPARISON.md','P3C_DECISION.md']:
        target=legacy/name
        if not target.exists():
            with target.open('xb') as stream:stream.write((ROOT/'docs'/name).read_bytes())
    p.require(INPUT.is_file(),'protected-automation-input-missing')
    automation=json.loads(INPUT.read_text(encoding='utf-8'))
    p.require(isinstance(automation,dict) and isinstance(automation.get('pin'),str)
              and automation['pin'].isdigit() and len(automation['pin'])==6,
              'protected-automation-input-invalid')
    del automation
    return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'PASS',
        'fixtureVerifiedInMemory':True,'privateFixturePreserved':True,'paths':paths,'scriptArgs':args,
        'phoneSerial':SERIAL,'phoneModel':'SM-S9180','phoneApkSha256':artifact['apkSha256'],
        'signerSha256':artifact['certificate']['certificateSha256'],'H2':manifest['boundary'],
        'H2Hash':'0x'+manifest['boundaryHash'].removeprefix('0x'),
        'manifestSha256':p.sha(ROOT/'runs/wo3b2/package-H2-immutable/manifest.json'),
        'oraclesAndEvidence':[{'path':rel,'sha256':p.sha(ROOT/rel)} for rel in evidence],
        'uiHelperSha256':p.sha(UIJAR),'scopeOfAuthorizedReset':'Only com.rjnr.pocketnode user 0; no unrelated data','D2Used':False}

if __name__=='__main__':
    try:
        result=check()
        with (BASE/'pre-destructive-check.json').open('xb') as f:f.write(p.encode(result))
        print('PRE_DESTRUCTIVE_CHECK_PASS; fixture/two identities/APK/H2/evidence/phone verified')
    except Exception as e:
        print('PHONE_PREFLIGHT_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''))
        raise SystemExit(2)
