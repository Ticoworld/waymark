"""Independent canonical TESTNET oracle; no wallet secrets, signing or app access."""
import argparse
import datetime
import h02_package as p
from p3c_phone_ui import BASE
from b2r2_chain import URL,GENESIS,SCRIPTS,rpc,pages,ckb_hash,raw_tx

def collect(label):
    out=BASE/('oracle-'+label+'.json')
    p.require(not out.exists(),'oracle-already-recorded')
    p.require(rpc(URL,'get_block_hash',['0x0'])==GENESIS,'wrong-public-network')
    before=rpc(URL,'get_tip_header',[]);accounts=[]
    for index,script in enumerate(SCRIPTS):
        cells=pages(URL,'get_cells',script);matches=pages(URL,'get_transactions',script)
        hashes=sorted(set(t['tx_hash'] for t in matches))
        details={h:rpc(URL,'get_transaction',[h]) for h in hashes}
        headers={d['tx_status']['block_hash']:rpc(URL,'get_header',[d['tx_status']['block_hash']]) for d in details.values()}
        for h,d in details.items():
            p.require(d['tx_status']['status']=='committed','oracle-unconfirmed-transaction')
            p.require('0x'+ckb_hash(raw_tx(d['transaction'])).hex()==h,'public-transaction-hash')
            p.require(rpc(URL,'get_block_hash',[headers[d['tx_status']['block_hash']]['number']])==d['tx_status']['block_hash'],'oracle-noncanonical')
        statuses=[{'outPoint':c['out_point'],'status':rpc(URL,'get_live_cell',[c['out_point'],False])['status']} for c in cells]
        p.require(all(s['status']=='live' for s in statuses),'oracle-live-state')
        p.require(pages(URL,'get_cells',script)==cells,'oracle-changed-during-capture')
        accounts.append({'index':index,'script':script,'liveCells':cells,'transactions':hashes,
            'transactionMatches':matches,'transactionDetails':details,'headers':headers,'liveStatuses':statuses,
            'capacity':sum(int(c['output']['capacity'],16) for c in cells),
            'plainCapacity':sum(int(c['output']['capacity'],16) for c in cells if c['output']['type'] is None and c['output_data']=='0x')})
    tip=rpc(URL,'get_tip_header',[]);indexer=rpc(URL,'get_indexer_tip',[])
    result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'network':'TESTNET','genesis':GENESIS,
            'tipBefore':before,'tip':tip,'indexerTip':indexer,'accounts':accounts}
    with out.open('xb') as f:f.write(p.encode(result))
    print('CANONICAL_PHONE_ORACLE_SAVED '+label+' tip='+str(int(tip['number'],16)),flush=True)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('label');args=parser.parse_args()
    try:collect(args.label)
    except Exception as e:
        print('PHONE_ORACLE_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''))
        raise SystemExit(2)
