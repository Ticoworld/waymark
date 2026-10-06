"""Fail-closed gates on disposable copies of a real B2 package; no adb or activation."""
import argparse,json,shutil,sqlite3,stat,uuid
from pathlib import Path
import h02_package as p
from h02_device import ROOT,run_dir
from r2_observe import APK,GENESIS

def main(package,trust):
    p.validate(package,trust,APK,GENESIS)
    out=run_dir(ROOT/'runs/wo3b2/negative-packages'/uuid.uuid4().hex)
    results=[]
    for name in ('corrupt-payload','missing-payload','wrong-network','wrong-genesis','unsupported-pocket-version','unsupported-room-schema','unsupported-native-schema','manifest-digest-mismatch','payload-hash-mismatch'):
        d=out/name;shutil.copytree(package,d);digest=trust
        for member in d.iterdir():
            p.require(member.resolve().is_relative_to(out.resolve()),'test-copy-path')
            member.chmod(stat.S_IREAD|stat.S_IWRITE)
        m=p.read_json(d/'manifest.json')
        if name=='corrupt-payload':
            b=bytearray((d/'native.sqlite').read_bytes());b[0]^=0xff;(d/'native.sqlite').write_bytes(b)
        elif name=='missing-payload':(d/'app.json').unlink()
        elif name=='wrong-network':m['network']='MAINNET'
        elif name=='wrong-genesis':m['genesis']='00'*32
        elif name=='unsupported-pocket-version':m['versionName']='1.8.6'
        elif name=='unsupported-room-schema':m['roomSchema']=18
        elif name=='unsupported-native-schema':
            db=sqlite3.connect(d/'native.sqlite');db.execute('PRAGMA user_version=1');db.close()
            m['files']['native.sqlite']={'bytes':(d/'native.sqlite').stat().st_size,'sha256':p.sha(d/'native.sqlite')}
        elif name=='manifest-digest-mismatch':m['boundary']+=1
        elif name=='payload-hash-mismatch':(d/'app.json').write_bytes((d/'app.json').read_bytes()+b' ')
        if name not in ('corrupt-payload','missing-payload','payload-hash-mismatch'):
            (d/'manifest.json').write_bytes(p.encode(m))
            # Deliberately trust changed test manifest for inner semantic gates.
            # Production callers must retain the original trusted digest.
            if name!='manifest-digest-mismatch':digest=p.sha(d/'manifest.json')
        try:p.validate(d,digest,APK,GENESIS)
        except p.Refused as e:results.append({'case':name,'rejected':True,'gate':str(e)})
        else:raise ValueError('negative accepted')
    result={'baselineManifest':trust,'deviceActivationAttempted':False,'results':results}
    (out/'result.json').write_bytes(p.encode(result));print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('package',type=Path);parser.add_argument('--trust',required=True);a=parser.parse_args()
    try:main(a.package,a.trust)
    except Exception as e:print('NEGATIVE_GATE_TEST_FAILED '+type(e).__name__);raise SystemExit(2)
