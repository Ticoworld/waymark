"""Bounded public TESTNET confirmation receipt. No transaction construction or keys."""
import argparse,datetime,json,time
from b2r2_chain import *
def confirm(txhash,label):
    out=ROOT/'runs/wo3b2/chain-events'/label/'confirmation.json';require(not out.exists(),'confirmation-exists')
    require(len(txhash)==66 and txhash.startswith('0x'),'txhash')
    began=time.monotonic()
    while time.monotonic()-began<300:
        obj=rpc(URL,'get_transaction',[txhash])
        if obj and obj['tx_status']['status']=='committed':break
        if obj and obj['tx_status']['status']=='rejected':raise ValueError('transaction-rejected')
        print('Waiting for TESTNET confirmation',flush=True);time.sleep(10)
    else:raise ValueError('confirmation-timeout')
    header=rpc(URL,'get_header',[obj['tx_status']['block_hash']]);require(rpc(URL,'get_block_hash',[header['number']])==header['hash'],'noncanonical')
    require('0x'+ckb_hash(raw_tx(obj['transaction'])).hex()==txhash,'tx-serialization')
    result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'txHash':txhash,'transaction':obj,'header':header,'inputStatuses':[{'outPoint':i['previous_output'],'status':rpc(URL,'get_live_cell',[i['previous_output'],False])['status']} for i in obj['transaction']['inputs']]}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(encode(result))
    print(json.dumps({'txHash':txhash,'height':int(header['number'],16),'headerHash':header['hash'],'epoch':header['epoch'],'inputStatuses':result['inputStatuses']}))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('txhash');a.add_argument('label');v=a.parse_args();confirm(v.txhash,v.label)
