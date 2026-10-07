"""Write R4 reports only from accepted, sealed public evidence; no guest access."""
import datetime
import json
import shutil
from decimal import Decimal

import h02_package as p
from h02_device import ROOT
from b2r2_chain import script

BASE = ROOT / "runs/wo3b2"
COMMIT = "b28979de744798ffb75367b031d4871ec3af1a12"
APK = "903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f"
PROFILE = "API 36 / x86_64 / 2048 MiB / 2 vCPUs / WHPX / Intel Iris Xe HOST GPU / headless / no snapshots"
NAMES = ["P3B2_FIXTURE.md", "P3B2_SOURCE_RESULT.md", "P3B2_CONTROL_RESULT.md", "P3B2_CANDIDATE_RESULT.md", "P3B2_COMPARISON.md", "P3B2_DECISION.md"]


def read(path):
    return p.read_json(BASE / path)


def ckb(value):
    return format(Decimal(value) / Decimal(10**8), ".8f")


def gib(value):
    return f"{value / 2**30:.3f} GiB ({value:,} bytes)"


def events(role):
    rows = [json.loads(x) for x in (BASE / role / "events.jsonl").read_text().splitlines()]
    return {x["event"]: x for x in rows}


def phase(e, start, end):
    return e[end]["monotonic"] - e[start]["monotonic"]


def live_table(accounts):
    text = "| Account | Outpoint | Capacity (CKB) | Kind |\n|---|---|---:|---|\n"
    for a in accounts:
        for cell in a["liveCells"]:
            if "out_point" in cell:
                out = cell["out_point"]
                h, i, capacity, typed = out["tx_hash"], int(out["index"], 16), int(cell["output"]["capacity"], 16), cell["output"]["type"] is not None
            else:
                h, i, capacity, typed = cell["txHash"], cell["index"], cell["capacity"], cell["type"] is not None
            index = a.get("index", a.get("accountIndex"))
            text += f"| {index} | `{h}:{i}` | {ckb(capacity)} | {'DAO deposit' if typed else 'ordinary'} |\n"
    return text


def progress_table(n):
    text = "| Account | Local wallet UUID | Parent UUID | Native registration | Native global minimum | Verified tip | Room saved cursor |\n|---|---|---|---:|---:|---:|---:|\n"
    for a in n["accounts"]:
        w = a["wallet"]
        packed = script(a["script"]).hex() + ":0"
        room = next(x for x in n["progress"] if x["walletId"] == w["walletId"])
        text += f"| {w['accountIndex']} | `{w['walletId']}` | `{w['parentWalletId']}` | {a['registrations'][packed]} | {a['minFiltered']} | {a['verifiedTip']} | {room['localSavedBlockNumber']} |\n"
    return text


def dao_table(rows):
    text = "| Observation | Inferred estimate header | Pocket compensation (shannons) | Canonical compensation (shannons) | Cache age at capture (ms) |\n|---|---:|---:|---:|---:|\n"
    for label, a in rows:
        m = a["matchingKnownReaderHeaders"][0]
        text += f"| {label} | {m['height']} | {a['observedCompensation']} | {m['canonicalCompensation']} | {a.get('cacheAgeAtCaptureMs', 'see audit')} |\n"
    return text


def main():
    out = ROOT / "runs/wo3b2-r4"
    archive = out / "previous-b2-reports"
    p.require(not (out / "result.json").exists(), "reports-already-generated")
    receipt, boundary, oracle = read("source/package-receipt.json"), read("final-boundary.json"), read("oracle-F2.json")
    final_public = read("oracle-final-recheck.json")
    for expected, current in zip(oracle["accounts"], final_public["accounts"]):
        p.require(all(expected[k] == current[k] for k in ("index", "script", "liveCells", "transactions", "capacity", "plainCapacity")), "public-fixture-changed-after-F2")
    a, b = read("control/result.json"), read("candidate/result.json")
    p.require(a["result"] == b["result"] == "PASS" and a["restart"] == b["restart"] == "PASS", "arms-not-accepted")
    p.require(a["canonicalSemanticSha256"] == b["canonicalSemanticSha256"], "arm-semantic-divergence")
    p.require(not set(oracle["accounts"][0]["transactions"]) & set(oracle["accounts"][1]["transactions"]), "overlapping-account-histories")
    for role in ("source", "control", "candidate"):
        seal = read(role + "/evidence-seal-r4.json")
        p.require(seal["accepted"] and seal["restartPassed"], "unsealed-acceptance")
        for item in seal["files"]:
            p.require(p.sha(ROOT / item["path"]) == item["sha256"], "evidence-hash-mismatch")
    p.validate(BASE / "package-H2-immutable", receipt["manifestSha256"], APK, oracle["genesis"][2:])
    source = read("source/r4-H2-canonical/summary.json")
    snapshots = {role: read(role + "/" + result["restartObservation"] + "/summary.json") for role, result in (("control", a), ("candidate", b))}
    audits = [("SOURCE H2", read("source/r4-H2-canonical-dao-audit.json"))]
    for role, result in (("control", a), ("candidate", b)):
        for label in (result["firstObservation"], result["restartObservation"]):
            audits.append((role + " " + label, read(role + "/" + label + "-dao-audit.json")))
    if archive.exists():
        # A prior formatting refusal can leave the archival checkpoint intact.
        # Reuse it only while every original and archived report still agrees.
        history = p.read_json(archive / "hashes.json")
        for item in history:
            p.require(p.sha(archive / item["path"]) == item["sha256"]
                      and p.sha(ROOT / "docs" / item["path"]) == item["sha256"], "archival-checkpoint-changed")
    else:
        archive.mkdir(parents=True)
        history = []
        for name in NAMES:
            original = ROOT / "docs" / name
            if original.exists():
                shutil.copy2(original, archive / name)
                history.append({"path": name, "sha256": p.sha(original)})
        (archive / "hashes.json").write_bytes(p.encode(history))
    sr, ar = read("source/runtime-retirement.json"), read("control/runtime-retirement.json")
    e0, e1 = boundary["events"]
    dao = receipt["sourceAcceptance"]["semantic"]["dao"][0]
    common = f"Pocket v1.8.5/code 27, commit `{COMMIT}`; approved APK SHA-256 `{APK}`. TESTNET. {PROFILE}. Explicit emulator serial `emulator-5580`. Physical Samsung untouched; D2 excluded; production Pocket source unchanged.\n\n"
    fixture = "# WO-3B2-R4 fixture\n\n**Two genuinely populated derived accounts and one confirmed active DAO deposit.** Continued from the preserved R2/R3 SOURCE; no account or DAO fixture was recreated.\n\n" + common
    fixture += "Both locks use code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`.\n\n| Account | Derivation path | Lock args | Parent | Historical coverage |\n|---|---|---|---|---:|\n"
    for x in receipt["sourceAcceptance"]["semantic"]["accounts"]:
        fixture += f"| {x['accountIndex']} | `{x['path']}` | `{x['script']['args']}` | {x['parentAccountIndex']} | {x['coverageStart']} |\n"
    fixture += f"\nAccount 1 was funded through the independently controlled disposable TESTNET relay; its history is distinct from account 0. DAO owner: account 1; outpoint `{dao['txHash']}:{dao['index']}`; principal {ckb(dao['capacity'])} CKB; stage DEPOSITED; data `0x0000000000000000`; type code hash `0x82d76d1b75fe2fd9a27dfbaa65a039221a380d76c926f378d3f81cf3e7e13f2e`, hash type `type`, empty args. Deposit block {dao['depositBlockNumber']}, hash `{dao['depositBlockHash']}`, epoch `{dao['depositEpochHex']}`. No later DAO transition was attempted.\n\n"
    fixture += f"H2 = {boundary['H2']}, hash `{boundary['H2Hash']}`. F2 = {boundary['F2']}, hash `{boundary['F2Hash']}`. Both post-H2 events confirmed at {e0['confirmationHeight']}, hash `{e0['confirmationHash']}`. Activity was frozen afterward.\n\nAccount-0 transaction `{e0['transactionHash']}` consumes H2-live U `{e0['U']['tx_hash']}:{int(e0['U']['index'],16)}` and creates two ordinary owned Cells. The public node reports U as `unknown`, with null Cell; its confirmed canonical spend and absence from the final live index jointly prove consumption. Account-1 transaction `{e1['transactionHash']}` delivers 100 CKB from the existing relay.\n\n"
    fixture += "Final canonical live set:\n\n" + live_table(oracle["accounts"])
    fixture += "\nFull transaction bodies, lock/type/data, headers, live-status queries and histories are retained in `runs/wo3b2/oracle-H2.json`, `oracle-F2.json`, `final-boundary.json` and `chain-events/post-H2-account*/`. F2 histories contain six account-0 and three account-1 transactions, with no cross-account transaction overlap.\n\nThe known reader defect uses 61 CKB instead of canonical 102 CKB occupied capacity. This trial accepts canonical DAO position continuity; compensation is independently audited and reported separately. See [R3 diagnosis](P3B2_R3_DAO_SOURCE_DIAGNOSIS.md). Later withdrawal, unlock and mature DAO lifecycle execution remain NOT TESTED.\n"

    source_doc = "# WO-3B2-R4 SOURCE result\n\n**PASS under the PM-approved canonical DAO-position contract.** The R2/R3 SOURCE was integrity-checked and resumed, without rebuilding accounts or transactions. The earlier R2 compensation halt remains preserved as history.\n\n" + common
    source_doc += "Both accounts matched their public canonical history, exact live Cells and balances before export. Supported UI reconciliation and restart passed, discovery was settled, both Scripts were registered, and per-Script/native/Room progress was coherent. The first proposed H2 capture had a sibling tip and was rejected; no package or event was produced from it. A later capture passed canonical chain anchoring.\n\n" + progress_table(source)
    source_doc += f"\nH2 {receipt['H2']}, hash `{receipt['H2Hash']}`. Package `runs/wo3b2/package-H2-immutable`; {receipt['packageBytes']:,} bytes; export {receipt['exportSeconds']:.3f} seconds; trusted manifest SHA-256 `{receipt['manifestSha256']}`. Logical payload: sanitized public wallet/account/mapping/coverage/progress/discovery state and native TESTNET state. The two accounts retain distinct derivations and parent relationships. Balance/history/header/DAO caches, pending actions, contacts/freeform metadata, source key material/security and peer identity are excluded and reconstructed.\n\n"
    source_doc += "Structural and exact-credential exclusion passed: mnemonic, BIP39 seed, both derived private keys and emulator PIN absent in checked encodings. `key_material`, PIN/security preferences, key backups and Android Keystore state are excluded. Manifest, payload hashes, approved version/schema, TESTNET genesis and account/Script checks passed. Receipt: `source/package-receipt.json`.\n\n" + dao_table(audits[:1])
    source_doc += f"\nAfter the two authorized confirmed events, F2 {boundary['F2']} was independently captured. SOURCE remained frozen at H2; no source catch-up was used by either arm. SOURCE was stopped and declared lost, 117 compact files were hashed, and exact allowlisted disposable runtime images were retired. Logical runtime bytes removed: {sr['logicalBytes']:,}; observed host free-space delta: {sr['reclaimedHostBytes']:,}; free afterward: {gib(sr['freeAfter'])}. The delta is a host observation, not solely logical image size. A PowerShell receipt-size summing error occurred after deletion; every planned path was verified absent before receipt finalization. No additional deletion was performed.\n\n`source/LOST.json`, `evidence-seal-r4.json`, `runtime-retirement-plan.json` and `runtime-retirement.json` preserve this boundary. After loss, arms used only normal recovery secrets, the sanitized package where authorized, retained public facts and public chain access; no SOURCE guest/native/Room state was queried.\n"

    arm_docs = {}
    for role, result in (("control", a), ("candidate", b)):
        ev = events(role)
        n = snapshots[role]
        accepted = read(role + "/" + result["restartObservation"] + "-acceptance.json")
        text = f"# WO-3B2-R4 {'CONTROL A2' if role=='control' else 'CANDIDATE B2'} result\n\n**PASS, including restart and both-account local signing readiness.**\n\n" + common
        text += f"Fresh independent userdata/encryption backing was created from the installed API-36 image. Pre-launch free space: {gib(read(role+'/disk-before.json')['freeBytes'])}. Pre-install Pocket was absent; before first launch Room DB, native TESTNET store, Pocket preferences and key backups were absent. Exact APK installation/hash and role registry were verified. New destination UUIDs and Keystore state were retained; source security/key rows were never restored. Provisioning evidence: `{role}/boot/provision.json`, `{role}/fresh-runtime.json`.\n\n"
        provision = read(role + "/boot/provision.json")
        text += f"Pre-install Android boot ANRs/crashes recorded: {provision['priorBootAnrCount']}. Where nonzero, the existing settled-Android gate required seven Settings/Home/system-server observations for at least 180 seconds without new ANRs/crashes before installation. This is recorded as a boot qualification caveat, not claimed as an ANR-free first boot.\n\nNormal automatic mnemonic recovery and supported Add account flow produced the expected account-0/account-1 identities and parent relationship. No Room/account row injection. Both CUSTOM historical floors were verified. UI switching continuations and discovery replays are included in total elapsed time, not deducted.\n\n"
        if role == "control":
            text += "No H2 package was used. An initial exact check already matched all owned canonical facts but rejected unsettled discovery/global native progress (four pending probes). That incomplete capture is retained at `control/r4-first`; normal Pocket resume completed the replay. A second capture, `control/r4-settled-first`, had complete discovery/progress but its latest native tip differed from the public node's canonical block at the same height; the audit refused it. Its public anchor diagnostic is retained, and F2 itself remained canonical. Normal catch-up then passed the full canonical gate. Startup UI timing refusals were handled by a bounded public-authentication wait in the harness; Pocket was not modified, and all such elapsed time remains included.\n\n"
        else:
            activation = read("candidate/activation-receipt.json")
            stale = read("candidate/restored-stale-proof.json")
            p.require(stale["result"] == "PASS" and stale["UObservedLiveAfterActivation"] and stale["postH2TransactionsAbsentBeforeLaunch"], "restored-staleness-not-proven")
            text += f"The immutable H2 package was validated against trusted digest `{activation['packageManifest']}`, mapped to freshly recovered destination accounts, transferred, staged and activated using the approved WO-2 helper. Activated native payload hash matched `{activation['activatedNativeDigest']}` before launch. The actual guest pre-launch capture `candidate/r4-restored-H2` proves U was restored live and both post-H2 transactions absent, with progress at H2. Room DAO, transaction and balance caches were empty, as intended; source caches were not restored. Proof: `candidate/restored-stale-proof.json`. Normal catch-up removed U, indexed account-0 replacements and account-1 incoming Cell, and reconstructed application/DAO caches. Neither Script acquired the other's state.\n\n"
        text += "Accepted per-account native/Room progress after restart:\n\n" + progress_table(n)
        text += "\nExact accepted live set:\n\n" + live_table(accepted["semantic"]["accounts"])
        text += "\nBoth spendable balances and six/three covered histories match F2; all app transactions are CONFIRMED/nonlocal. Account 1 retains its exact canonical DAO owner/lock/type/outpoint/principal/data/stage/live status/deposit block/hash/epoch/history, with null withdrawal/unlock metadata. Discovery is settled. Compensation refresh is bound to a fresh canonical header interval and matches the known 61-CKB formula; an unexplained estimate or unchanged old H2 cache would be rejected.\n\n"
        text += dao_table([(label, audit) for label, audit in audits if label.startswith(role + " ")])
        text += f"\nForce-stop/normal authentication/relaunch preserved the canonical semantic hash `{result['canonicalSemanticSha256']}`. Challenge signatures for both accounts verified locally against their expected Scripts before and after restart; no transaction was broadcast for signing checks. This covers emulator V1 security, not physical-device V2 authentication. Full acceptance result: `{role}/result.json`; first observation `{result['firstObservation']}`, restart observation `{result['restartObservation']}`.\n\n"
        text += f"Total recovery time from before first Pocket launch through complete restart acceptance: **{result['totalSeconds']:.3f} seconds**. Key/security: {phase(ev,'first_launch_begin','normal_keys_and_security_complete'):.3f} s. TESTNET account-0 registration requested at {phase(ev,'first_launch_begin','testnet_custom_registration_requested'):.3f} s. Account-1 coverage requested at {phase(ev,'first_launch_begin','account1_custom_registration_requested'):.3f} s.\n\n"
        if role == "control":
            first_event = result["firstObservation"] + "_exact_acceptance_pass"
            text += f"Registration-to-first exact acceptance: {phase(ev,'testnet_custom_registration_requested',first_event):.3f} s, an inclusive reconstruction interval containing account setup, UI reconciliation, discovery, replay and audit; pure historical reconstruction and post-F2 tip catch-up were not independently separable. Runtime retired only after accepted captures and hashes were sealed; free afterward {gib(ar['freeAfter'])}.\n"
        else:
            first_event = result["firstObservation"] + "_exact_acceptance_pass"
            text += f"Package transfer: {phase(ev,'package_transfer_begin','package_transfer_complete'):.3f} s; validation: {phase(ev,'package_validation_begin','package_validation_complete'):.3f} s; total package restore including mapping/staging/activation: {phase(ev,'package_restore_begin','package_restore_complete'):.3f} s. Launch request to first exact acceptance: {phase(ev,'light_client_launch_requested',first_event):.3f} s, inclusive of catch-up, app reconciliation and acceptance audit. Pure native catch-up was not independently isolated. Accepted Candidate runtime is stopped/sealed and retained for PM review.\n"
            watch = [json.loads(x) for x in (BASE / "candidate/r4-catchup-watch.jsonl").read_text().splitlines()]
            first_synced = next(x for x in watch if "\u2713 Synced" in x["publicStatus"] and (x.get("nativeLastLoggedMinimum") or 0) >= boundary["F2"])
            observed = (datetime.datetime.fromisoformat(first_synced["utc"]) - datetime.datetime.fromisoformat(ev["light_client_launch_requested"]["utc"])).total_seconds()
            text += f"\nThe first qualifying synced watcher sample occurred {observed:.3f} s after launch request (about 33-second sampling granularity). It is an observed startup/catch-up bound; final exact acceptance still required the later canonical/native/Room audit.\n"
        arm_docs[role] = text

    comparison = "# WO-3B2-R4 comparison\n\n**A2 and B2 are canonically equivalent at F2: B2-PASS.**\n\n" + common
    comparison += "| Acceptance item | Control A2 | Candidate B2 |\n|---|---|---|\n| Normal key/account recovery and parent association | PASS | PASS |\n| Both exact Scripts and distinct owned state | PASS | PASS |\n| F2 live Cells, balances and covered histories | PASS | PASS |\n| Account-0 stale-U removal/new state | PASS | PASS |\n| Account-1 post-H2 activity | PASS | PASS |\n| DAO canonical position and account association | PASS | PASS |\n| Known reader compensation defect only | PASS | PASS |\n| Per-Script/native/Room progress and settled discovery | PASS | PASS |\n| Two-account local signing readiness | PASS | PASS |\n| Restart semantic persistence | PASS | PASS |\n\n"
    comparison += f"Both canonical semantic hashes: `{a['canonicalSemanticSha256']}`. UUIDs, cache timestamps, native tips beyond F2, and tip-dependent compensation values are deliberately retained as observations rather than treated as equal wallet semantics. Known estimate values are independently matched to the same 61-CKB algorithm at each tightly bounded canonical header interval; raw reward numbers at different tips are not directly compared.\n\n" + dao_table(audits)
    comparison += f"\nA final independent public-chain recheck at tip {int(final_public['tip']['number'],16)} confirmed the exact F2 live sets, histories and capacities remain unchanged. Raw evidence: `runs/wo3b2/oracle-final-recheck.json`.\n"
    be = events("candidate")
    comparison += f"\n| Measurement | Value |\n|---|---:|\n| A2 total, including restart acceptance | {a['totalSeconds']:.3f} s |\n| B2 total, including restart acceptance | {b['totalSeconds']:.3f} s |\n| H2 package | {receipt['packageBytes']:,} bytes |\n| Package export | {receipt['exportSeconds']:.3f} s |\n| Package restore including gates/activation | {phase(be,'package_restore_begin','package_restore_complete'):.3f} s |\n\n**LIMITED PERFORMANCE FIXTURE.** This run tests correctness across richer wallet state. Totals include host/UI accommodations, discovery replays, auditing and restart. No production speed claim or generalized multiplier is justified. Detailed event timestamps and bounded watcher samples are retained per arm.\n\nNine disposable-copy package tests rejected corruption, missing payload, wrong network/genesis, unsupported Pocket/Room/native versions, manifest-digest mismatch and payload-hash mismatch before activation. Results are under `runs/wo3b2/negative-packages/`. No production source changes were made.\n"
    decision = "# WO-3B2-R4 decision\n\n**B2-PASS. Current demonstrated product boundary: POCKET FEATURE.**\n\n"
    decision += "Same-version wallet-owned sanitized recovery survived two populated accounts, distinct lock Scripts, wallet/account mapping, per-Script progress, active DAO application state, stale post-backup activity on both accounts, independent normal-recovery control, signing readiness and restart without D2. No repeated responsibility outside Pocket ownership was demonstrated. D2 has no demonstrated H02 job from this run.\n\n"
    decision += "The pre-existing v1.8.5 DAO reader defect remains separately documented and unpatched: canonical occupied capacity 102 CKB, reader argument 61 CKB. Canonical DAO ownership/identity/stage/live status/principal/header/epoch/history passed; estimates refreshed using the known algorithm. No recovery-specific DAO divergence occurred. This PASS does not certify correct compensation/APC display or a mature withdrawal/unlock transaction. The unsent bug draft remains separate.\n\n"
    decision += "Recommend PM-authorized real-phone validation next, especially Android Keystore/V2 authentication, actual device packaging/activation and lifecycle behavior. The Samsung was untouched during this work order; no next phase starts automatically. Largest remaining unknown: the emulator's V1 same-version result has not yet been demonstrated on the real phone's V2 security and device storage. Long DAO lifecycle, reorg depth/finality tolerance, cross-version migration, extensive wallet activity and product-level benefit also remain outside this core proof.\n\n"
    decision += "Source and Control runtimes were retired sequentially only after compact evidence was verified and sealed; Candidate remains stopped and retained. Historical R2 report versions are archived byte-for-byte under `runs/wo3b2-r4/previous-b2-reports/`, with hashes. B1 and R1/R2/R3 evidence, H02 private fixture and protected D2/iBytes/PR #297 material remain preserved. No further transactions after F2.\n\n**STOP. Wait for PM review.**\n"
    docs = [fixture, source_doc, arm_docs["control"], arm_docs["candidate"], comparison, decision]
    for name, text in zip(NAMES, docs):
        (ROOT / "docs" / name).write_text(text, encoding="utf-8")
    result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "classification": "B2-PASS",
              "canonicalStatesEquivalent": True, "semanticSha256": a["canonicalSemanticSha256"],
              "D2Used": False, "physicalPhoneTouched": False, "productionSourceModified": False,
              "productBoundary": "POCKET FEATURE", "performanceFixture": "LIMITED", "productSpeedClaim": False,
              "finalPublicOracleSha256": p.sha(BASE / "oracle-final-recheck.json"),
              "reports": [{"path": "docs/"+n, "sha256": p.sha(ROOT / "docs" / n)} for n in NAMES]}
    (out / "result.json").write_bytes(p.encode(result))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
