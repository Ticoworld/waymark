"""Compare frozen public Pocket observations with an independent saved oracle.
No device access, wallet keys, RPC acceleration, or changes to observations.
"""
import argparse,hashlib,json
from pathlib import Path
import h02_package as p
from r2_observe import SCRIPT

def check(observation,oracle,boundary):
    n=p.read_json(Path(observation)/'summary.json');o=p.read_json(Path(oracle))
    expected=sorted([{'txHash':c['out_point']['tx_hash'],'index':int(c['out_point']['index'],16),'capacity':int(c['output']['capacity'],16),'type':c['output']['type'],'data':c['output_data']} for c in o['liveCells']],key=lambda c:(c['txHash'],c['index']))
    actual=[{k:c[k] for k in ('txHash','index','capacity','type','data')} for c in n['liveCells']]
    txs=sorted(set(t['tx_hash'] for t in o['transactions']))
    p.require(n['script']==SCRIPT==o['script'],'script-identity')
    p.require(actual==expected,'live-cells-differ')
    p.require(n['transactions']==txs,'native-history-differs')
    p.require(len(n['wallets'])==1 and n['wallets'][0]['accountIndex']==0 and n['wallets'][0]['derivationPath']=="m/44'/309'/0'/0/0",'account-map')
    wallet=n['wallets'][0];packed=p.script_from_address(wallet['testnetAddress'],'TESTNET')
    p.require(bytes.fromhex(packed)[-20:].hex()==SCRIPT['args'][2:],'account-address')
    p.require(n['prefs']['selected_network']=='TESTNET','app-network')
    p.require(n['verifiedTip']>=boundary and n['registrations'][packed+':0']>=boundary,'native-progress-below-boundary')
    p.require(n['matchedWorkRows']==0,'pending-matched-work')
    # lightStartBlockNumber records the latest registration/resume start, not
    # the historical coverage floor (SyncCoordinator.setScriptsAndRecordLocked).
    p.require(n['prefs'].get(wallet['walletId']+'_testnet_sync_mode')=='CUSTOM' and n['prefs'].get(wallet['walletId']+'_testnet_custom_block_height')==22369937,'coverage-policy')
    p.require(len(n['progress'])==1 and n['progress'][0]['lightStartBlockNumber']<=n['progress'][0]['localSavedBlockNumber'] and boundary<=n['progress'][0]['localSavedBlockNumber']<=n['registrations'][packed+':0'],'app-progress')
    balances=n['room']['balances'];p.require(len(balances)==1 and balances[0]['walletId']==wallet['walletId'],'balance-owner')
    p.require(int(balances[0]['capacity'],16)==sum(c['capacity'] for c in expected),'app-balance')
    rows=n['room']['transactions'];p.require(sorted(set(r['txHash'] for r in rows))==txs,'app-history')
    p.require(all(r['walletId']==wallet['walletId'] and r['status']=='CONFIRMED' and r['isLocal']==0 for r in rows),'app-history-status')
    p.require(n['room']['daoCount']==0,'unexpected-dao')
    p.require(n['keyFamilyCounts'].get('32',n['keyFamilyCounts'].get(32,0))==len(expected),'unexpected-extra-script-live-cells')
    semantic={'network':'TESTNET','script':SCRIPT,'path':wallet['derivationPath'],'liveCells':expected,'capacity':sum(c['capacity'] for c in expected),'history':txs,'coverageStart':22369937,'acceptedThrough':boundary,'daoCount':0}
    return {'result':'PASS','semantic':semantic,'semanticSha256':hashlib.sha256(p.encode(semantic)).hexdigest()}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('observation');parser.add_argument('oracle');parser.add_argument('--boundary',type=int,required=True);parser.add_argument('--out',type=Path,required=True);a=parser.parse_args()
    try:
        result=check(a.observation,a.oracle,a.boundary)
        with a.out.open('xb') as f:f.write(p.encode(result))
        print(json.dumps(result,indent=2))
    except p.Refused as e:print('ACCEPTANCE_REFUSED '+str(e));raise SystemExit(2)
