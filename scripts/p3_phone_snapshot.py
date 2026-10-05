"""WO-3 authorized disposable phone: read-only acquisition into private/ only.
Never prints device file contents. Refuses a running Pocket process or overwrite.
This is fixture-secret custody, NOT the sanitized Candidate B exporter.
"""
import base64, hashlib, json, os, re, shlex, sqlite3, subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ADB = Path(os.environ['LOCALAPPDATA'])/'Android/Sdk/platform-tools/adb.exe'
SERIAL = 'R5CW6127VPR'
APP = 'com.rjnr.pocketnode'
OUT = ROOT/'private/phone-acquisition'

def shell(*args):
    p = subprocess.run([str(ADB), '-s', SERIAL, 'shell', '-T', shlex.join(args)], capture_output=True)
    if p.returncode: raise RuntimeError('ADB_READ_REFUSED')
    return p.stdout

def sandbox(*args): return shell('run-as', APP, *args)

def stopped():
    if APP.encode() in shell('ps', '-A', '-o', 'NAME'): raise RuntimeError('POCKET_RUNNING')

def acquire():
    stopped()
    if shell('getprop','ro.product.model').strip() != b'SM-S9180': raise RuntimeError('WRONG_DEVICE')
    OUT.mkdir()  # exclusive; parent already ACL-restricted
    files=['databases/pocket_node.db','shared_prefs/ckb_wallet_prefs.xml']
    for suffix in ('-wal','-shm'):
        p='databases/pocket_node.db'+suffix
        if sandbox('sh','-c', 'if test -f '+shlex.quote(p)+'; then echo yes; fi').strip()==b'yes': files.append(p)
    for name in sandbox('ls','files/key_backups').decode().splitlines():
        if re.fullmatch(r'[a-zA-Z0-9-]+\.enc',name): files.append('files/key_backups/'+name)
    hashes={p:sandbox('sha256sum',p).decode().split()[0] for p in files}
    for p in files:
        raw=base64.b64decode(b''.join(sandbox('base64',p).split()),validate=True)
        if hashlib.sha256(raw).hexdigest()!=hashes[p]: raise RuntimeError('CAPTURE_CHANGED')
        dest=OUT/p;dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as f:f.write(raw)
    stopped()
    if any(sandbox('sha256sum',p).decode().split()[0]!=h for p,h in hashes.items()): raise RuntimeError('CAPTURE_CHANGED')
    (OUT/'receipt.json').write_text(json.dumps({'serial':SERIAL,'file_sha256':hashes},indent=2))
    print('PRIVATE_ACQUISITION_OK; no app launch or source write')

def public():
    # Private working copy ensures host WAL handling cannot alter acquisition.
    work=ROOT/'private/phone-analysis';work.mkdir(exist_ok=True)
    import shutil
    for p in (OUT/'databases').iterdir():
        target=work/p.name
        if not target.exists(): shutil.copyfile(p,target)
    db=sqlite3.connect((work/'pocket_node.db').as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    result={'serial':SERIAL,'uid':sandbox('id','-u').decode().strip(),'room_schema':db.execute('pragma user_version').fetchone()[0]}
    selections={
      'wallets':'walletId,type,derivationPath,parentWalletId,accountIndex,mainnetAddress,testnetAddress',
      'key_material':'walletId,kdfVersion,walletType,mnemonicBackedUp',
      'sync_progress':'walletId,network,lightStartBlockNumber,localSavedBlockNumber,updatedAt',
      'sub_account_candidates':'parentWalletId,derivationPath,accountIndex,scriptArgs,state,registeredFromBlock',
    }
    for table,cols in selections.items():
        available={r[1] for r in db.execute('pragma table_info('+table+')')}
        selected=[c for c in cols.split(',') if c in available]
        result[table]=[dict(r) for r in db.execute('select '+','.join(selected)+' from '+table)] if selected else []
    result['table_counts']={r[0]:db.execute('select count(*) from "'+r[0]+'"').fetchone()[0] for r in db.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")}
    allowed={'selected_network','sync_strategy','active_wallet_id'}
    for w in result['wallets']:
        for net in ('testnet','mainnet'):
            for s in ('sync_mode','custom_block_height','initial_sync_completed','zero_cell_rescan_done'):
                allowed.add(w['walletId']+'_'+net+'_'+s)
    result['preferences']={e.attrib['name']:e.text if e.tag=='string' else e.attrib.get('value') for e in ET.parse(OUT/'shared_prefs/ckb_wallet_prefs.xml').getroot() if e.attrib.get('name') in allowed}
    result['backup_formats']={p.stem:p.read_bytes()[4] for p in (OUT/'files/key_backups').glob('*.enc') if p.read_bytes()[:4]==b'PNBK'}
    out=ROOT/'runs/wo3-setup';out.mkdir(parents=True,exist_ok=True)
    (out/'phone-public.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2));db.close()

def native():
    stopped();capture=ROOT/'private/native-acquisition';capture.mkdir()
    files=[f'files/data/{net}/store.db{s}' for net in ('testnet','mainnet') for s in ('','-wal','-shm')]
    hashes={p:sandbox('sha256sum',p).decode().split()[0] for p in files}
    for p in files:
        raw=base64.b64decode(b''.join(sandbox('base64',p).split()),validate=True)
        if hashlib.sha256(raw).hexdigest()!=hashes[p]:raise RuntimeError('CAPTURE_CHANGED')
        dest=capture/p;dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as f:f.write(raw)
    stopped()
    if any(sandbox('sha256sum',p).decode().split()[0]!=h for p,h in hashes.items()):raise RuntimeError('CAPTURE_CHANGED')
    (capture/'receipt.json').write_text(json.dumps(hashes,indent=2))
    print('NATIVE_PRIVATE_ACQUISITION_OK; source files unchanged')

def detail():
    import shutil
    result={}
    for net in ('testnet','mainnet'):
        folder=ROOT/'private/native-analysis'/net;folder.mkdir(parents=True,exist_ok=True)
        for p in (ROOT/'private/native-acquisition/files/data'/net).iterdir():
            if not (folder/p.name).exists():shutil.copyfile(p,folder/p.name)
        db=sqlite3.connect((folder/'store.db').as_uri()+'?mode=ro',uri=True)
        counts={};regs=[];txs=[];cells=[];meta={}
        for k,v in db.execute('select key,value from kv'):
            counts[str(k[0])]=counts.get(str(k[0]),0)+1
            if k.startswith(b'\xe0FILTER_SCRIPTS'):
                regs.append({'packedScript':k[15:-1].hex(),'role':k[-1],'progress':int.from_bytes(v,'big')})
            if k[0]==0:txs.append({'tx_hash':'0x'+k[1:].hex(),'block':int.from_bytes(v[:8],'big'),'txIndex':int.from_bytes(v[8:12],'big')})
            if k[0]==32:cells.append({'indexKey':k.hex(),'tx_hash':'0x'+v.hex(),'index':int.from_bytes(k[-4:],'big'),'block':int.from_bytes(k[-16:-8],'big')})
            if k[0]==224 and k[1:] in (b'MIN_FILTERED_NUMBER',b'MAX_CHECK_POINT_INDEX',b'GENESIS_BLOCK'):
                meta[k[1:].decode()]=v[:32].hex() if k[1:]==b'GENESIS_BLOCK' else {'bytes':v.hex(),'value':int.from_bytes(v,'little' if k[1:]==b'MIN_FILTERED_NUMBER' else 'big')}
        result[net]={'prefixCounts':counts,'registrations':regs,'transactions':txs,'liveCellIndex':cells,'metadata':meta};db.close()
    db=sqlite3.connect((ROOT/'private/phone-analysis/pocket_node.db').as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    result['appTransactions']=[dict(r) for r in db.execute('select txHash,blockNumber,blockHash,timestamp,balanceChange,direction,fee,confirmations,network,status,isLocal,walletId from transactions')]
    result['balanceCache']=[dict(r) for r in db.execute('select * from balance_cache')];db.close()
    hist=ROOT.parent/'ckb-script-port/_work/g3-1-pocket-node/_g3-1r1-evidence'
    hd=sqlite3.connect((hist/'pocket-testnet-real-room-source-1.db').as_uri()+'?immutable=1&mode=ro',uri=True);hd.row_factory=sqlite3.Row
    result['historicalD2Wallets']=[dict(r) for r in hd.execute('select walletId,type,derivationPath,parentWalletId,accountIndex,mainnetAddress,testnetAddress from wallets')];hd.close()
    hd=sqlite3.connect((hist/'pocket-testnet-real-pocket-source-1.db').as_uri()+'?immutable=1&mode=ro',uri=True)
    result['historicalD2NativeTransactions']=[{'tx_hash':'0x'+k[1:].hex(),'block':int.from_bytes(v[:8],'big')} for k,v in hd.execute('select key,value from kv') if k[0]==0];hd.close()
    (ROOT/'runs/wo3-setup/phone-chain-public.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':
    import sys
    try:
        {'acquire':acquire,'public':public,'native':native,'detail':detail}[sys.argv[1]]()
    except Exception:
        print('P3_INSPECTION_REFUSED; details deliberately suppressed');raise SystemExit(2)
