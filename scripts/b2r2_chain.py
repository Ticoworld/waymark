"""Public TESTNET oracle and molecule codecs. Never reads wallet credentials."""
import argparse,datetime,hashlib,json,struct
from pathlib import Path
from p3_public_chain import rpc,pages
from h02_device import ROOT
from h02_package import CODE_HASH,require,encode
URL='https://testnet.ckb.dev'
GENESIS='0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606'
ARGS=['bc5882c4309431ee23ad7bbad4b5c3325539eebd','2da024570462b0e2421d87abcbfebd4567d52ad5']
SCRIPTS=[{'code_hash':'0x'+CODE_HASH,'hash_type':'type','args':'0x'+a} for a in ARGS]
DAO='0x82d76d1b75fe2fd9a27dfbaa65a039221a380d76c926f378d3f81cf3e7e13f2e'
def unhex(s):return bytes.fromhex(s.removeprefix('0x'))
def u32(n):return struct.pack('<I',n)
def u64(n):return struct.pack('<Q',n)
def blob(b):return u32(len(b))+b
def table(fields):
 offset=4*(len(fields)+1);offsets=[]
 for f in fields:offsets.append(offset);offset+=len(f)
 return u32(offset)+b''.join(u32(x) for x in offsets)+b''.join(fields)
def fixed(items):return u32(len(items))+b''.join(items)
def script(s):return table([unhex(s['code_hash']),bytes([{'data':0,'type':1,'data1':2,'data2':4}[s['hash_type']]]),blob(unhex(s['args']))])
def outpoint(s):return unhex(s['tx_hash'])+u32(int(s['index'],16))
def raw_tx(tx):
 return table([u32(int(tx['version'],16)),fixed([outpoint(x['out_point'])+bytes([x['dep_type']=='dep_group']) for x in tx['cell_deps']]),fixed([unhex(h) for h in tx['header_deps']]),fixed([u64(int(x['since'],16))+outpoint(x['previous_output']) for x in tx['inputs']]),table([table([u64(int(x['capacity'],16)),script(x['lock']),b'' if x['type'] is None else script(x['type'])]) for x in tx['outputs']]),table([blob(unhex(x)) for x in tx['outputs_data']])])
def ckb_hash(b):return hashlib.blake2b(b,digest_size=32,person=b'ckb-default-hash').digest()
def collect(label):
 out=ROOT/'runs/wo3b2'/label
 require(not out.exists(),'oracle-path-exists')
 require(rpc(URL,'get_block_hash',['0x0'])==GENESIS,'wrong-network')
 before=rpc(URL,'get_tip_header',[]);accounts=[]
 for i,s in enumerate(SCRIPTS):
  cells=pages(URL,'get_cells',s);matches=pages(URL,'get_transactions',s)
  hashes=sorted(set(t['tx_hash'] for t in matches));details={h:rpc(URL,'get_transaction',[h]) for h in hashes}
  headers={d['tx_status']['block_hash']:rpc(URL,'get_header',[d['tx_status']['block_hash']]) for d in details.values()}
  for h,d in details.items():
   require(d['tx_status']['status']=='committed','unconfirmed-fixture')
   require('0x'+ckb_hash(raw_tx(d['transaction'])).hex()==h,'canonical-transaction-serialization')
   require(rpc(URL,'get_block_hash',[headers[d['tx_status']['block_hash']]['number']])==d['tx_status']['block_hash'],'noncanonical-fixture')
  statuses=[{'outPoint':c['out_point'],'status':rpc(URL,'get_live_cell',[c['out_point'],False])['status']} for c in cells]
  require(all(x['status']=='live' for x in statuses),'cell-not-live')
  again=pages(URL,'get_cells',s);require(cells==again,'oracle-changed')
  accounts.append({'index':i,'script':s,'liveCells':cells,'transactions':hashes,'transactionMatches':matches,'transactionDetails':details,'headers':headers,'liveStatuses':statuses,'capacity':sum(int(c['output']['capacity'],16) for c in cells),'plainCapacity':sum(int(c['output']['capacity'],16) for c in cells if c['output']['type'] is None and c['output_data']=='0x')})
 tip=rpc(URL,'get_tip_header',[]);indexer=rpc(URL,'get_indexer_tip',[])
 result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'network':'TESTNET','genesis':GENESIS,'tipBefore':before,'tip':tip,'indexerTip':indexer,'accounts':accounts}
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('xb') as f:f.write(encode(result))
 print(json.dumps({'tip':int(tip['number'],16),'accounts':[{'index':a['index'],'liveCells':len(a['liveCells']),'transactions':len(a['transactions']),'capacity':a['capacity'],'plainCapacity':a['plainCapacity']} for a in accounts]}))
 return result
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('label');v=a.parse_args();collect(v.label)
