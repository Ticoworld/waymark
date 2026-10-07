"""Hash-seal completed phone arms; no device mutation or secret access."""
import argparse
import datetime
from pathlib import Path
import h02_package as p
from h02_device import ROOT
from p3c_phone_ui import BASE,event
from p3c_phone_state import save
from b2r4_acceptance import check

def public_evidence_gate(path):
    raw=path.read_bytes()
    if b'pocket_node_key_material' in raw:
        # Package exclusion intentionally rejects alias names. Evidence may
        # contain their strictly public protection/creation metadata only.
        def visit(obj):
            if isinstance(obj,dict):
                for k,v in obj.items():
                    if k in ('pocket_node_key_material','pocket_node_key_material_v2'):
                        p.require(isinstance(v,dict) and set(v)<= {'present','createdAt','userAuthenticationRequired','authenticationValiditySeconds','authenticationType','securityLevel','invalidatedByBiometricEnrollment','protectionMetadata'},'non-public-security-evidence')
                        p.require(all(type(x) in (bool,int,type(None)) or x=='UNKNOWN_API_REFUSED' for x in v.values()),'non-public-security-value')
                    visit(v)
            elif isinstance(obj,list):
                for v in obj:visit(v)
        visit(p.read_json(path))
        raw=raw.replace(b'pocket_node_key_material_v2',b'public_protection_v2').replace(b'pocket_node_key_material',b'public_protection_v1')
    p.secret_gate(raw)

def boundary(role,label):
    signing=p.read_json(BASE/role/'signing-result.json')
    oracle=p.read_json(BASE/('oracle-'+label+'.json'))
    tx=signing['txHash']
    height=int(oracle['tip']['number'],16)
    p.require(signing['confirmed'] and tx in oracle['accounts'][0]['transactions'],'signing-boundary-not-covered')
    save(BASE/(label+'-boundary.json'),{'network':'TESTNET','height':height,'hash':oracle['tip']['hash'],
        'transaction':tx,'transactionHeight':int(signing['header']['number'],16),'oracleSha256':p.sha(BASE/('oracle-'+label+'.json'))})
    print('PHONE_BOUNDARY_RECORDED '+label+' '+str(height))

def finish(role,initial,restart,oracle_label,boundary_label):
    folder=BASE/role
    p.require(not (folder/'evidence-manifest.json').exists(),'arm-already-sealed')
    oracle=BASE/('oracle-'+oracle_label+'.json')
    edge=p.read_json(BASE/(boundary_label+'-boundary.json'))
    final=p.read_json(folder/(restart+'-acceptance.json'))
    verified=check(folder/restart,oracle,edge['height'],folder/(restart+'-dao-audit.json'))
    p.require(verified['semanticSha256']==final['semanticSha256'],'final-acceptance-binding')
    first=p.read_json(folder/(initial+'-acceptance.json'))
    p.require(first['result']==final['result']=='PASS','canonical-acceptance-incomplete')
    p.require(p.read_json(folder/(restart+'-restart.json'))['normalPocketUnlock'],'restart-unproved')
    signing=p.read_json(folder/'signing-result.json')
    p.require(signing['signing']==signing['broadcast']=='PASS' and signing['confirmed'] and signing['signatureMatchesOwnedScript'],'signing-unproved')
    key=p.read_json(folder/restart/'security.json')['pocket_node_key_material_v2']
    before=p.read_json(folder/'security-after-account0.json')['pocket_node_key_material_v2']
    p.require(key==before,'fresh-keystore-metadata-changed')
    if role=='candidate':
        activation=p.read_json(folder/'activation.json')
        p.require(activation['result']=='PASS' and activation['destinationSecurityUnchanged'],'activation-unproved')
        control=p.read_json(BASE/'control/result.json')
        p.require(first['semanticSha256']==control['canonicalSemanticSha256'],'common-FP-canonical-divergence')
        old=p.read_json(BASE/'control/security-after-account0.json')['pocket_node_key_material_v2']
        p.require(key['createdAt']!=old['createdAt'],'candidate-keystore-not-independent')
    utc=datetime.datetime.now(datetime.timezone.utc)
    start=datetime.datetime.fromisoformat(p.read_json(folder/'fresh-state.json')['utc'])
    result={'role':role,'result':'PASS','utc':utc.isoformat(),'totalSeconds':(utc-start).total_seconds(),
        'initialObservation':initial,'restartObservation':restart,'restart':'PASS','signing':'PASS',
        'transaction':signing['txHash'],'confirmed':True,'boundary':edge,
        'canonicalSemanticSha256':final['semanticSha256'],'initialSemanticSha256':first['semanticSha256'],
        'freshV2KeystorePreserved':True,'genuineAndroidAuthentication':'MANUALLY_APPROVED',
        'productionSourceModified':False,'D2Used':False}
    if (folder/'result.json').exists():
        prior=p.read_json(folder/'result.json')
        p.require(all(prior[k]==result[k] for k in result if k not in ('utc','totalSeconds')),'retained-arm-result-changed')
    else:save(folder/'result.json',result)
    event(role,'arm_evidence_seal_complete',semanticSha256=final['semanticSha256'])
    files=[]
    paths=list(folder.rglob('*'))+[oracle,BASE/(boundary_label+'-boundary.json'),BASE/'pre-destructive-check.json']
    for path in sorted(set(paths)):
        if not path.is_file():continue
        if path.suffix in ('.json','.jsonl'):public_evidence_gate(path)
        files.append({'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,'sha256':p.sha(path)})
    save(folder/'evidence-manifest.json',{'role':role,'accepted':True,'utc':utc.isoformat(),'files':files})
    for row in files:p.require(p.sha(ROOT/row['path'])==row['sha256'],'arm-seal-verification')
    print('PHONE_ARM_SEALED_PASS '+role+' files='+str(len(files)))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('role',choices=['control','candidate']);a.add_argument('action',choices=['boundary','finish']);a.add_argument('--label');a.add_argument('--initial');a.add_argument('--restart');a.add_argument('--oracle');a.add_argument('--boundary')
    v=a.parse_args()
    try:
        if v.action=='boundary':boundary(v.role,v.label)
        else:finish(v.role,v.initial,v.restart,v.oracle,v.boundary)
    except Exception as e:
        print('PHONE_FINISH_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else ''));raise SystemExit(2)
