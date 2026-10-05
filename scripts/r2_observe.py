"""Frozen, non-secret B1 observation; not a candidate backup or a recovery claim."""
import argparse,datetime,hashlib,json,sqlite3,struct,time,uuid
from pathlib import Path
import h02_device as transport
import h02_package as p
APK='903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f'
GENESIS='10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
ARGS='bc5882c4309431ee23ad7bbad4b5c3325539eebd'
SCRIPT={'code_hash':'0x'+p.CODE_HASH,'hash_type':'type','args':'0x'+ARGS}

def table(b):
    p.require(len(b)>=4 and int.from_bytes(b[:4],'little')==len(b),'molecule-size')
    if len(b)==4:return []
    first=int.from_bytes(b[4:8],'little');p.require(first>=8 and first%4==0 and first<=len(b),'molecule-offset')
    offsets=list(struct.unpack('<'+'I'*(first//4-1),b[4:first]))+[len(b)]
    p.require(offsets==sorted(offsets),'molecule-order')
    return [b[a:z] for a,z in zip(offsets,offsets[1:])]

def native(path):
    db=sqlite3.connect(path.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:data=dict(db.execute('SELECT key,value FROM kv'))
    finally:db.close()
    p.require(data[b'\xe0GENESIS_BLOCK'][:32].hex()==GENESIS,'wrong-native-network')
    raw_script=bytes.fromhex(p.CODE_HASH+'01'+ARGS);live=[];history=set();regs={};counts={}
    for k,v in data.items():
        counts[k[0]]=counts.get(k[0],0)+1
        if k.startswith(b'\xe0FILTER_SCRIPTS'):regs[k[len(b'\xe0FILTER_SCRIPTS'):-1].hex()+':'+str(k[-1])]=int.from_bytes(v,'big')
        if k.startswith(b'\x60'+raw_script):history.add('0x'+v.hex())
        if not k.startswith(b'\x20'+raw_script):continue
        p.require(len(k)==70 and len(v)==32,'live-index-shape')
        height=int.from_bytes(k[-16:-8],'big');tx_index=int.from_bytes(k[-8:-4],'big');index=int.from_bytes(k[-4:],'big')
        txdata=data[b'\0'+v];p.require(int.from_bytes(txdata[:8],'big')==height and int.from_bytes(txdata[8:12],'big')==tx_index,'transaction-index-mismatch')
        raw=table(txdata[12:])[0]
        p.require(hashlib.blake2b(raw,digest_size=32,person=b'ckb-default-hash').digest()==v,'transaction-hash')
        fields=table(raw);output=table(table(fields[4])[index]);capacity=int.from_bytes(output[0],'little')
        lock=table(output[1]);p.require(lock[0]+lock[1]+lock[2][4:]==raw_script,'live-script')
        payload=table(fields[5])[index];p.require(int.from_bytes(payload[:4],'little')==len(payload)-4,'output-data-size')
        live.append({'txHash':'0x'+v.hex(),'index':index,'capacity':capacity,'blockNumber':height,'type':None if not output[2] else output[2].hex(),'data':'0x'+payload[4:].hex()})
    state=data[b'\xe0LAST_STATE'];header=state[32:]
    p.require(len(header)==208,'header-size')
    return {'script':SCRIPT,'liveCells':sorted(live,key=lambda c:(c['txHash'],c['index'])),'capacity':sum(c['capacity'] for c in live),'transactions':sorted(history),'registrations':regs,'verifiedTip':int.from_bytes(header[16:24],'little'),'verifiedTipHash':'0x'+hashlib.blake2b(header,digest_size=32,person=b'ckb-default-hash').hexdigest(),'minFiltered':int.from_bytes(data[b'\xe0MIN_FILTERED_NUMBER'],'little'),'keyFamilyCounts':counts,'matchedWorkRows':sum(k.startswith(b'\xe0MATCHED_BLOCKS') for k in data)}

def capture(label):
    out=transport.run_dir(transport.ROOT/'runs/wo3b1-r2'/label)
    d=transport.Device('emulator-5580',APK);d.freeze()
    transport.HELPER=transport.ROOT/'runs/wo3b1-r2/state-helper/helper.jar';d.deploy()
    remote=transport.REMOTE_ROOT+'/files/h02-inspect-'+uuid.uuid4().hex[:16]
    d.helper('observe-b1',remote)
    for name in ('app.json','native.sqlite','public.json'):
        raw=d.get(remote+'/'+name)
        if name!='native.sqlite':p.secret_gate(raw)
        (out/name).write_bytes(raw)
    app=p.read_json(out/'app.json');scripts=p.validate_app(app,destination=True,profile=p.B1_FORMAT)
    n=native(out/'native.sqlite');n['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();n['wallets']=app['wallets'];n['progress']=app['progress'];n['prefs']=app['prefs'];n['room']=p.read_json(out/'public.json')
    p.require(all(s+':0' in n['registrations'] for s in scripts.values()),'missing-primary-registration')
    n['discoveryCandidateCount']=len(app['candidates']);n['discoveryStates']=sorted(set(c['state'] for c in app['candidates']))
    (out/'summary.json').write_bytes(p.encode(n));print(json.dumps({k:v for k,v in n.items() if k not in ('registrations','prefs','wallets','room')},indent=2))
    print('OBSERVATION_ONLY; Pocket remains disabled')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('label');v=a.parse_args()
    try:capture(v.label)
    except Exception as e:print('OBSERVATION_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''));raise SystemExit(2)
