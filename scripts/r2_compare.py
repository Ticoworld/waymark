"""Cross-arm semantic and stale-Cell proof from retained public evidence only."""
import json
from pathlib import Path
import h02_package as p
from h02_device import ROOT
from r2_observe import APK,GENESIS,native,SCRIPT

def main():
    base=ROOT/'runs/wo3b1-r2'
    trust='f89fc4feeb019b47b625be8df71f5ef9cd64acdf2104cd793f113e0c9530fd12'
    m,_=p.validate(base/'package-H-immutable',trust,APK,GENESIS)
    at_h=native(base/'package-H-immutable/native.sqlite')
    u=('0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894',0)
    tx='0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7'
    p.require(u in {(c['txHash'],c['index']) for c in at_h['liveCells']},'U-not-live-in-H')
    oracle=p.read_json(base/'oracle-F.json');detail=oracle['transactionDetails'][tx]
    p.require(detail['tx_status']['status']=='committed' and int(detail['tx_status']['block_number'],16)>m['boundary'],'not-post-H')
    p.require([i['previous_output'] for i in detail['transaction']['inputs']]==[{'tx_hash':u[0],'index':hex(u[1])}],'wrong-spend')
    p.require(oracle['spentU']['result']['status']!='live','U-publicly-live')
    arms={};semantics=[]
    for role in ('control','candidate'):
        result=p.read_json(base/role/'result.json')
        p.require(result['result']=='PASS' and result['restart']=='PASS','arm-failed')
        accepts=[p.read_json(x) for x in sorted((base/role).glob('*-acceptance.json'))]
        p.require(len(accepts)>=2 and all(a['result']=='PASS' and a['semanticSha256']==result['semanticSha256'] for a in accepts),'restart-acceptance-mismatch')
        s=accepts[-1]['semantic'];p.require(s['acceptedThrough']==22646322 and s['capacity']==1999999998000,'wrong-F-state')
        live={(c['txHash'],c['index']) for c in s['liveCells']}
        p.require(u not in live and (tx,0) in live and (tx,1) in live and tx in s['history'],'stale-catchup-failed')
        semantics.append(s)
        events=[json.loads(x) for x in (base/role/'events.jsonl').read_text().splitlines()]
        by={e['event']:e for e in events};p.require(len(by)==len(events),'duplicate-timing-event')
        def interval(a,b):return round(by[b]['monotonic']-by[a]['monotonic'],6)
        timing={'keyRecoverySeconds':interval('first_launch_begin','normal_keys_and_security_complete'),'networkAndCoverageUISeconds':interval('normal_keys_and_security_complete','testnet_custom_registration_requested'),'totalSeconds':interval('first_launch_begin','full_acceptance_complete'),'firstExactAcceptanceSecondsFromLaunch':interval('first_launch_begin','first-accepted_exact_acceptance_pass'),'restartAcceptanceSeconds':interval('first-accepted_exact_acceptance_pass','full_acceptance_complete')}
        if role=='control':
            timing['initialReconstructionCatchupReconciliationAndCheckSeconds']=interval('testnet_custom_registration_requested','first-accepted_exact_acceptance_pass')
        else:
            timing.update(packageSeconds=interval('package_restore_begin','package_restore_complete'),validationSeconds=interval('package_validation_begin','package_validation_complete'),transferSeconds=interval('package_transfer_begin','package_transfer_complete'),stageSeconds=interval('package_transfer_complete','restore_staged'),activationSeconds=interval('activation_begin','activation_complete'),launchToUnlockSeconds=interval('light_client_launch_requested','restored_app_unlocked'),postUnlockCatchupReconciliationAndCheckSeconds=interval('restored_app_unlocked','first-accepted_exact_acceptance_pass'))
        arms[role]={'semanticSha256':result['semanticSha256'],'timing':timing,'firstLaunchUTC':by['first_launch_begin']['utc'],'endUTC':by['full_acceptance_complete']['utc'],'pendingDiscoveryAtFirstAcceptance':result['normalDiscoveryPendingAtFirstAcceptance']}
    p.require(semantics[0]==semantics[1],'A-B-semantic-difference')
    negatives=list((base/'negative-packages').glob('*/result.json'))
    p.require(bool(negatives),'negative-gates-not-run')
    n=p.read_json(negatives[-1]);p.require(len(n['results'])==9 and all(r['rejected'] for r in n['results']) and not n['deviceActivationAttempted'],'negative-gate-failed')
    result={'classification':'B1-PASS','F':22646322,'H':m['boundary'],'manifestSha256':trust,'UWasLiveAtH':True,'UAbsentFromBothArms':True,'postHTx':tx,'publicUStatus':oracle['spentU']['result']['status'],'semantic':semantics[0],'arms':arms,'negativeTests':n['results'],'performanceFixture':'LIMITED','generalizableProductSpeedClaim':False,'timingCaveat':'Observed inclusive wall time; networking, reconstruction, catch-up and app polling overlap. Timer includes UI automation, validation, exact-state captures and restarts. No pure internal phase durations inferred.'}
    with (base/'comparison.json').open('xb') as f:f.write(p.encode(result))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
