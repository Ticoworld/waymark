"""Exercise B1 extraction/staging/activation only in generated /data/local/tmp files.
No production Pocket sandbox is read or written by these helper invocations.
"""
import hashlib,json,sqlite3,uuid
import h02_package as p
from h02_device import Device,ROOT,run_dir
from r2_observe import APK
from test_r2_profile import one
from test_android_helper import make_source

def main():
    d=Device('emulator-5580',APK);token=uuid.uuid4().hex[:16]
    local=run_dir(ROOT/'runs/wo3b1-r2/synthetic-android'/token)
    app=one();src=local/'source';make_source(src,app,p.B1_FORMAT)
    remote='/data/local/tmp/h02-synthetic-'+token
    jar='/data/local/tmp/h02-synthetic-helper-'+token+'.jar'
    d.call('push',str(ROOT/'runs/wo3b1-r2/state-helper/helper.jar'),jar)
    d.call('push',str(src),remote)
    def helper(action,where,*args):
        raw=d.shell('env','CLASSPATH='+jar,'app_process','/system/bin','h02.H02State',action,remote,where,*args)
        p.require(raw.strip()==b'H02_HELPER_OK','synthetic-helper-refused')
    export=remote+'/files/h02-export-test';helper('export-b1',export)
    pkg=local/'package';pkg.mkdir()
    for name in ('app.json','native.sqlite'):d.call('pull',export+'/'+name,str(pkg/name))
    a=p.read_json(pkg/'app.json');scripts=p.validate_app(a,profile=p.B1_FORMAT);p.secret_gate((pkg/'app.json').read_bytes())
    stage=remote+'/files/h02-stage-'+token;d.shell('mkdir',stage)
    plan={'format':p.B1_FORMAT,'destinationScripts':scripts,'progress':a['progress'],'candidates':a['candidates'],'prefs':a['prefs'],'nativeSha256':p.sha(pkg/'native.sqlite')}
    (local/'plan.json').write_bytes(p.encode(plan))
    for name,source in [('plan.json',local/'plan.json'),('destination.json',pkg/'app.json'),('native.sqlite',pkg/'native.sqlite')]:d.call('push',str(source),stage+'/'+name)
    helper('stage',stage,p.sha(local/'plan.json'));helper('commit',stage)
    result=local/'destination-synthetic.db';d.call('pull',remote+'/databases/pocket_node.db',str(result))
    db=sqlite3.connect(result)
    try:
        p.require(db.execute('SELECT count(*) FROM key_material WHERE encryptedPrivateKey=?',(b'H02_TEST_SECRET_encrypted',)).fetchone()[0]==1,'synthetic-key-canary-changed')
        p.require(db.execute('SELECT count(*) FROM wallets').fetchone()[0]==1,'synthetic-account-count')
    finally:db.close()
    p.require(b'H02_TEST_SECRET_PIN' in d.shell('cat',remote+'/shared_prefs/ckb_pin_prefs.xml'),'synthetic-pin-changed')
    report={'kind':'synthetic-only','profile':p.B1_FORMAT,'extraction':'PASS','stage':'PASS','activation':'PASS','key_and_pin_canaries_preserved':True,'no_actual_wallet_restore':True}
    (local/'result.json').write_bytes(p.encode(report));print(json.dumps(report))

if __name__=='__main__':
    try:main()
    except Exception as e:print('SYNTHETIC_HELPER_REFUSED '+type(e).__name__);raise SystemExit(2)
