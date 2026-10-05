"""Read-only public CKB fixture inventory. No keys, signing or wallet RPCs."""
import datetime, json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/wo3-setup'
ENDPOINTS={'TESTNET':'https://testnet.ckb.dev','MAINNET':'https://mainnet.ckb.dev'}

def rpc(url,method,params):
    req=urllib.request.Request(url,json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(),{'Content-Type':'application/json','User-Agent':'H02-public-fixture-inspector/1'})
    with urllib.request.urlopen(req,timeout=40) as r:obj=json.load(r)
    if 'error' in obj:raise RuntimeError('PUBLIC_RPC_ERROR: '+method)
    return obj['result']

def pages(url,method,script):
    cursor=None;items=[]
    for _ in range(100):
        params=[{'script':script,'script_type':'lock','script_search_mode':'exact'},'asc','0x64']
        if cursor:params.append(cursor)
        page=rpc(url,method,params);items.extend(page['objects'])
        if len(page['objects'])<100:return items
        if page['last_cursor']==cursor:raise RuntimeError('PAGINATION_STALLED')
        cursor=page['last_cursor']
    raise RuntimeError('PAGINATION_LIMIT')

def inspect(net,identity):
    url=ENDPOINTS[net];script=identity['lockScript'];result={'network':net,'endpoint':url,'queriedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script':script}
    result['tipBefore']=rpc(url,'get_tip_header',[])
    result['genesisHash']=rpc(url,'get_block_hash',['0x0'])
    result['indexerTip']=rpc(url,'get_indexer_tip',[])
    result['liveCells']=pages(url,'get_cells',script)
    result['transactionMatches']=pages(url,'get_transactions',script)
    hashes=list(dict.fromkeys(t['tx_hash'] for t in result['transactionMatches']))
    result['transactions']={h:rpc(url,'get_transaction',[h]) for h in hashes}
    blocks=list(dict.fromkeys(t['block_number'] for t in result['transactionMatches']))
    result['activityHeaders']={b:rpc(url,'get_header_by_number',[b]) for b in blocks}
    result['liveCellStatus']=[{'outPoint':c['out_point'],'result':rpc(url,'get_live_cell',[c['out_point'],False])} for c in result['liveCells']]
    result['tipAfter']=rpc(url,'get_tip_header',[])
    result['summary']={'uniqueTransactions':len(hashes),'liveCells':len(result['liveCells']),
      'capacityShannons':sum(int(c['output']['capacity'],16) for c in result['liveCells']),
      'plainCapacityShannons':sum(int(c['output']['capacity'],16) for c in result['liveCells'] if c['output']['type'] is None and c['output_data']=='0x'),
      'typedCells':sum(c['output']['type'] is not None for c in result['liveCells']),
      'earliestActivityBlock':min((int(b,16) for b in blocks),default=None),
      'latestActivityBlock':max((int(b,16) for b in blocks),default=None)}
    (OUT/(net.lower()+'-public-rpc.json')).write_text(json.dumps(result,indent=2))
    return net,result['summary']

if __name__=='__main__':
    identity=json.loads((OUT/'fixture-public-verified.json').read_text())[0]
    failed=False
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs={net:pool.submit(inspect,net,identity) for net in ENDPOINTS}
        for net,f in jobs.items():
            try:print(json.dumps(f.result()))
            except Exception as e:
                failed=True;print(net+' PUBLIC_QUERY_INCOMPLETE '+type(e).__name__)
    if failed:raise SystemExit(2)
