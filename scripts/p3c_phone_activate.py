"""PM-authorized Candidate activation through separate qualified phone policy."""
import datetime
import h02_package as p
from h02_device import ROOT
from p3c_phone_destination import compatibility,stage,activate,enable
from p3c_phone_state import save,security
from p3c_phone_ui import BASE,device,event

R='d0f69fd873008f4ec528ddfe1427f4cfac43535f5b10177b4ff7de1bc77ea8ee'
A='b9adf7b0e47e86191808615d05d05b154311f00e1191bcb56c18b4d5cca26b05'

def run():
    folder=BASE/'candidate'
    p.require((folder/'fresh-state.json').exists() and (folder/'public-after-account1.json').exists(),'normal-candidate-recovery-required')
    p.require(not (folder/'activation-stage.json').exists(),'activation-already-staged-retain-and-inspect')
    artifact,manifest,_=compatibility(R,A)
    before=security(device())
    p.require(before==p.read_json(folder/'security-after-account0.json'),'candidate-security-changed-before-activation')
    event('candidate','immutable_H2_phone_validation_pass',H2=manifest['boundary'])
    token=stage(R,A,execute=True)
    save(folder/'activation-stage.json',{'token':token,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'manifestSha256':p.sha(ROOT/'runs/wo3b2/package-H2-immutable/manifest.json'),'destinationApkSha256':artifact['apkSha256'],
        'artifactReceiptDigest':R,'crossAbiAuditDigest':A,'securityBefore':before})
    event('candidate','immutable_H2_phone_staged')
    activate(token,R,A,execute=True)
    after=security(device())
    p.require(after==before,'candidate-keystore-metadata-changed-on-activation')
    d=device();d.deploy();_,app=d.inspect(manifest['format'])
    recovered=p.read_json(folder/'public-after-account1.json')
    p.require(sorted(app['wallets'],key=lambda w:w['accountIndex'])==sorted(recovered['wallets'],key=lambda w:w['accountIndex']),'destination-wallet-identities-changed')
    save(folder/'activation-public.json',app)
    enable(R,A,execute=True)
    save(folder/'activation.json',{'result':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'H2':manifest['boundary'],'H2Hash':'0x'+manifest['boundaryHash'].removeprefix('0x'),
        'sourceManifestUnchanged':True,'destinationSecurityUnchanged':True,'securityAfter':after,
        'destinationWalletIdsUnchanged':True,'normalHelperEncryptedRowDigestGuards':'PASS',
        'sourceSecretsImported':False,'originalEmulatorPolicyRelaxed':False})
    event('candidate','immutable_H2_phone_activation_pass')
    print('PHONE_H2_ACTIVATION_PASS; enabled but not launched')

if __name__=='__main__':
    try:run()
    except Exception as e:
        print('PHONE_ACTIVATION_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else '')+'; retain state and stage journal');raise SystemExit(2)
