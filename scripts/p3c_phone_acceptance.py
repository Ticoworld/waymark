"""Frozen canonical phone acceptance, security metadata, ordinary cold restart."""
import argparse
import json
import time
import datetime
import h02_package as p
from h02_device import APP
from p3c_phone_ui import BASE,device,event,reconcile,unlock,nodes,nav
from p3c_phone_state import capture,save,security
from p3c_r1a_observe import mappings,lifecycle
from b2r4_acceptance import audit,check

def native_runtime(role,label):
    d=device();pid=d.shell('pidof',APP).decode().strip()
    p.require(pid.isdigit(),'single-phone-pocket-process')
    result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':int(pid),
            'mappings':mappings(pid),'lifecycleEvents':lifecycle(pid)}
    p.require(result['mappings']['libckb_light_client_lib.so']['executableMappingPresent'],'phone-native-not-mapped')
    errors=result['lifecycleEvents']
    p.require(all(errors[k]==0 for k in ('nativeInitReturnedFalse','nativeStartReturnedFalse','setupError','unsatisfiedLinkError','nativeLoadSkipped','fatalJavaException','roomMigrationError','invalidKeyException','userNotAuthenticatedException')),'phone-startup-runtime-error')
    save(BASE/role/(label+'-runtime.json'),result)
    return result

def accept(role,label,oracle,boundary):
    reconcile(role,label)
    native_runtime(role,label)
    out=capture(role,label)
    auditfile=BASE/role/(label+'-dao-audit.json')
    audit(out,oracle,auditfile)
    result=check(out,oracle,boundary,auditfile)
    keys=p.read_json(out/'security.json')
    p.require(keys['pocket_node_key_material_v2']['present'] and
              keys['pocket_node_key_material_v2']['userAuthenticationRequired'] and
              keys['pocket_node_key_material_v2']['authenticationValiditySeconds']==0,'phone-v2-security-required')
    result.update({'phoneSecurity':'V2 destination device-bound, per-operation authentication',
                   'pocketDataClearedForThisRole':True,'immutableH2Applied':role=='candidate'})
    save(BASE/role/(label+'-acceptance.json'),result)
    event(role,'exact_canonical_acceptance_pass',label=label,semanticSha256=result['semanticSha256'])
    print('PHONE_EXACT_CANONICAL_ACCEPTANCE_PASS '+result['semanticSha256'],flush=True)
    return result

def restart(role,label):
    d=device()
    # Supports a frozen accepted capture; enabling does not import/change security.
    d.shell('pm','enable','--user','0',APP)
    old=d.shell('sh','-c','pidof '+APP+' || true').decode().strip()
    d.shell('am','force-stop','--user','0',APP);d.stopped()
    event(role,'cold_restart_begin',oldPid=int(old) if old.isdigit() else None)
    d.shell('am','start','-W','-n',APP+'/.MainActivity');time.sleep(2)
    p.require(unlock(role),'SYSTEM-AUTH-WAITING')
    new=d.shell('pidof',APP).decode().strip()
    p.require(new.isdigit() and new!=old,'cold-restart-process-boundary')
    save(BASE/role/(label+'-restart.json'),{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'oldPid':int(old) if old.isdigit() else None,'newPid':int(new),'processAbsentBeforeLaunch':True,
        'normalPocketUnlock':True,'dataCleared':False,'authBypassed':False})
    event(role,'cold_restart_unlocked',newPid=int(new))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('role',choices=['control','candidate'])
    parser.add_argument('action',choices=['accept','restart']);parser.add_argument('label')
    parser.add_argument('--oracle');parser.add_argument('--boundary',type=int)
    args=parser.parse_args()
    try:
        if args.action=='accept':accept(args.role,args.label,args.oracle,args.boundary)
        else:restart(args.role,args.label)
    except Exception as e:
        print('PHONE_ACCEPTANCE_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else '')+'; keep arm retained')
        raise SystemExit(2)
