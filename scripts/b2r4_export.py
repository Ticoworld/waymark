"""Seal B2 package under the PM-approved R4 canonical-position contract."""
import argparse,datetime,json,shutil,stat,time
from pathlib import Path
from types import SimpleNamespace
import h02_device as d
import h02_package as p
from b2r2_observe import APK,GENESIS,native
from b2r4_acceptance import check
from b2r2_acceptance import FLOORS
from b2r2_chain import ARGS,URL
from p3_public_chain import rpc
def main(observation,oracle,dao_audit):
    root=d.ROOT/'runs/wo3b2';p.require(not (root/'source/LOST.json').exists(),'source-lost')
    n=p.read_json(Path(observation)/'summary.json');app=p.read_json(Path(observation)/'app.json')
    scripts=p.validate_app(app)
    h=min([a['verifiedTip'] for a in n['accounts']]+[a['minFiltered'] for a in n['accounts']]+[r['localSavedBlockNumber'] for r in n['progress']]+[a['registrations'][scripts[a['wallet']['walletId']]+':0'] for a in n['accounts']])
    accepted=check(observation,oracle,h,dao_audit=dao_audit)
    header=rpc(URL,'get_header_by_number',[hex(h)])
    for a in n['accounts']:
        p.require(rpc(URL,'get_block_hash',[hex(a['verifiedTip'])])==a['verifiedTipHash'],'source-tip-not-canonical')
    coverage={w['walletId']:FLOORS[w['accountIndex']] for w in app['wallets']}
    path=root/'source/coverage.json'
    with path.open('xb') as f:f.write(p.encode(coverage))
    out=root/'package-H2';args=SimpleNamespace(serial='emulator-5580',apk_sha256=APK,out=str(out),genesis=GENESIS,boundary=h,boundary_hash=header['hash'][2:],coverage=str(path),profile=p.FORMAT)
    device=d.Device(args.serial,APK);device.stopped()
    p.require(('package:'+d.APP) in device.shell('pm','list','packages','-d','--user','0',d.APP).decode().splitlines(),'source-not-disabled')
    d.HELPER=d.ROOT/'runs/wo3b2-r2/state-helper/helper.jar'
    start=time.monotonic();d.export(args);duration=time.monotonic()-start
    digest=p.sha(out/'manifest.json');p.validate(out,digest,APK,GENESIS)
    from b2r4_secret_gate import check as exact_secret_check
    exact_gate=exact_secret_check(out)
    for a in n['accounts']:
        exported=native(out/'native.sqlite',ARGS[a['wallet']['accountIndex']])
        p.require(all(exported[k]==a[k] for k in ('liveCells','capacity','transactions','registrations','verifiedTipHash','minFiltered')),'capture-changed')
    immutable=root/'package-H2-immutable';shutil.copytree(out,immutable);p.validate(immutable,digest,APK,GENESIS)
    for file in immutable.iterdir():file.chmod(stat.S_IREAD)
    receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'H2':h,'H2Hash':header['hash'],'header':header,'sourceAcceptance':accepted,'exportSeconds':duration,'packageBytes':sum(f.stat().st_size for f in immutable.iterdir()),'manifestSha256':digest,'contents':{f.name:{'bytes':f.stat().st_size,'sha256':p.sha(f)} for f in immutable.iterdir()},'secretExclusion':'PASS','immutableCopy':'runs/wo3b2/package-H2-immutable','sourceRemainsDisabled':True}
    receipt['exactCredentialExclusion']=exact_gate
    with (root/'source/package-receipt.json').open('xb') as f:f.write(p.encode(receipt))
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('sourceAcceptance','header')},indent=2))
if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('observation');q.add_argument('oracle');q.add_argument('--dao-audit',required=True);a=q.parse_args()
    try:main(a.observation,a.oracle,a.dao_audit)
    except Exception as e:print('B2_EXPORT_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''));raise SystemExit(2)
