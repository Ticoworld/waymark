"""Independent public TESTNET observation for the fixed primary Script. No signing."""
import argparse,datetime,json,re
from pathlib import Path
from p3_public_chain import rpc,pages
from h02_device import ROOT
from r2_observe import SCRIPT,GENESIS
URL='https://testnet.ckb.dev'

def collect(out,spent=None):
    before=rpc(URL,'get_tip_header',[])
    genesis=rpc(URL,'get_block_hash',['0x0'])
    if genesis!='0x'+GENESIS:raise ValueError()
    cells=pages(URL,'get_cells',SCRIPT);txs=pages(URL,'get_transactions',SCRIPT)
    unique=sorted({t['tx_hash'] for t in txs})
    details={h:rpc(URL,'get_transaction',[h]) for h in unique}
    statuses=[{'outPoint':c['out_point'],'status':rpc(URL,'get_live_cell',[c['out_point'],False])['status']} for c in cells]
    if any(s['status']!='live' for s in statuses):raise ValueError()
    indexer=rpc(URL,'get_indexer_tip',[]);tip=rpc(URL,'get_tip_header',[])
    result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'network':'TESTNET','script':SCRIPT,'genesis':genesis,'tipBefore':before,'tip':tip,'indexerTip':indexer,'liveCells':cells,'transactions':txs,'transactionDetails':details,'liveStatuses':statuses,'capacity':sum(int(c['output']['capacity'],16) for c in cells)}
    if spent:
        m=re.fullmatch(r'(0x[0-9a-f]{64}):(\d+)',spent)
        if not m:raise ValueError()
        op={'tx_hash':m[1],'index':hex(int(m[2]))}
        result['spentU']={'outPoint':op,'result':rpc(URL,'get_live_cell',[op,False])}
    with Path(out).open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps({'network':'TESTNET','tip':int(tip['number'],16),'indexerTip':int(indexer['block_number'],16),'liveCells':len(cells),'transactions':len(unique),'capacity':result['capacity'],'spentUStatus':result.get('spentU',{}).get('result',{}).get('status')}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('--spent');a=p.parse_args()
    collect(a.output,a.spent)
