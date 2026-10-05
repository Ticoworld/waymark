"""Seal a B1 package from an already accepted, frozen SOURCE; no keys or signing."""
import argparse,datetime,json,shutil,stat,time
from pathlib import Path
from types import SimpleNamespace
import h02_device as d
import h02_package as p
from r2_observe import APK,GENESIS,native
from r2_acceptance import check
from p3_public_chain import rpc

def main(observation,oracle):
    root=d.ROOT/'runs/wo3b1-r2'
    p.require(not (root/'source/LOST.json').exists(),'source-lost')
    n=p.read_json(Path(observation)/'summary.json');app=p.read_json(Path(observation)/'app.json')
    p.require(all(c['state']=='EMPTY' for c in app['candidates']),'source-discovery-unsettled')
    scripts=p.validate_app(app,profile=p.B1_FORMAT)
    h=min(n['verifiedTip'],n['minFiltered'],n['progress'][0]['localSavedBlockNumber'],n['registrations'][next(iter(scripts.values()))+':0'])
    accepted=check(observation,oracle,h)
    header=rpc('https://testnet.ckb.dev','get_header_by_number',[hex(h)])
    tip_header=rpc('https://testnet.ckb.dev','get_header_by_number',[hex(n['verifiedTip'])])
    p.require(tip_header['hash']==n['verifiedTipHash'],'source-tip-not-canonical')
    coverage={w['walletId']:22369937 for w in app['wallets']}
    coverage_path=root/'source/coverage.json'
    with coverage_path.open('xb') as f:f.write(p.encode(coverage))
    out=root/'package-H';a=SimpleNamespace(serial='emulator-5580',apk_sha256=APK,out=str(out),genesis=GENESIS,boundary=h,boundary_hash=header['hash'][2:],coverage=str(coverage_path),profile=p.B1_FORMAT)
    device=d.Device(a.serial,APK);device.stopped()
    p.require(('package:'+d.APP) in device.shell('pm','list','packages','-d','--user','0',d.APP).decode().splitlines(),'source-not-disabled')
    d.HELPER=d.ROOT/'runs/wo3b1-r2/state-helper/helper.jar'
    began=time.monotonic();d.export(a);duration=time.monotonic()-began
    digest=p.sha(out/'manifest.json');p.validate(out,digest,APK,GENESIS)
    exported=native(out/'native.sqlite')
    p.require(all(exported[k]==n[k] for k in ('liveCells','capacity','transactions','registrations','verifiedTipHash','minFiltered')),'capture-changed')
    immutable=root/'package-H-immutable';shutil.copytree(out,immutable)
    p.validate(immutable,digest,APK,GENESIS)
    for file in immutable.iterdir():file.chmod(stat.S_IREAD)
    receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'H':h,'HHash':header['hash'],'sourceVerifiedTip':n['verifiedTip'],'sourceVerifiedTipHash':n['verifiedTipHash'],'sourcePrimaryProgress':n['progress'][0],'sourceMinFiltered':n['minFiltered'],'sourceAcceptance':accepted,'exportSeconds':duration,'packageBytes':sum(f.stat().st_size for f in immutable.iterdir()),'manifestSha256':digest,'contents':{f.name:{'bytes':f.stat().st_size,'sha256':p.sha(f)} for f in immutable.iterdir()},'secretExclusion':'PASS','normalDiscoveryCandidatesEmpty':len(app['candidates']),'immutableCopy':'runs/wo3b1-r2/package-H-immutable','sourceRemainsDisabled':True}
    with (root/'source/package-receipt.json').open('xb') as f:f.write(p.encode(receipt))
    print(json.dumps({k:v for k,v in receipt.items() if k!='sourceAcceptance'},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('observation');parser.add_argument('oracle');a=parser.parse_args()
    try:main(a.observation,a.oracle)
    except Exception as e:print('EXPORT_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''));raise SystemExit(2)
