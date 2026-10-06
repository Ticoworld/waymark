"""Two-account canonical comparison. No device/credential access or data mutation."""
import argparse,hashlib,json
from pathlib import Path
import h02_package as p
from b2r2_chain import SCRIPTS,script,DAO
FLOORS={0:22369937,1:22647000}
def number(v):return v if type(v) is int else int(v,16)
def check(observation,oracle,boundary,require_dao=True,dao_audit=None,position_only=False):
    n=p.read_json(Path(observation)/'summary.json');o=p.read_json(Path(oracle));app=p.read_json(Path(observation)/'app.json')
    scripts=p.validate_app(app);p.require(len(n['accounts'])==2,'account-count')
    semantic=[];dao_expected=[]
    for i,(a,b) in enumerate(zip(n['accounts'],o['accounts'])):
        w=a['wallet'];wid=w['walletId'];packed=scripts[wid]
        p.require(w['accountIndex']==b['index']==i and a['script']==b['script']==SCRIPTS[i],'identity-map')
        expected=sorted([{'txHash':c['out_point']['tx_hash'],'index':int(c['out_point']['index'],16),'capacity':int(c['output']['capacity'],16),'type':None if c['output']['type'] is None else script(c['output']['type']).hex(),'data':c['output_data']} for c in b['liveCells']],key=lambda c:(c['txHash'],c['index']))
        actual=[{k:c[k] for k in ('txHash','index','capacity','type','data')} for c in a['liveCells']]
        p.require(actual==expected,'account-'+str(i)+'-live-cells')
        p.require(a['transactions']==b['transactions'],'account-'+str(i)+'-native-history')
        p.require(a['verifiedTip']>=boundary and a['registrations'][packed+':0']>=boundary and a['minFiltered']>=boundary,'native-progress')
        p.require(a['matchedWorkRows']==0,'matched-work-pending')
        progress=[r for r in n['progress'] if r['walletId']==wid];p.require(len(progress)==1,'progress-owner')
        r=progress[0];p.require(r['lightStartBlockNumber']<=r['localSavedBlockNumber'] and boundary<=r['localSavedBlockNumber']<=a['registrations'][packed+':0'],'room-progress')
        p.require(n['prefs'].get(wid+'_testnet_sync_mode')=='CUSTOM' and n['prefs'].get(wid+'_testnet_custom_block_height')==FLOORS[i],'historical-coverage')
        bal=[r for r in n['room']['balances'] if r['walletId']==wid];p.require(len(bal)==1,'balance-owner')
        p.require(int(bal[0]['capacity'],16)==b['plainCapacity'] and p.script_from_address(bal[0]['address'],'TESTNET')==packed,'account-'+str(i)+'-app-balance')
        txs=[r for r in n['room']['transactions'] if r['walletId']==wid]
        p.require(sorted(r['txHash'] for r in txs)==b['transactions'],'account-'+str(i)+'-room-history')
        p.require(all(r['status']=='CONFIRMED' and r['isLocal']==0 for r in txs),'pending-history')
        for c in b['liveCells']:
            if c['output']['type'] is None:continue
            p.require(c['output']['type']=={'code_hash':DAO,'hash_type':'type','args':'0x'},'unexpected-typed-cell')
            h=c['out_point']['tx_hash'];index=int(c['out_point']['index'],16)
            rows=[r for r in n['room']['daoCells'] if r['txHash']==h and int(r['index'],16)==index]
            p.require(len(rows)==1,'dao-row-missing-or-duplicate');r=rows[0]
            p.require(r['walletId']==wid and r['network']=='TESTNET' and number(r['capacity'])==int(c['output']['capacity'],16),'dao-owner-capacity')
            header=b['headers'][b['transactionDetails'][h]['tx_status']['block_hash']]
            if c['output_data']=='0x0000000000000000':
                p.require(r['status']=='DEPOSITED' and r['depositBlockHash']==header['hash'] and number(r['depositBlockNumber'])==int(header['number'],16) and int(r['depositEpochHex'],16)==int(header['epoch'],16),'dao-deposit-state')
                p.require(r['withdrawBlockNumber'] is None and r['withdrawBlockHash'] is None,'unexpected-dao-withdraw-cache')
            else:
                p.require(r['status'] in ('LOCKED','UNLOCKABLE'),'dao-withdraw-state')
                p.require(r['withdrawBlockHash']==header['hash'] and number(r['withdrawBlockNumber'])==int(header['number'],16),'dao-withdraw-header')
                p.require(int.from_bytes(bytes.fromhex(c['output_data'][2:]),'little')==number(r['depositBlockNumber']),'dao-deposit-link')
            dao_expected.append({'accountIndex':i,'txHash':h,'index':index,'capacity':int(c['output']['capacity'],16),'data':c['output_data'],'status':r['status'],'depositBlockHash':r['depositBlockHash'],'depositBlockNumber':r['depositBlockNumber'],'depositEpochHex':r['depositEpochHex'],'withdrawBlockHash':r['withdrawBlockHash'],'withdrawBlockNumber':r['withdrawBlockNumber'],'withdrawEpochHex':r['withdrawEpochHex'],'unlockEpochHex':r['unlockEpochHex']})
        semantic.append({'accountIndex':i,'path':w['derivationPath'],'parentAccountIndex':None if i==0 else 0,'script':SCRIPTS[i],'liveCells':expected,'totalCapacity':b['capacity'],'spendableCapacity':b['plainCapacity'],'history':b['transactions'],'coverageStart':FLOORS[i]})
    p.require(not require_dao or len(dao_expected)==1,'real-dao-required')
    p.require(n['room']['daoCount']==len(dao_expected)==len(n['room']['daoCells']),'unexpected-dao-cache')
    p.require(n['accounts'][0]['keyFamilyCounts'].get('32',0)==sum(len(a['liveCells']) for a in semantic),'extra-owned-native-cells')
    p.require(not any(c['state'] in ('PENDING','FOUND') for c in app['candidates']),'discovery-unsettled')
    if dao_expected and not position_only:
        p.require(dao_audit is not None,'dao-compensation-not-validated')
        audit=p.read_json(Path(dao_audit));row=n['room']['daoCells'][0]
        p.require(Path(audit['observation']).resolve()==Path(observation).resolve() and audit['observedRoomCompensation']==row['compensation'] and audit['roomLastUpdatedAt']==row['lastUpdatedAt'],'dao-audit-observation-mismatch')
        p.require(audit['verdict']=='ROW_MATCHES_CANONICAL_FORMULA','dao-compensation-noncanonical-or-unresolved')
    result={'network':'TESTNET','acceptedThrough':boundary,'accounts':semantic,'dao':dao_expected}
    return {'result':'POSITION_ONLY_PASS' if position_only else 'PASS','scope':'Compensation excluded; not full SOURCE acceptance' if position_only else 'Canonical state including validated DAO compensation','semantic':result,'semanticSha256':hashlib.sha256(p.encode(result)).hexdigest()}
if __name__=='__main__':
    q=argparse.ArgumentParser();q.add_argument('observation');q.add_argument('oracle');q.add_argument('--boundary',type=int,required=True);q.add_argument('--out',type=Path,required=True);q.add_argument('--allow-no-dao',action='store_true');q.add_argument('--dao-audit',type=Path);q.add_argument('--position-only',action='store_true');a=q.parse_args()
    try:
        result=check(a.observation,a.oracle,a.boundary,not a.allow_no_dao,a.dao_audit,a.position_only)
        with a.out.open('xb') as f:f.write(p.encode(result))
        print(json.dumps(result,indent=2))
    except p.Refused as e:print('ACCEPTANCE_REFUSED '+str(e));raise SystemExit(2)
