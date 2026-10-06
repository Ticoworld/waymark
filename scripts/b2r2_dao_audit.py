"""Independent canonical DAO compensation audit of a public frozen observation.
No wallet data writes or key access. Active-deposit cache lacks an as-of header;
compare its value against every canonical header up to the captured native tip.
"""
import argparse,concurrent.futures,json
from pathlib import Path
from b2r2_chain import ROOT,URL,rpc,encode,require,DAO
def audit(observation,oracle,label):
    n=json.loads((Path(observation)/'summary.json').read_text());o=json.loads(Path(oracle).read_text())
    out=ROOT/'runs/wo3b2'/label;require(not out.exists(),'audit-path-exists')
    rows=n['room']['daoCells'];require(len(rows)==1 and rows[0]['status']=='DEPOSITED','audit-deposit-profile')
    row=rows[0];start=row['depositBlockNumber'];end=n['accounts'][0]['verifiedTip']
    require(0<end-start<1000,'bounded-header-range')
    def get(height):return rpc(URL,'get_header_by_number',[hex(height)])
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:headers=list(pool.map(get,range(start,end+1)))
    require(headers[0]['hash']==row['depositBlockHash'] and headers[-1]['hash']==n['accounts'][0]['verifiedTipHash'],'canonical-anchor-mismatch')
    require(all(h['parent_hash']==prev['hash'] for prev,h in zip(headers,headers[1:])),'header-chain-discontinuous')
    require(rpc(URL,'get_block_hash',[hex(end)])==headers[-1]['hash'],'tip-not-canonical')
    owned=[a for a in o['accounts'] if any(c['out_point']['tx_hash']==row['txHash'] and int(c['out_point']['index'],16)==int(row['index'],16) for c in a['liveCells'])]
    require(len(owned)==1,'oracle-deposit-owner')
    cell=next(c for c in owned[0]['liveCells'] if c['out_point']['tx_hash']==row['txHash'] and int(c['out_point']['index'],16)==int(row['index'],16))
    output=cell['output'];require(output['type']=={'code_hash':DAO,'hash_type':'type','args':'0x'} and cell['output_data']=='0x0000000000000000','not-standard-deposit')
    occupied_bytes=8+32+1+len(bytes.fromhex(output['lock']['args'][2:]))+32+1+len(bytes.fromhex(output['type']['args'][2:]))+len(bytes.fromhex(cell['output_data'][2:]))
    require(occupied_bytes==102 and row['capacity']==int(output['capacity'],16),'occupied-capacity')
    ar=lambda h:int.from_bytes(bytes.fromhex(h['dao'][2:])[8:16],'little')
    initial=ar(headers[0]);capacity=row['capacity'];computed=[]
    for h in headers:
        def reward(occupied):return (capacity-occupied)*ar(h)//initial+occupied-capacity
        computed.append({'height':int(h['number'],16),'hash':h['hash'],'rewardWith102CKB':reward(102*10**8),'rewardWith61CKB':reward(61*10**8)})
    observed=row['compensation'];right=[r for r in computed if r['rewardWith102CKB']==observed];wrong=[r for r in computed if r['rewardWith61CKB']==observed]
    result={'observation':str(observation),'network':'TESTNET','depositOutpoint':cell['out_point'],'accountIndex':owned[0]['index'],'capacity':capacity,'occupiedBytes':occupied_bytes,'canonicalOccupiedShannons':occupied_bytes*10**8,'observedRoomCompensation':observed,'roomLastUpdatedAt':row['lastUpdatedAt'],'capturedNativeTip':end,'canonicalFormulaMatches':right,'pocket61FormulaMatches':wrong,'verdict':'ROW_MATCHES_61_CKB_ONLY' if wrong and not right else 'ROW_MATCHES_CANONICAL_FORMULA' if right and not wrong else 'REQUIRES_REVIEW','limitation':'Room does not persist a compensation as-of header; matching header is inferred from the exact integer result, not claimed as an observed RPC call','headers':headers,'computed':computed}
    out.write_bytes(encode(result));print(json.dumps({k:v for k,v in result.items() if k not in ('headers','computed')},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('observation');p.add_argument('oracle');p.add_argument('label');a=p.parse_args();audit(a.observation,a.oracle,a.label)
