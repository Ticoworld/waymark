"""Normal supported phone recovery phases. Stop at genuine Android auth prompts."""
import argparse
import time
import h02_package as p
from h02_device import APP
from p3c_phone_ui import BASE,device,event,tap,private_input,nodes,system_auth,ack_page_warning,unlock,nav,back,select_account
from p3c_r1_probe import probe
from p3c_phone_state import save,security

def begin(role):
    p.require((BASE/role/'fresh-state.json').exists(),'fresh-state-required')
    p.require(not (BASE/role/'events.jsonl').read_text().count('first_launch_begin'),'recovery-already-started')
    event(role,'first_launch_begin');device().shell('am','start','-n',APP+'/.MainActivity');time.sleep(2)
    ack_page_warning(role);tap(public_id='onboarding-recover');private_input('phrase')
    event(role,'protected_mnemonic_fields_filled');tap(public_id='import-submit');event(role,'normal_import_submitted')
    if system_auth(nodes()):event(role,'SYSTEM_AUTH_WAITING',operation='secure imported keys');return

def after_import_auth(role):
    p.require(not system_auth(nodes()),'system-auth-still-waiting')
    event(role,'android_key_encryption_auth_approved',evidence='Genuine prompt; manual approval confirmed')
    tap(public_id='sync-sheet-apply');tap(public_id='pin-intro-continue');private_input('pin');time.sleep(1);private_input('pin');time.sleep(2)
    tap(public_id='bg-sync-optin-skip');event(role,'normal_account0_recovery_and_pin_setup_complete')
    if any(n.get('text')=='Got it' for n in nodes()):tap(text='Got it')
    save(BASE/role/'security-after-account0.json',security(device()))
    tap(text='CKB Mainnet')
    # Restart can end the UI helper after its legitimate click. Observe before retrying.
    try:tap(text='Switch & Restart')
    except p.Refused:
        p.require(not any(n.get('text')=='Switch to Testnet?' for n in nodes()),'network-switch-not-activated')
    time.sleep(3)
    p.require(unlock(role),'system-auth-still-waiting')
    event(role,'testnet_switch_and_normal_app_unlock_complete')

def coverage(role,index):
    floor={0:22369937,1:22647000}[index]
    nav('Settings');tap(text='Sync Options');tap(text='From a specific date');tap(text='Block Height')
    device().shell('input','keycombination','113','29');device().shell('input','text',str(floor));back()
    tap(public_id='sync-sheet-apply');event(role,'account'+str(index)+'_historical_coverage_requested',floor=floor);nav('Wallet')

def request_account(role):
    app=probe('app');p.require(len(app['wallets'])==1,'account1-already-present-or-unexpected-wallet')
    nav('Settings');tap(text='Manage Wallets');tap(description='Settings');tap(text='Add account')
    tap(text='Account Name');device().shell('input','text','Phone%sAccount%s1');back();tap(text='Create')
    if any(n.get('text')=='Continue anyway' for n in nodes()):tap(text='Continue anyway')
    event(role,'supported_account1_creation_requested');time.sleep(1)
    if system_auth(nodes()):event(role,'SYSTEM_AUTH_WAITING',operation='supported account1 creation')

def after_account_auth(role,set_coverage=False):
    p.require(not system_auth(nodes()),'system-auth-still-waiting')
    app=probe('app');ws=sorted(app['wallets'],key=lambda w:w['accountIndex'])
    p.require(len(ws)==2 and ws[0]['parentWalletId'] is None and ws[1]['parentWalletId']==ws[0]['walletId'],'two-account-parent-map')
    expected=['bc5882c4309431ee23ad7bbad4b5c3325539eebd','2da024570462b0e2421d87abcbfebd4567d52ad5']
    p.require([p.script_from_address(w['testnetAddress'],'TESTNET')[-40:] for w in ws]==expected,'two-owned-scripts')
    p.require([w['derivationPath'] for w in ws]==["m/44'/309'/0'/0/0","m/44'/309'/1'/0/0"],'normal-derivation-paths')
    p.require(len(app['keyMetadata'])==2 and all(k['kdfVersion']==2 for k in app['keyMetadata']),'fresh-v2-rows')
    save(BASE/role/'public-after-account1.json',app)
    save(BASE/role/'security-after-account1.json',security(device()))
    event(role,'both_normal_accounts_and_expected_scripts_verified');back();back();nav('Wallet')
    select_account(0);select_account(1)
    if set_coverage:coverage(role,1)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('role',choices=['control','candidate'])
    parser.add_argument('phase',choices=['begin','after-import-auth','coverage0','request-account1','after-account-auth'])
    args=parser.parse_args()
    try:
        if args.phase=='begin':begin(args.role)
        elif args.phase=='after-import-auth':after_import_auth(args.role)
        elif args.phase=='coverage0':coverage(args.role,0)
        elif args.phase=='request-account1':request_account(args.role)
        else:after_account_auth(args.role,set_coverage=args.role=='control')
    except Exception as e:
        print('PHONE_RECOVERY_PHASE_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else '')+'; retain current UI/state, do not re-enter phrase blindly')
        raise SystemExit(2)
