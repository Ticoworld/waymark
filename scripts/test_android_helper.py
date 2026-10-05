"""Runs the standalone helper on synthetic SQLite files in the named emulator.
Does not install/start Pocket, derive keys or access a wallet sandbox.
"""
import hashlib
import json
import os
import shlex
import sqlite3
import subprocess
import uuid
from pathlib import Path
import h02_package as p
from test_package import app_fixture,native_fixture,APK,GENESIS

ROOT=Path(__file__).resolve().parent.parent
ADB=str(Path(os.environ['LOCALAPPDATA'])/'Android/Sdk/platform-tools/adb.exe')
SERIAL='emulator-5580'

def adb(*a):
    r=subprocess.run([ADB,'-s',SERIAL,*a],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
    if r.returncode:
        # This test only handles generated canaries, never a Pocket sandbox.
        print(r.stderr.decode(errors='replace'))
    p.require(r.returncode==0,'synthetic-adb-failed');return r.stdout
def shell(*a):return adb('shell',shlex.join(a))
def helper(action,root,stage,*a):
    b=shell('env','CLASSPATH=/data/local/tmp/h02-helper-test.jar','app_process','/system/bin','h02.H02State',action,root,stage,*a)
    p.require(b.strip()==b'H02_HELPER_OK','synthetic-helper-failed')

def make_source(directory,app):
    (directory/'databases').mkdir(parents=True);(directory/'shared_prefs').mkdir();(directory/'files/data/testnet').mkdir(parents=True)
    schema=json.loads((ROOT/'repos/pocket-node/android/app/schemas/com.rjnr.pocketnode.data.database.AppDatabase/17.json').read_text())['database']
    db=sqlite3.connect(directory/'databases/pocket_node.db')
    for entity in schema['entities']:
        db.execute(entity['createSql'].replace('${TABLE_NAME}',entity['tableName']))
        for index in entity.get('indices',[]):db.execute(index['createSql'].replace('${TABLE_NAME}',entity['tableName']))
    db.execute('CREATE TABLE room_master_table (id INTEGER PRIMARY KEY,identity_hash TEXT)');db.execute('INSERT INTO room_master_table VALUES(42,?)',(p.IDENTITY,));db.execute('PRAGMA user_version=17')
    for w in app['wallets']:
        full=dict(w,name='synthetic account',isActive=int(w['accountIndex']==0),createdAt=123,lastActiveAt=123,colorIndex=0)
        db.execute('INSERT INTO wallets('+','.join(full)+') VALUES('+','.join('?' for _ in full)+')',list(full.values()))
        db.execute('INSERT INTO key_material(walletId,encryptedPrivateKey,encryptedMnemonic,iv,walletType,mnemonicBackedUp,updatedAt,kdfVersion) VALUES(?,?,?,?,?,?,?,?)',(w['walletId'],b'H02_TEST_SECRET_encrypted',None,b'H02_TEST_SECRET_iv','mnemonic',0,123,2))
    for table,rows in [('sync_progress',app['progress']),('sub_account_candidates',app['candidates'])]:
        for row in rows:db.execute('INSERT INTO '+table+'('+','.join(row)+') VALUES('+','.join('?' for _ in row)+')',list(row.values()))
    db.commit();db.close()
    import xml.etree.ElementTree as E
    xml=E.Element('map')
    for k,v in dict(app['prefs'],sync_progress_migrated_to_room_v7=True,unrelated_sensitive_preference='H02_TEST_SECRET_never_export').items():
        if k=='sync_strategy':continue  # Pocket's genuine unset default is ALL_WALLETS.
        t='boolean' if type(v) is bool else 'long' if type(v) is int else 'string'
        e=E.SubElement(xml,t,name=k)
        if t=='string':e.text=v
        else:e.set('value',str(v).lower())
    E.ElementTree(xml).write(directory/'shared_prefs/ckb_wallet_prefs.xml',encoding='utf-8',xml_declaration=True)
    (directory/'shared_prefs/ckb_pin_prefs.xml').write_text('<map><string name="pin_hash">H02_TEST_SECRET_PIN</string></map>')
    native_fixture(directory/'files/data/testnet/store.db',app)

def main():
    p.require(adb('emu','avd','name').decode().splitlines()[0]=='H02_P0_API36_X64','wrong-emulator')
    p.require(shell('getprop','ro.kernel.qemu').strip()==b'1','not-emulator')
    p.require(not shell('pm','list','packages','com.rjnr.pocketnode').strip(),'Pocket-must-not-be-installed')
    token=uuid.uuid4().hex[:16];local=ROOT/'runs/wo2/android-synthetic'/token;local.mkdir(parents=True)
    src=local/'source';app=app_fixture();make_source(src,app)
    # Hold committed WALs open while copying this frozen synthetic file set.
    room_wal=sqlite3.connect(src/'databases/pocket_node.db');room_wal.execute('PRAGMA journal_mode=WAL');room_wal.execute('PRAGMA wal_autocheckpoint=0');room_wal.execute('UPDATE sync_progress SET updatedAt=124');room_wal.commit()
    native_wal=sqlite3.connect(src/'files/data/testnet/store.db');native_wal.execute('PRAGMA journal_mode=WAL');native_wal.execute('PRAGMA wal_autocheckpoint=0')
    native_wal.execute('UPDATE kv SET value=? WHERE substr(key,1,15)=?',((101).to_bytes(8,'big'),b'\xe0FILTER_SCRIPTS'));native_wal.commit()
    remote='/data/local/tmp/h02-synthetic-'+token
    adb('push',str(ROOT/'runs/wo2/helper/helper.jar'),'/data/local/tmp/h02-helper-test.jar');shell('chmod','444','/data/local/tmp/h02-helper-test.jar')
    adb('push',str(src),remote)
    room_wal.close();native_wal.close()
    helper('export',remote,remote+'/files/h02-export-test')
    pkg=local/'package';pkg.mkdir()
    for name in ('app.json','native.sqlite'):adb('pull',remote+'/files/h02-export-test/'+name,str(pkg/name))
    exported=p.read_json(pkg/'app.json');p.validate_app(exported)
    p.require(exported['prefs']['sync_strategy']=='ALL_WALLETS','default-sync-strategy-not-preserved')
    p.require(all(r['updatedAt']==124 for r in exported['progress']),'Room-WAL-not-read')
    p.require(all(h==101 for h in p.inspect_native(pkg/'native.sqlite',GENESIS).values()),'native-WAL-not-read')
    digest=p.seal(pkg,APK,GENESIS,100,'ef'*32,{w['walletId']:10 for w in app['wallets']},'synthetic')
    p.validate(pkg,digest,APK,GENESIS,True)
    # Do not send a synthetic package to Pocket. Test staging only in this
    # synthetic directory with non-signing canaries and the same helper binary.
    plan={'format':p.FORMAT,'destinationScripts':p.validate_app(exported),'progress':exported['progress'],'candidates':exported['candidates'],'prefs':exported['prefs'],'nativeSha256':p.sha(pkg/'native.sqlite')}
    stage=remote+'/files/h02-stage-'+token;shell('mkdir',stage)
    (local/'plan.json').write_bytes(p.encode(plan))
    adb('push',str(local/'plan.json'),stage+'/plan.json');adb('push',str(pkg/'app.json'),stage+'/destination.json');adb('push',str(pkg/'native.sqlite'),stage+'/native.sqlite')
    helper('stage',remote,stage,p.sha(local/'plan.json'))
    # Synthetic activation only; production transport is not invoked in WO-2.
    helper('commit',remote,stage)
    # Failure after the first rename must leave a journal and permit rollback.
    stage2=remote+'/files/h02-stage-'+uuid.uuid4().hex[:16];shell('mkdir',stage2)
    for name,source in [('plan.json',local/'plan.json'),('destination.json',pkg/'app.json'),('native.sqlite',pkg/'native.sqlite')]:adb('push',str(source),stage2+'/'+name)
    helper('stage',remote,stage2,p.sha(local/'plan.json'))
    # Stale stage must refuse before journaling or replacing destination data.
    prefs_path=remote+'/shared_prefs/ckb_wallet_prefs.xml'
    baseline_prefs=shell('cat',prefs_path)
    changed=local/'changed-prefs.xml';changed.write_bytes(baseline_prefs+b'\n')
    adb('push',str(changed),prefs_path)
    try:helper('commit',remote,stage2)
    except p.Refused:pass
    else:raise AssertionError('changed destination was overwritten')
    shell('test','!','-e',remote+'/files/h02-restore-journal.json')
    changed.write_bytes(baseline_prefs);adb('push',str(changed),prefs_path)
    try:helper('commit-interrupt',remote,stage2)
    except p.Refused:pass
    else:raise AssertionError('synthetic interruption did not fail')
    shell('test','-f',remote+'/files/h02-restore-journal.json')
    helper('rollback',remote,stage2)
    shell('test','!','-e',remote+'/files/h02-restore-journal.json')
    result=local/'destination-room.db';adb('pull',remote+'/databases/pocket_node.db',str(result))
    with sqlite3.connect(result) as db:
        p.require(db.execute('SELECT count(*) FROM key_material WHERE encryptedPrivateKey=?',(b'H02_TEST_SECRET_encrypted',)).fetchone()[0]==2,'destination-secrets-changed')
    pin=shell('cat',remote+'/shared_prefs/ckb_pin_prefs.xml');p.require(b'H02_TEST_SECRET_PIN' in pin,'pin-changed')
    p.require(b'H02_TEST_SECRET' not in (pkg/'app.json').read_bytes(),'source-secret-leaked')
    report={'synthetic_only':True,'Pocket_installed':False,'export_policy':'PASS','manifest_digest':digest,'stage_commit':'PASS','WAL_reads':'PASS','changed_destination_refusal':'PASS','interrupted_activation_rollback':'PASS','destination_key_canaries_unchanged':True,'package_secret_exclusion':'PASS'}
    (local/'result.json').write_bytes(p.encode(report));print(json.dumps(report,indent=2))

if __name__=='__main__':main()
