"""Strict, test-only Pocket 1.8.5 package policy. No wallet secrets or cloud APIs.

Native snapshots are trusted-self inputs, not proofs of historical completeness.
TESTNET only: legacy two-account policy and explicit single-parent policy.
"""
import argparse
import hashlib
import json
import re
import sqlite3
import struct
import uuid
from pathlib import Path
from functools import lru_cache

PIN = 'b28979de744798ffb75367b031d4871ec3af1a12'
LC_TREE = '3ac3e0ce1f4e46897d188b76c5b841b9097fa506'
IDENTITY = '091b40f9618fee3fc8032ff01255a9a4'
CODE_HASH = '9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8'
FORMAT = 'h02-p0-v1'
SINGLE_ACCOUNT_FORMAT = 'h02-p0-b1-one-account-v1'
MEMBERS = {'manifest.json', 'app.json', 'native.sqlite'}
WALLET = {'walletId','type','derivationPath','parentWalletId','accountIndex','mainnetAddress','testnetAddress'}
PROGRESS = {'walletId','network','lightStartBlockNumber','localSavedBlockNumber','updatedAt'}
CANDIDATE = {'parentWalletId','derivationPath','accountIndex','scriptArgs','state','createdAt','registeredFromBlock'}
PREF_SUFFIXES = {'sync_mode','custom_block_height','initial_sync_completed','zero_cell_rescan_done','gap_limit_signal','gap_limit_banner_dismissed'}
BOOL_PREFS = {'initial_sync_completed','zero_cell_rescan_done','gap_limit_signal','gap_limit_banner_dismissed'}
APP_KEYS = {'schema','identity','wallets','progress','candidates','prefs','migrationReady','pendingFree','keysPresent'}
MANIFEST_KEYS = {'format','kind','pocketCommit','lcTree','versionName','versionCode','roomSchema','roomIdentity','apkSha256','network','genesis','boundary','boundaryHash','coverage','scripts','files','abi','nativeSchema','nativeProgress','captureMethod','omissions'}
NATIVE_SCHEMA = {'backend':'sqlite-kv','userVersion':0,'columns':['key BLOB PRIMARY KEY','value BLOB']}
CAPTURE_METHOD = 'force-stop-disable-logical-snapshot'
OMISSIONS = ['source-key-material','source-security-state','peer-identity','pending-actions','transaction-balance-header-dao-caches','contacts-and-freeform-metadata']

class Refused(ValueError):
    pass

def require(ok, code):
    if not ok:
        raise Refused(code)  # Never interpolate wallet data into error text.

def keys(obj, expected):
    require(type(obj) is dict and set(obj) == expected, 'unexpected-fields')

def integer(x, minimum=0):
    require(type(x) is int and minimum <= x < 2**63, 'invalid-integer')

def hx(x, size):
    require(type(x) is str and re.fullmatch('[0-9a-f]{%d}' % (size*2),x), 'invalid-hex')
    return bytes.fromhex(x)

def ident(x):
    require(type(x) is str and str(uuid.UUID(x)) == x, 'invalid-id')

def unique_object(pairs):
    out = {}
    for k,v in pairs:
        require(k not in out, 'duplicate-json-key')
        out[k] = v
    return out

def read_json(path):
    require(path.stat().st_size <= 8*1024*1024, 'json-size-limit')
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)

def encode(obj):
    return (json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n').encode()

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

@lru_cache(maxsize=1)
def dictionary():
    return set((Path(__file__).with_name('bip39-english.txt')).read_text().split())

def secret_gate(data):
    low=data.lower()
    forbidden = [b'key_material',b'encryptedprivatekey',b'encryptedmnemonic',b'key_backups',b'ckb_pin_prefs',b'pin_hash',b'pin_salt',b'pinbackup',b'androidkeystore',b'private_key',b'privatekey',b'"mnemonic":',b'"seed":',b'h02_test_secret',b'wallet_state_test_secret',b'-----begin private key',b'-----begin ec private key',b'-----begin rsa private key']
    require(not any(x in low for x in forbidden), 'known-secret-structure')
    require(b'PNBK' not in data and b'\xfe\xed\xfe\xed' not in data and b'\xce\xce\xce\xce' not in data, 'key-backup-or-keystore-magic')
    require(not re.search(rb'\b(?:xprv|tprv)[1-9A-HJ-NP-Za-km-z]{80,110}\b',data), 'extended-private-key')
    # Public, pinned BIP39 dictionary; reject any 12 consecutive dictionary words.
    words=dictionary()
    streak=0
    for w in re.findall(r'[a-z]+',data.decode('utf-8',errors='ignore').lower()):
        streak=streak+1 if w in words else 0
        require(streak<12, 'mnemonic-word-sequence')

def script_from_address(address, network):
    require(type(address) is str and address == address.lower(), 'address-case')
    pos=address.rfind('1'); hrp=address[:pos]
    require(hrp == ('ckt' if network=='TESTNET' else 'ckb'), 'address-network')
    alphabet='qpzry9x8gf2tvdw0s3jn54khce6mua7l'
    try: values=[alphabet.index(c) for c in address[pos+1:]]
    except ValueError: raise Refused('address-alphabet')
    require(len(values)>=6, 'address-short')
    polymod=1
    for v in [ord(x)>>5 for x in hrp]+[0]+[ord(x)&31 for x in hrp]+values:
        top=polymod>>25;polymod=((polymod&0x1ffffff)<<5)^v
        for i,g in enumerate([0x3b6a57b2,0x26508e6d,0x1ea119fa,0x3d4233dd,0x2a1462b3]):
            if (top>>i)&1: polymod ^= g
    require(polymod in (1,0x2bc830a3), 'address-checksum')
    acc=bits=0;out=[]
    for v in values[:-6]:
        acc=(acc<<5)|v;bits+=5
        if bits>=8: bits-=8;out.append((acc>>bits)&255)
    require(bits<5 and ((acc<<(8-bits))&255)==0, 'address-padding')
    b=bytes(out)
    if len(b)==22 and b[:2]==b'\x01\x00' and polymod==1:
        code=bytes.fromhex(CODE_HASH);typ=1;args=b[2:]
    else:
        require(len(b)==54 and b[0]==0 and polymod==0x2bc830a3, 'unsupported-address')
        code=b[1:33];typ=b[33];args=b[34:]
    require(code.hex()==CODE_HASH and typ==1 and len(args)==20, 'unsupported-script')
    return (struct.pack('<IIII',73,16,48,49)+code+bytes([typ])+struct.pack('<I',20)+args).hex()

def validate_app(app, destination=False, profile=FORMAT):
    require(profile in (FORMAT,SINGLE_ACCOUNT_FORMAT),'unsupported-profile')
    count=1 if profile==SINGLE_ACCOUNT_FORMAT else 2
    keys(app, APP_KEYS)
    require(app['schema']==17 and app['identity']==IDENTITY,'room-version')
    require(app['migrationReady'] is True and app['pendingFree'] is True and app['keysPresent'] is True,'source-not-settled-or-keys-missing')
    require(type(app['wallets']) is list and len(app['wallets'])==count, 'account-count-profile')
    ids=set();scripts={}; parent=None
    for w in app['wallets']:
        keys(w,WALLET);ident(w['walletId']);require(w['walletId'] not in ids,'duplicate-wallet');ids.add(w['walletId'])
        require(w['type']=='mnemonic' and type(w['accountIndex']) is int and w['accountIndex'] in range(count),'account-profile')
        require(w['derivationPath']=="m/44'/309'/%d'/0/0"%w['accountIndex'],'account-path')
        if w['accountIndex']==0:
            require(w['parentWalletId'] is None and parent is None,'parent-map');parent=w['walletId']
        scripts[w['walletId']]=script_from_address(w['testnetAddress'],'TESTNET')
        require(scripts[w['walletId']]==script_from_address(w['mainnetAddress'],'MAINNET'),'address-script-mismatch')
    require(parent is not None and len(set(scripts.values()))==count,'identity-collision')
    for w in app['wallets']:
        if w['accountIndex']==1: require(w['parentWalletId']==parent,'child-map')
    require(type(app['progress']) is list,'progress-type')
    seen=set()
    for r in app['progress']:
        keys(r,PROGRESS);require(r['walletId'] in ids and r['network']=='TESTNET' and r['walletId'] not in seen,'progress-map');seen.add(r['walletId'])
        for k in ('lightStartBlockNumber','localSavedBlockNumber','updatedAt'): integer(r[k])
        if not destination: require(r['lightStartBlockNumber']<=r['localSavedBlockNumber'],'progress-inconsistent')
    if not destination: require(seen==ids,'missing-progress')
    seen=set()
    require(type(app['candidates']) is list and len(app['candidates'])<=500,'candidate-limit')
    for r in app['candidates']:
        keys(r,CANDIDATE);require(r['parentWalletId']==parent,'candidate-parent')
        require(re.fullmatch(r"m/44'/309'/\d+'/[01]/\d+",r['derivationPath']) is not None,'candidate-path')
        require(r['derivationPath'] not in seen,'duplicate-candidate');seen.add(r['derivationPath'])
        require(r['state'] in ('PENDING','FOUND','RESTORED','EMPTY'),'candidate-state')
        if profile==SINGLE_ACCOUNT_FORMAT: require(r['state'] in ('PENDING','EMPTY'),'single-account-no-additional-populated-account')
        hx(r['scriptArgs'].removeprefix('0x'),20)
        for k in ('accountIndex','createdAt','registeredFromBlock'): integer(r[k])
    require(type(app['prefs']) is dict,'preferences-type')
    allowed={'selected_network','sync_strategy','active_wallet_id'}|{f'{i}_testnet_{s}' for i in ids for s in PREF_SUFFIXES}
    require(set(app['prefs'])<=allowed,'preference-not-allowed')
    require(app['prefs'].get('selected_network')=='TESTNET' and app['prefs'].get('sync_strategy')=='ALL_WALLETS' and app['prefs'].get('active_wallet_id') in ids,'preference-profile')
    for i in ids:
        require(app['prefs'].get(i+'_testnet_sync_mode') in ('FULL_HISTORY','CUSTOM','RECENT'),'coverage-mode')
    for k,v in app['prefs'].items():
        if k.endswith('_custom_block_height'): require(type(v) is int and -1<=v<2**63,'custom-height')
        if any(k.endswith('_'+s) for s in BOOL_PREFS): require(type(v) is bool,'boolean-preference')
    secret_gate(encode(app))
    return scripts

def inspect_native(path, genesis, require_funded=False):
    require(path.is_file() and not path.is_symlink(),'native-file')
    db=sqlite3.connect(path.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        require(db.execute('PRAGMA integrity_check').fetchall()==[('ok',)],'native-integrity')
        require(db.execute('PRAGMA user_version').fetchone()[0]==0,'native-version')
        objects=db.execute("SELECT type,name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").fetchall()
        require(objects==[('table','kv')],'native-schema-objects')
        require([(r[1],r[2].upper(),r[5]) for r in db.execute('PRAGMA table_info(kv)')]==[('key','BLOB',1),('value','BLOB',0)],'native-columns')
        require(db.execute('PRAGMA freelist_count').fetchone()[0]==0,'native-free-pages')
        require(db.execute('PRAGMA page_count').fetchone()[0]*db.execute('PRAGMA page_size').fetchone()[0]==path.stat().st_size,'native-trailing-data')
        regs={};meta={};count=0;counts={}
        for k,v in db.execute('SELECT key,value FROM kv'):
            require(type(k) is bytes and type(v) is bytes and k and (v or k==b'\xe0LAST_N_HEADERS'),'native-row-type')
            secret_gate(k+v);count+=1
            p=k[0]
            counts[p]=counts.get(p,0)+1
            require(p in (0,32,64,96,128,160,192,208,224),'native-key-family')
            if p in (0,160): require(len(k)==33,'native-key-size')
            if p in (192,208): require(len(k)==(9 if p==192 else 5) and len(v)==32,'native-number-key')
            if p in (32,64,96,128): require(len(k)>54 and len(v)==32,'native-script-index')
            if p==224:
                tail=k[1:]
                if tail.startswith(b'FILTER_SCRIPTS'):
                    script=tail[14:-1]
                    require(len(script)>=53 and len(v)==8 and tail[-1] in (0,1),'registration-shape')
                    require(struct.unpack('<I',script[:4])[0]==len(script),'packed-script-size')
                    regs[script.hex()+':'+str(tail[-1])]=int.from_bytes(v,'big')
                elif tail.startswith(b'MATCHED_BLOCKS'):
                    require(len(tail)==len(b'MATCHED_BLOCKS')+8,'matched-work-key')
                else:
                    require(tail in (b'GENESIS_BLOCK',b'LAST_STATE',b'LAST_N_HEADERS',b'MAX_CHECK_POINT_INDEX',b'MIN_FILTERED_NUMBER'),'unknown-native-metadata')
                    meta[tail]=v
        require(count>0 and meta.get(b'GENESIS_BLOCK',b'')[:32]==hx(genesis,32),'native-genesis')
        require(len(meta.get(b'LAST_STATE',b''))==240 and len(meta.get(b'MIN_FILTERED_NUMBER',b''))==8,'native-required-state')
        require(b'LAST_N_HEADERS' in meta and len(meta.get(b'MAX_CHECK_POINT_INDEX',b''))==4,'native-checkpoints')
        require(len(meta[b'LAST_N_HEADERS'])%40==0,'native-last-headers-shape')
        if require_funded:
            require(counts.get(0,0)>0 and counts.get(160,0)>0 and counts.get(32,0)>=2 and counts.get(96,0)>=2,'missing-funded-fixture-state')
        # Also scan unused bytes; the fresh logical snapshot should not carry
        # freelist/slack residue from an arbitrary input database.
        with path.open('rb') as stream:
            tail=b''
            for part in iter(lambda:stream.read(1024*1024),b''):
                secret_gate(tail+part);tail=part[-512:]
        return regs
    finally: db.close()

def validate(package, trusted_digest, apk_hash, genesis, allow_synthetic=False):
    package=Path(package)
    require(package.is_dir() and not package.is_symlink(),'package-directory')
    require({p.name for p in package.iterdir()}==MEMBERS,'package-members')
    for p in package.iterdir(): require(p.is_file() and not p.is_symlink(),'unsafe-member')
    require(sha(package/'manifest.json')==trusted_digest,'manifest-trust-digest')
    m=read_json(package/'manifest.json');keys(m,MANIFEST_KEYS);secret_gate(encode(m))
    require(m['format'] in (FORMAT,SINGLE_ACCOUNT_FORMAT) and m['pocketCommit']==PIN and m['lcTree']==LC_TREE and m['versionName']=='1.8.5' and m['versionCode']==27 and m['roomSchema']==17 and m['roomIdentity']==IDENTITY,'unsupported-version')
    require(m['abi']=='x86_64' and m['nativeSchema']==NATIVE_SCHEMA and m['captureMethod']==CAPTURE_METHOD and m['omissions']==OMISSIONS,'unsupported-capture-profile')
    require(m['kind']=='candidate' or (allow_synthetic and m['kind']=='synthetic'),'synthetic-not-restorable')
    require(m['network']=='TESTNET' and m['genesis']==genesis,'wrong-network')
    hx(apk_hash,32);hx(genesis,32);require(m['apkSha256']==apk_hash,'apk-mismatch')
    integer(m['boundary']);hx(m['boundaryHash'],32)
    keys(m['files'],{'app.json','native.sqlite'})
    for name,entry in m['files'].items():
        keys(entry,{'bytes','sha256'});integer(entry['bytes'],1);hx(entry['sha256'],32)
        require((package/name).stat().st_size==entry['bytes'] and sha(package/name)==entry['sha256'],'member-hash')
    app=read_json(package/'app.json');scripts=validate_app(app,profile=m['format'])
    require(m['scripts']==scripts,'manifest-script-mismatch')
    keys(m['coverage'],set(scripts))
    regs=inspect_native(package/'native.sqlite',genesis,m['kind']=='candidate')
    require(m['nativeProgress']==regs,'native-progress-manifest')
    if m['format']==SINGLE_ACCOUNT_FORMAT:
        allowed={s+':0' for s in scripts.values()}
        for c in app['candidates']:
            packed=struct.pack('<IIII',73,16,48,49)+bytes.fromhex(CODE_HASH)+b'\x01'+struct.pack('<I',20)+hx(c['scriptArgs'].removeprefix('0x'),20)
            allowed.add(packed.hex()+':0')
        require(set(regs)<=allowed,'unknown-single-account-registration')
    for row in app['progress']:
        wid=row['walletId'];start=m['coverage'][wid];integer(start)
        require(start<=m['boundary']<=row['localSavedBlockNumber']<=regs.get(scripts[wid]+':0',-1),'incomplete-native-progress')
    return m,app

def seal(package, apk_hash, genesis, boundary, boundary_hash, coverage, kind='candidate', profile=FORMAT):
    package=Path(package)
    require({p.name for p in package.iterdir()}=={'app.json','native.sqlite'},'unapproved-extraction-members')
    app=read_json(package/'app.json');scripts=validate_app(app,profile=profile)
    m=dict(format=profile,kind=kind,pocketCommit=PIN,lcTree=LC_TREE,versionName='1.8.5',versionCode=27,roomSchema=17,roomIdentity=IDENTITY,apkSha256=apk_hash,network='TESTNET',genesis=genesis,boundary=boundary,boundaryHash=boundary_hash,coverage=coverage,scripts=scripts,files={n:{'bytes':(package/n).stat().st_size,'sha256':sha(package/n)} for n in ('app.json','native.sqlite')})
    m.update(abi='x86_64',nativeSchema=NATIVE_SCHEMA,nativeProgress=inspect_native(package/'native.sqlite',genesis,kind=='candidate'),captureMethod=CAPTURE_METHOD,omissions=OMISSIONS)
    # Create exclusively; a failed gate leaves an untrusted package, never a success receipt.
    with (package/'manifest.json').open('xb') as f:f.write(encode(m))
    digest=sha(package/'manifest.json')
    validate(package,digest,apk_hash,genesis,kind=='synthetic')
    return digest

def restore_plan(package, digest, apk_hash, genesis, destination):
    m,app=validate(package,digest,apk_hash,genesis)
    dst_scripts=validate_app(destination,destination=True,profile=m['format'])
    src_scripts=m['scripts'];mapping={}
    for sw in app['wallets']:
        matches=[dw for dw in destination['wallets'] if dst_scripts[dw['walletId']]==src_scripts[sw['walletId']] and dw['derivationPath']==sw['derivationPath'] and dw['accountIndex']==sw['accountIndex']]
        require(len(matches)==1,'destination-identity-mismatch');mapping[sw['walletId']]=matches[0]['walletId']
    dst_candidates={(c['parentWalletId'],c['derivationPath']):c for c in destination['candidates']}
    for c in app['candidates']:
        other=dst_candidates.get((mapping[c['parentWalletId']],c['derivationPath']))
        require(other is not None and other['accountIndex']==c['accountIndex'] and other['scriptArgs'].removeprefix('0x')==c['scriptArgs'].removeprefix('0x'),'destination-candidate-mismatch')
    progress=[dict(r,walletId=mapping[r['walletId']]) for r in app['progress']]
    candidates=[dict(r,parentWalletId=mapping[r['parentWalletId']]) for r in app['candidates']]
    prefs={}
    for k,v in app['prefs'].items():
        if k=='active_wallet_id': v=mapping[v]
        for old,new in mapping.items():
            if k.startswith(old+'_'): k=new+k[len(old):];break
        prefs[k]=v
    return {'format':m['format'],'destinationScripts':dst_scripts,'progress':progress,'candidates':candidates,'prefs':prefs,'nativeSha256':m['files']['native.sqlite']['sha256']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('package',type=Path);p.add_argument('--trust',required=True);p.add_argument('--apk-sha256',required=True);p.add_argument('--genesis',required=True);p.add_argument('--allow-synthetic',action='store_true')
    a=p.parse_args();validate(a.package,a.trust,a.apk_sha256,a.genesis,a.allow_synthetic);print('PACKAGE_POLICY_PASS (not wallet recovery)')

if __name__=='__main__':
    try: main()
    except (Refused,ValueError,KeyError,TypeError,OSError,sqlite3.Error):
        print('PACKAGE_REFUSED');raise SystemExit(2)
