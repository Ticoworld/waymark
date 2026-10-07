"""Normal Pocket self-transfer and independent public-chain signing proof."""
import argparse
import datetime
import time
from coincurve import PublicKey
import h02_package as p
from p3c_phone_ui import BASE,device,event,nav,select_account,tap,nodes,system_auth,back
from p3c_phone_state import save
from b2r2_chain import SCRIPTS,ARGS,URL,rpc,pages,raw_tx,ckb_hash,table,blob,u64,unhex
from b2r2_observe import table as unpack

def prepare(role,acceptance_label=None):
    out=BASE/role/'signing-attempt.json'
    p.require(not out.exists(),'signing-attempt-exists-reconcile-before-retry')
    label=acceptance_label or ('initial' if role=='control' else 'caught-up-FP')
    p.require((BASE/role/(label+'-acceptance.json')).is_file(),'canonical-state-before-signing-required')
    nav('Wallet');select_account(0)
    current=pages(URL,'get_transactions',SCRIPTS[0]);prior=sorted(set(t['tx_hash'] for t in current))
    ws=p.read_json(BASE/role/'public-after-account1.json')['wallets']
    address=next(w['testnetAddress'] for w in ws if w['accountIndex']==0)
    save(out,{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':role,
        'network':'TESTNET','recipient':address,'sourceAccount':0,'amountShannons':61*10**8,
        'priorTransactionHashes':prior,'signer':'Pocket supported V2 UI path; no host private-key signer',
        'confirmationRequired':True,'acceptedObservation':label})
    tap(text='SEND');tap(text='Enter CKB Address');device().shell('input','text',address);back()
    tap(text='Enter Amount');device().shell('input','text','61');back();tap(text='Send CKB')
    ns=nodes()
    p.require(any(n.get('text')=='Review transaction' for n in ns),'review-sheet-required')
    # The prepared public input is verified by normal review and canonical result.
    review={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'knownReviewLabels':[n.get('text') for n in ns if n.get('text') in ('Review transaction','Recipient','Amount','Network fee','Total','61.00 CKB','61 CKB','Confirm')],
        'normalReviewShown':True}
    save(BASE/role/'signing-review.json',review)
    event(role,'normal_self_transfer_review_ready',account=0,amountShannons=61*10**8)

def confirm(role):
    p.require((BASE/role/'signing-review.json').exists(),'normal-review-required')
    p.require(not (BASE/role/'signing-confirm-request.json').exists(),'confirmation-already-requested')
    save(BASE/role/'signing-confirm-request.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'normalUIConfirm':True})
    tap(text='Confirm');event(role,'normal_self_transfer_confirm_requested');time.sleep(1)
    if system_auth(nodes()):event(role,'SYSTEM_AUTH_WAITING',operation='Authenticate to Send');return

def verify_public_transaction(txhash):
    detail=rpc(URL,'get_transaction',[txhash])
    p.require(detail and detail['tx_status']['status']=='committed','phone-transaction-not-confirmed')
    tx=detail['transaction'];p.require('0x'+ckb_hash(raw_tx(tx)).hex()==txhash,'confirmed-transaction-hash')
    header=rpc(URL,'get_header',[detail['tx_status']['block_hash']])
    p.require(rpc(URL,'get_block_hash',[header['number']])==header['hash'],'phone-transaction-noncanonical')
    inputs=[]
    for item in tx['inputs']:
        prev=item['previous_output'];old=rpc(URL,'get_transaction',[prev['tx_hash']])['transaction']
        output=old['outputs'][int(prev['index'],16)]
        p.require(output['lock']==SCRIPTS[0] and output['type'] is None,'self-transfer-input-owner-or-type')
        inputs.append({'outPoint':prev,'capacity':int(output['capacity'],16)})
    p.require(all(o['lock']==SCRIPTS[0] and o['type'] is None for o in tx['outputs']) and all(x=='0x' for x in tx['outputs_data']),'not-harmless-self-transfer')
    p.require(any(int(o['capacity'],16)==61*10**8 for o in tx['outputs']),'self-transfer-amount')
    fee=sum(x['capacity'] for x in inputs)-sum(int(o['capacity'],16) for o in tx['outputs'])
    p.require(0<fee<=10**6,'unexpected-phone-transfer-fee')
    witnesses=[unhex(w) for w in tx['witnesses']]
    fields=unpack(witnesses[0]);p.require(len(fields)==3 and len(fields[0])==69,'signature-witness-shape')
    signature=fields[0][4:]
    first=table([blob(bytes(65)),fields[1],fields[2]])
    message=ckb_hash(raw_tx(tx))+u64(len(first))+first
    for w in witnesses[1:]:message+=u64(len(w))+w
    recovered=PublicKey.from_signature_and_message(signature,ckb_hash(message),hasher=None).format(compressed=True)
    p.require(ckb_hash(recovered)[:20].hex()==ARGS[0],'public-signature-does-not-match-account0')
    return {'txHash':txhash,'confirmed':True,'header':header,'transaction':tx,'inputs':inputs,'feeShannons':fee,
            'recoveredPublicKey':'0x'+recovered.hex(),'signatureMatchesOwnedScript':True,'status':detail['tx_status']}

def confirmed(role,seconds=300,auth_evidence='UI_OBSERVED_AND_USER_APPROVED'):
    attempt=p.read_json(BASE/role/'signing-attempt.json')
    p.require((BASE/role/'signing-confirm-request.json').exists(),'send-confirm-required')
    p.require(not (BASE/role/'signing-result.json').exists(),'phone-signing-result-exists')
    p.require(auth_evidence in ('UI_OBSERVED_AND_USER_APPROVED','USER_OBSERVED_AND_APPROVED'),'auth-evidence-kind')
    event(role,'android_signing_auth_approved',evidence=auth_evidence)
    deadline=time.monotonic()+seconds
    while True:
        matches=pages(URL,'get_transactions',SCRIPTS[0])
        new=sorted(set(t['tx_hash'] for t in matches)-set(attempt['priorTransactionHashes']))
        p.require(len(new)<=1,'ambiguous-post-signing-chain-activity')
        if new:
            result=verify_public_transaction(new[0]);result.update({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'role':role,'signing':'PASS','broadcast':'PASS','auth':'GENUINE_ANDROID_APPROVED','authEvidence':auth_evidence,'hostPrivateSignerUsed':False})
            save(BASE/role/'signing-result.json',result)
            event(role,'phone_signing_broadcast_confirmation_pass',txHash=new[0],block=int(result['header']['number'],16))
            print('PHONE_SIGNING_CONFIRMED '+new[0],flush=True);return result
        if time.monotonic()>=deadline:raise p.Refused('no-confirmed-phone-signing-transaction-yet')
        time.sleep(10)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('role',choices=['control','candidate']);parser.add_argument('action',choices=['prepare','confirm','confirmed'])
    parser.add_argument('--acceptance-label')
    parser.add_argument('--auth-evidence',choices=['UI_OBSERVED_AND_USER_APPROVED','USER_OBSERVED_AND_APPROVED'],default='UI_OBSERVED_AND_USER_APPROVED')
    args=parser.parse_args()
    try:
        if args.action=='prepare':prepare(args.role,args.acceptance_label)
        elif args.action=='confirmed':confirmed(args.role,auth_evidence=args.auth_evidence)
        else:confirm(args.role)
    except Exception as e:
        print('PHONE_SIGNING_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else '')+'; reconcile public attempt before retry, never duplicate blindly')
        raise SystemExit(2)
