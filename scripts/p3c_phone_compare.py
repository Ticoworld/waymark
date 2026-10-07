"""Normalize common-FP equivalence and Candidate's later self-transfer effect."""
import datetime
import h02_package as p
from h02_device import ROOT
from p3c_phone_ui import BASE
from p3c_phone_state import save
from p3c_phone_finish import public_evidence_gate
from p3c_phone_destination import compatibility
from p3c_phone_activate import R,A

def cells(account):
    return {(c['out_point']['tx_hash'],int(c['out_point']['index'],16)):
            {'output':c['output'],'output_data':c['output_data']} for c in account['liveCells']}

def run():
    c=p.read_json(BASE/'control/result.json');b=p.read_json(BASE/'candidate/result.json')
    p.require(c['result']==b['result']=='PASS','phone-arms-incomplete')
    for role in ('control','candidate'):
        for row in p.read_json(BASE/role/'evidence-manifest.json')['files']:
            p.require(p.sha(ROOT/row['path'])==row['sha256'],'phone-arm-seal-changed')
    p.require(c['canonicalSemanticSha256']==b['initialSemanticSha256'],'common-FP-semantic-divergence')
    fp=p.read_json(BASE/'oracle-FP.json');end=p.read_json(BASE/'oracle-final.json')
    signed=p.read_json(BASE/'candidate/signing-result.json');tx=signed['transaction'];h=signed['txHash']
    p.require(end['accounts'][0]['transactions']==sorted(fp['accounts'][0]['transactions']+[h]),'unaccounted-account0-history')
    expected=cells(fp['accounts'][0])
    for item in tx['inputs']:
        prev=item['previous_output'];key=(prev['tx_hash'],int(prev['index'],16))
        p.require(key in expected,'candidate-signing-input-not-live-at-FP');del expected[key]
    for i,(out,data) in enumerate(zip(tx['outputs'],tx['outputs_data'])):
        expected[h,i]={'output':out,'output_data':data}
    p.require(expected==cells(end['accounts'][0]),'unaccounted-account0-live-state')
    p.require(cells(fp['accounts'][1])==cells(end['accounts'][1]) and fp['accounts'][1]['transactions']==end['accounts'][1]['transactions'],'unaccounted-account1-state')
    p.require(end['accounts'][0]['plainCapacity']==fp['accounts'][0]['plainCapacity']-signed['feeShannons'],'unaccounted-capacity-change')
    p.require(end['accounts'][1]['capacity']==fp['accounts'][1]['capacity'],'unaccounted-dao-account-capacity')
    caught=p.read_json(BASE/'candidate/caught-up-FP-acceptance.json')
    p.require(c['transaction'] in caught['semantic']['accounts'][0]['history'],'control-FP-not-recovered')
    artifact,manifest,_=compatibility(R,A)
    result={'result':'PASS','classification':'PHONE-PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'commonFP':c['boundary'],'commonFPSemanticSha256':c['canonicalSemanticSha256'],
        'commonFPExactEquivalence':True,'controlFPRecoveredByCandidate':True,
        'candidateLaterTransaction':h,'candidateTransactionFeeShannons':signed['feeShannons'],
        'laterHistoryAndLiveStateExactlyExplained':True,'finalOracleSha256':p.sha(BASE/'oracle-final.json'),
        'candidateFinalSemanticSha256':b['canonicalSemanticSha256'],
        'recoverySpecificDaoDivergence':False,'knownDaoDefectOnly':True,'canonicalOccupiedCKB':102,'readerOccupiedCKB':61,
        'destinationKeystoreIndependent':True,'genuineAndroidSigningAuthenticationBothArms':True,
        'immutableH2ManifestSha256':p.sha(ROOT/'runs/wo3b2/package-H2-immutable/manifest.json'),
        'phoneApkSha256':artifact['apkSha256'],'productionSourceModified':False,
        'D2Used':False,'D2DemonstratedJob':False,'productBoundary':'POCKET FEATURE','additionalTechnicalProofRequiredBeforeOwnerHandoff':False}
    save(BASE/'comparison.json',result)
    reports(c,b,result,artifact)
    files=[]
    final_paths=([BASE/'comparison.json',BASE/'oracle-final.json',BASE/'oracle-FP.json',BASE/'retained-phone-runtime.json',
                 BASE/'control/evidence-manifest.json',BASE/'candidate/evidence-manifest.json']+
                [ROOT/'docs'/name for name in ('P3C_PHONE_CONTROL.md','P3C_PHONE_CANDIDATE.md','P3C_PHONE_COMPARISON.md','P3C_DECISION.md')])
    for path in final_paths:
        public_evidence_gate(path) if path.suffix=='.json' else p.secret_gate(path.read_bytes())
        files.append({'path':path.relative_to(ROOT).as_posix(),'sha256':p.sha(path),'bytes':path.stat().st_size})
    save(BASE/'final-evidence-manifest.json',{'result':'PASS','files':files})
    for row in files:p.require(p.sha(ROOT/row['path'])==row['sha256'],'final-seal-changed')
    print('PHONE_AB_CANONICAL_COMPARISON_AND_REPORTS_PASS')

def duration(seconds):
    return f'{int(seconds)//60} min {int(seconds)%60} sec (elapsed, including manual authentication and qualification overhead; not a speed benchmark)'

def reports(c,b,r,artifact):
    common=f"Samsung SM-S9180 (`R5CW6127VPR`), Android 16/API 36, arm64-v8a, 4096-byte pages. Pocket 1.8.5/code 27, TESTNET, source commit `{artifact['pocketCommit']}`. Phone APK SHA-256 `{artifact['apkSha256']}`; signer `{artifact['certificate']['certificateSha256']}`. Physical phone used; D2 excluded."
    def dao(role,label):
        x=p.read_json(BASE/role/(label+'-dao-audit.json'));h=x['matchingKnownReaderHeaders'][0]
        return f"At canonical block {h['height']:,}, Pocket estimate {x['observedCompensation']:,} shannons versus canonical {h['canonicalCompensation']:,}. Canonical occupied capacity 102 CKB; reader 61 CKB. Audit verdict `{x['verdict']}`; no recovery-specific DAO divergence. Compensation remains separate from canonical position acceptance."
    control=f"""# WO-3C phone Control P-A

**PASS. Normal recovery, real device security, confirmed signing and cold restart verified.**

{common}

Pre-destructive custody gates verified the protected fixture, both known paths, exact approved artifact, immutable H2 and historical evidence/oracles. Only Pocket user-0 data was cleared. Fresh-state evidence proves absence of wallet/Room/native/preferences/key backups/restore journal and both Pocket Keystore aliases. No unrelated phone data was touched. No H2 package was used in Control.

Protected normal mnemonic recovery and supported Add account created account 0 `m/44'/309'/0'/0/0` and account 1 `m/44'/309'/1'/0/0`. Genuine Android key-encryption/account authentication was observed and manually approved. Normal Pocket setup/unlock used protected input without credential output. Both key rows have kdfVersion 2; fresh V2 alias metadata establishes per-operation authentication and Trusted Environment protection. No source key/security state was imported.

Historical CUSTOM floors: 22,369,937 and 22,647,000. Exact canonical gates PASS for identities, Scripts, account/parent mapping, no cross-account leakage, live outpoints/balances, native/Room history, both B2 post-H2 activities, DAO owner/outpoint/principal/stage/live status/deposit header/epoch and coherent progress. The 1,000 CKB DAO remains DEPOSITED under account 1. Background discovery settled to 50 EMPTY candidates plus one RESTORED account, no pending probes/matched work.

Pocket reviewed and signed a 61 CKB account-0 self-transfer after genuine manually approved Android signing authentication. Transaction `{c['transaction']}` was broadcast and confirmed on canonical TESTNET; its recoverable witness signature independently matches account 0's Script. No host private-key signer was used. FP: **{c['boundary']['height']:,}**, hash `{c['boundary']['hash']}`.

The required post-signing cold restart, normal Pocket authentication and native ARM64 startup PASS. Exact post-restart acceptance includes the FP transaction, both accounts, DAO and persisted progress. Fresh Keystore protection/creation metadata remains unchanged; no auth/Keystore/native/schema errors were observed. FP semantic SHA-256 `{c['canonicalSemanticSha256']}`.

{dao('control',c['restartObservation'])}

Elapsed time: {duration(c['totalSeconds'])}. Two premature captures were correctly refused as unsettled while four discovery probes scanned; navigation before retirement restarted those probes and prolonged Control. These retained observations are not recovery failures. The final uninterrupted retirement and unchanged canonical acceptance gates passed. Public alias metadata receives separate strict schema checks for evidence; original package secret exclusion remains unchanged.

Evidence: `runs/wo3c/phone-ab/control/result.json`, `control/evidence-manifest.json`, `control/{c['initialObservation']}-acceptance.json`, `control/{c['restartObservation']}-acceptance.json`, `control/signing-result.json`, `FP-boundary.json`, `oracle-FP.json`. Evidence was hash-sealed/reverified before Candidate's authorized Pocket-only reset.
"""
    candidate=f"""# WO-3C phone Candidate P-B

**PASS. Immutable H2 recovery, stale catch-up, independent destination security, confirmed signing and cold restart verified.**

{common}

Control evidence was secured before clearing only Pocket user-0 state. Fresh Candidate evidence proves no Control wallet/Room/native/preferences/key-backup/journal state or Pocket Keystore aliases. Both accounts were recovered/created normally through protected fixture input and supported Pocket flows, with genuine manually approved Android key-encryption/account authentication. Both account paths, Scripts, parent mapping and V2 rows pass before H2. Candidate's V2 alias has a different creation time from Control and requires authentication per operation.

Immutable H2 is **22,652,549**, hash `0x3f96acadbf4ef0d847db36468ca13feb37630fd5a156a5540713897c0dd4e3ee`; manifest SHA-256 `{r['immutableH2ManifestSha256']}`. Separate qualified physical transport validates original source provenance/hash independently of the ARM destination artifact, same commit/native tree/schema, TESTNET/genesis, exact account/Script mapping, audited architecture-independent native encoding and unchanged secret exclusion. No resealing, ABI transformation or source secret/security import occurred. A pre-staging `coverage-mode` refusal was resolved by saving explicit historical options through normal Pocket Settings; validators were not relaxed.

Guarded staging/activation PASS. Wallet UUIDs/identities and fresh Keystore metadata remained unchanged; helper encrypted-row digest guards preserve destination phone-side security. Catch-up from H2 through F2 and FP PASS, including both original post-H2 activities, stale Cell removal and Control's signing transaction. Exact common-FP semantic SHA-256 `{b['initialSemanticSha256']}` equals Control. Both accounts, multi-Script state, history, balances/live outpoints, DAO canonical owner/outpoint/principal/stage/status/deposit metadata and coherent progress pass with no cross-account leakage.

After restore Pocket signed another 61 CKB account-0 self-transfer through the normal review flow and genuine manually approved Android signing authentication. The user observed and confirmed that Android approval; the transient prompt completed before automation captured its UI. Evidence records that distinction (`USER_OBSERVED_AND_APPROVED`), corroborated by per-operation V2 protection and the pinned authenticated signing path. Transaction `{b['transaction']}` was broadcast and confirmed canonically; its witness signature independently matches the owned Script. This proves the restored public state operates with the fresh destination authentication/Keystore path and has no emulator key dependency.

Required post-signing cold restart, normal unlock and ARM native startup PASS. Both accounts, DAO, caught-up state and Candidate transaction persist. Exact final acceptance PASS at **{b['boundary']['height']:,}**, hash `{b['boundary']['hash']}`. Fresh V2 creation/protection metadata remains intact; no auth/Keystore/native/schema error was observed.

{dao('candidate',b['restartObservation'])}

Elapsed time: {duration(b['totalSeconds'])}. Evidence: `runs/wo3c/phone-ab/candidate/result.json`, `candidate/evidence-manifest.json`, `candidate/activation.json`, `candidate/caught-up-FP-acceptance.json`, `candidate/{b['restartObservation']}-acceptance.json`, `candidate/signing-result.json`, `oracle-final.json`. The final capture stopped/froze Pocket; afterward the package was re-enabled without launch or state change. Candidate wallet data remains intact with its process stopped (`retained-phone-runtime.json`). No cleanup or further transaction is authorized by this result.
"""
    comparison=f"""# WO-3C phone A/B comparison

**PHONE-PASS. Canonical recovery equivalence YES; recovery-specific DAO divergence NO.**

{common}

| Requirement | Control P-A | Candidate P-B |
| --- | --- | --- |
| Fresh Pocket sandbox and Keystore | PASS | PASS, independent of Control |
| Normal two-account key recovery | PASS | PASS before H2 |
| Exact account/Script/parent mapping, no leakage | PASS | PASS |
| Canonical Cells, balances, covered history | PASS | PASS |
| Both B2 post-H2 activities | PASS | PASS after stale H2 catch-up |
| DAO canonical position/header/history | PASS | PASS |
| Known estimate defect only | PASS | PASS, separately audited |
| Genuine Android signing auth and confirmed transaction | PASS | PASS after restore |
| Cold restart/native persistence | PASS | PASS |

Common FP **{c['boundary']['height']:,} / {c['boundary']['hash']}** includes Control transaction `{c['transaction']}`. Control post-restart and Candidate caught-up canonical states have identical semantic SHA-256 `{r['commonFPSemanticSha256']}`. UUIDs are normalized through exact account/Script identity rather than compared across independent recovery installations. Native and Room histories, live Cells, balances, historical coverage and canonical DAO fields all pass.

Candidate's later transaction `{b['transaction']}` is explicitly accounted for. Its canonical inputs are removed from FP live Cells and its self outputs added; this exactly produces the final oracle. Account-0 history adds exactly this transaction and spendable capacity falls only by its **{r['candidateTransactionFeeShannons']} shannon** fee. Account 1/DAO history and live state remain identical. Later final tips are not compared blindly against Control's earlier tip.

Destination security remains independent: Control aliases were absent after reset, Candidate created fresh authenticated V2 security normally, activation preserved its creation/protection metadata and encrypted rows, and confirmed real-device signing succeeded afterward. No source security material was imported, no system credential collected and no Android authentication bypass used.

H2 manifest/package, original emulator APK, x86 validator/transport, B1/B2 evidence and production Pocket source remain unchanged. No physical data outside Pocket was touched; no historical H02/D2/iBytes cleanup occurred. Device page size is 4096; recurring 16 KB alignment warning is acknowledged normally and retained as a separate native packaging follow-up, with no H02 block or claim of 16 KB support.

Timing includes manual auth/setup and Control discovery/automation delays and is not a controlled performance benchmark. Scope: one disposable TESTNET fixture, two accounts/Scripts, one active DAO deposit, same pinned Pocket source/debug build on this Samsung; DAO withdrawal and cross-version/16 KB-device behavior were not required or demonstrated. Evidence: `runs/wo3c/phone-ab/comparison.json`, both arm evidence manifests, FP/final oracles and `final-evidence-manifest.json`.
"""
    decision=f"""# WO-3C decision

**PHONE-PASS. H02 boundary remains POCKET FEATURE. No further technical H02 proof is required before the Pocket owner handoff within this approved scope.**

Control normally recovered both populated accounts and the real DAO, created fresh authenticated V2 device-bound security, signed/broadcast a confirmed TESTNET self-transfer and passed cold restart. Candidate independently recovered keys/accounts, activated unchanged cross-ABI H2 public state, recovered F2 and Control FP activity exactly, preserved destination authentication/Keystore ownership, signed/broadcast a second confirmed transaction and passed cold restart. Both states are canonically equivalent at common FP; Candidate's subsequent transaction exactly explains its later state. No recovery-specific state, account mapping, multi-Script, DAO, catch-up, Keystore, authentication, signing or storage divergence was demonstrated.

Approved phone APK `{artifact['apkSha256']}` remains separately pinned from the original x86 emulator APK. H2 manifest `{r['immutableH2ManifestSha256']}` and source provenance were never rewritten. Existing x86 gates and package secret exclusion remain unchanged. Physical phone was used; D2 was not.

D2 has no demonstrated H02 job. The complete recovery responsibility tested here remains in Pocket's account model, persistence, embedded light-client state, normal recovery/authentication and signing flow. Strong proof does not establish a reusable layer or standalone grant product.

Recommended owner handoff: show the B1/B2 and phone A/B evidence, immutable public package/schema/secret exclusions, guarded same-source cross-ABI compatibility and independent destination Keystore proof; show both confirmed signing transactions and normalized FP/final comparison. Describe this as a Pocket-owned recovery feature experiment and discuss owner integration, supported import/export UX and maintenance of strict provenance/schema/network/account gates. Do not send private fixture material or credentials. Keep the existing 61-versus-102 CKB DAO display/cache defect separately linked to `P3B2_R3_DAO_SOURCE_DIAGNOSIS.md` and `P3B2_R3_POCKET_DAO_BUG_DRAFT.md`. Record the 16 KB native alignment warning as a separate compatibility follow-up; this 4096-byte-page phone passed.

Limits: same pinned version/commit, one Samsung/API-36 device, disposable TESTNET fixture and active DAO deposit. This is technical owner-handoff proof, not production release qualification or a timing benchmark. Candidate's final installation/evidence remain preserved. No cleanup, additional signing, D2 work, grant reclassification or owner messaging follows automatically.

Recommended H02 next action: PM review, then Pocket maintainer handoff of the compact public evidence and proposed Pocket feature boundary. **STOP. Wait for PM review.**
"""
    for name,text in {'P3C_PHONE_CONTROL.md':control,'P3C_PHONE_CANDIDATE.md':candidate,'P3C_PHONE_COMPARISON.md':comparison,'P3C_DECISION.md':decision}.items():
        p.secret_gate(text.encode());(ROOT/'docs'/name).write_text(text,encoding='utf-8')

if __name__=='__main__':
    try:run()
    except Exception as e:
        print('PHONE_COMPARISON_REFUSED '+type(e).__name__+((' '+str(e)) if isinstance(e,p.Refused) else '')+'; preserve all evidence');raise SystemExit(2)
