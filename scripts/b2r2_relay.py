"""Disposable TESTNET relay only. Never print keys, sign for owned accounts, or accept arbitrary destinations."""
import argparse,csv,datetime,json,subprocess,time
from pathlib import Path
from coincurve import PrivateKey,PublicKey
from b2r2_chain import *
from p3_fixture import address
KEY=ROOT/'private/wo3b2/relay.json'
PUBLIC=ROOT/'runs/wo3b2/relay-public.json'
DEP='0xf8de3bb47d055cdf460d93a2a6e1b05f7432f9777c8c474abf4eec1d4aee5d37'
def create():
 require(not KEY.exists() and not PUBLIC.exists(),'relay-already-created')
 KEY.parent.mkdir(parents=True,exist_ok=True)
 sid=next(csv.reader(subprocess.check_output(['whoami','/user','/fo','csv','/nh'],text=True).splitlines()))[1]
 subprocess.run(['icacls',str(KEY.parent),'/inheritance:r','/grant:r','*'+sid+':(OI)(CI)F','*S-1-5-18:(OI)(CI)F','*S-1-5-32-544:(OI)(CI)F'],capture_output=True,check=True)
 k=PrivateKey();pub=k.public_key.format(compressed=True);s={'code_hash':'0x'+CODE_HASH,'hash_type':'type','args':'0x'+ckb_hash(pub)[:20].hex()}
 public={'purpose':'Independent disposable TESTNET relay; outside owned mnemonic accounts','publicKey':'0x'+pub.hex(),'script':s,'address':address(k.secret,'ckt')}
 with KEY.open('x') as f:json.dump({'privateKey':k.secret.hex(),'network':'TESTNET'},f)
 with PUBLIC.open('xb') as f:f.write(encode(public))
 print(json.dumps(public,indent=2))
def send(label,amount_ckb):
 require(label in ('fund-account1','post-H2-account1'),'unapproved-relay-event')
 require(amount_ckb==(2000 if label=='fund-account1' else 100),'unapproved-amount')
 out=ROOT/'runs/wo3b2/chain-events'/label
 require(not out.exists(),'relay-event-already-attempted')
 require(rpc(URL,'get_block_hash',['0x0'])==GENESIS,'wrong-network')
 public=json.loads(PUBLIC.read_text());key=json.loads(KEY.read_text());require(key['network']=='TESTNET','private-relay-network')
 k=PrivateKey(unhex(key['privateKey']));require(k.public_key.format(compressed=True).hex()==public['publicKey'][2:],'relay-key-mismatch')
 cells=pages(URL,'get_cells',public['script']);amount=amount_ckb*10**8;fee=1000
 good=[c for c in cells if c['output']['type'] is None and c['output_data']=='0x' and int(c['output']['capacity'],16)>=amount+fee+61*10**8]
 require(len(good)==1,'relay-input-not-unambiguous');c=good[0];require(rpc(URL,'get_live_cell',[c['out_point'],False])['status']=='live','relay-input-spent')
 capacity=int(c['output']['capacity'],16)
 tx={'version':'0x0','cell_deps':[{'out_point':{'tx_hash':DEP,'index':'0x0'},'dep_type':'dep_group'}],'header_deps':[],'inputs':[{'since':'0x0','previous_output':c['out_point']}],'outputs':[{'capacity':hex(amount),'lock':SCRIPTS[1],'type':None},{'capacity':hex(capacity-amount-fee),'lock':public['script'],'type':None}],'outputs_data':['0x','0x'],'witnesses':[]}
 h=ckb_hash(raw_tx(tx));empty=table([blob(bytes(65)),b'',b'']);message=ckb_hash(h+u64(len(empty))+empty)
 signature=k.sign_recoverable(message,hasher=None)
 require(PublicKey.from_signature_and_message(signature,message,hasher=None).format(compressed=True)==k.public_key.format(compressed=True),'relay-signature-verification')
 tx['witnesses']=['0x'+table([blob(signature),b'',b'']).hex()]
 require(sum(int(x['capacity'],16) for x in tx['outputs'])+fee==capacity,'capacity-conservation')
 out.mkdir(parents=True)
 # This is public signed transaction material, never a key or mnemonic.
 (out/'signed-transaction.json').write_bytes(encode(tx))
 receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'network':'TESTNET','label':label,'expectedTxHash':'0x'+h.hex(),'input':c['out_point'],'capacity':capacity,'amount':amount,'fee':fee,'destination':SCRIPTS[1],'broadcastAttempted':True}
 (out/'attempt.json').write_bytes(encode(receipt))
 returned=rpc(URL,'send_transaction',[tx,'passthrough']);require(returned==receipt['expectedTxHash'],'broadcast-hash-mismatch')
 receipt['returnedTxHash']=returned;(out/'broadcast.json').write_bytes(encode(receipt));print(json.dumps(receipt,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['create','fund-account1','post-H2-account1']);a=p.parse_args()
 try:
  if a.action=='create':create()
  else:send(a.action,2000 if a.action=='fund-account1' else 100)
 except Exception as e:
  print('RELAY_REFUSED '+type(e).__name__+'; reconcile retained public attempt before any retry');raise SystemExit(2)
