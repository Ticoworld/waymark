# WO-3B1-R2 decision: B1-PASS

**The basic mechanism passes.** Pocket v1.8.5 recovered the existing disposable account from normal keys plus a sanitized same-version non-secret state package, processed the post-H spend correctly, rebuilt app state and matched independent normal recovery through F. Restart preserved the result. All nine required/adjoining negative package cases failed closed before activation.

Control A: **24m13.074s** to full restart-qualified acceptance; first exact F state at **13m20.542s**. Candidate B: **4m53.140s** full; first exact F state at **3m28.774s**; package operation **8.480s**. This is a **LIMITED PERFORMANCE FIXTURE**, not a production speed claim. Detailed phase definitions, overlapping/unisolated costs and the normal second discovery pass are retained in the comparison/arm reports.

Shared semantic hash: `13cb9e9b74c918a9fe27bb9a9205545125998bfcb86fb5f02408a23db754567a`. H 22,646,283; F 22,646,322. U was genuinely live in the saved package, then consumed by the one authorized TESTNET self-transfer. Both independent arms end with four live Cells, four transactions and 19,999.99998 CKB. Source was lost/sealed before A/B; source DBs/userdata were not consulted afterward.

## What this establishes

A wallet-owned snapshot of selected non-secret native and application state is enough for this basic same-version user job. Raw Room copying was unnecessary. Normal recovery creates fresh destination secrets; public IDs/progress/discovery settings are remapped; normal Pocket reconciliation recreates omitted caches. Production source/APK were unchanged; test-only debug/run-as tooling performed export/import.

The result includes application continuity as well as native state: preserving settled discovery metadata prevented the ordinary additional discovery replay observed on SOURCE and A. Native-only portability is not what this experiment tested. The complete transfer was small (1,895,341 bytes), but package size alone says nothing about supported production history scale.

## What remains unproved

- More than one populated account/Script, account-axis and chain discovery beyond this one-account fixture, and their exact ownership/history mapping.
- DAO deposit/withdrawal lifecycle and reconstruction of omitted application DAO caches after stale backup.
- Cross-version/schema/ABI restoration, arbitrary Android devices and production non-debuggable export/import. Unsupported versions currently refuse.
- Crash/power-loss behavior on real devices, reorg/long-stale packages, concurrent actions and richer app metadata. Synthetic journal tests are not a real-device crash campaign.
- Independent historical completeness or an untrusted snapshot source. This package reuses trusted source work; hashes authenticate retained bytes, not omitted history.
- Typical user benefit across older/denser histories, devices and repeated trials; reliable off-device backup creation before phone loss. Encryption, scheduling, storage and a supported wallet UX were not implemented.

## D2 and next decision

**Does D2 enter next: NO.** No portability or authority failure appeared that requires D2 to solve this one-Script same-version case. Continue evaluating the simpler wallet-owned route within its stated trust boundary. This result neither reopens nor extends D2's completed proof program.

**Recommend WO-3B2 extended acceptance: YES, subject to PM review. Do not execute it in this order.** B2 should add two populated Scripts/accounts with exact mapping/coverage, a DAO position and its relevant deposit/withdrawal progression, stale and post-H activity on those states, exact native/app reconciliation and restart. If a separate disposable counterparty is necessary for that fixture, define it in the approved B2 contract first. Preserve the key-exclusion and malformed-package gates. A meaningful performance study is a separate later decision after broader correctness.

Biggest remaining correctness unknown: whether the same narrowly selected application/native state is sufficient for multi-account and DAO recovery without skipped discovery, missing history or stale app decisions. Biggest product unknown: the magnitude and reliability of user benefit once production wallet integration and realistic restore burdens are measured.

## Handoff

All five requested reports are complete. Both measured emulators are stopped; SOURCE remains sealed. Only the one approved TESTNET transaction was created. No phone access, production source changes, D2, second actual account, DAO, cloud integration, PR or grant work. Generated packages/DBs/APKs/logs and private material remain ignored by git. Only experiment documents/scripts are eligible for the local commit.

Review `P3B1_COMPARISON.md` and its evidence paths before approving further work. **STOP for PM review; B2 has not started.**

The previous environmental B1-INCONCLUSIVE reports are preserved with checked SHA-256 hashes in `runs/wo3b1-r2/previous-b1-reports/`. Original run artifacts, R1 diagnosis and qualified profile remain unchanged.
