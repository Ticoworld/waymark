# WO-3B2-R2 decision

**B2-INCONCLUSIVE. Stop before H2 for PM review.** SOURCE has correct two-account chain state and a real DAO deposit, but Pocket's stored DAO compensation disagrees with canonical math and remains wrong after restart. The work order explicitly forbids proceeding with an incorrect SOURCE. No H02 restoration or independent A2/B2 result exists.

Pocket v1.8.5 / code 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`; APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. TESTNET only. API 36 x86_64, 2048 MiB, two vCPUs, WHPX, Intel Iris Xe host GPU, headless, no snapshots. Explicit ADB serial `emulator-5580`. No SwiftShader, production source changes, physical Samsung access or D2. B1 evidence remains unchanged.

## Failure ownership

- What was correct: normally recovered parent/account identities, exact Script associations, two funded native Cell sets, per-account spendable balances/history, coherent coverage/progress, DAO principal/outpoint/header/epoch and restart persistence. No account rows were injected.
- What was wrong: SOURCE's Room `dao_cells.compensation`. The pinned Pocket DAO reader supplies 61 CKB occupied capacity for a 102-CKB DAO Cell. Two canonical-header audits reproduce the precise resulting overestimates (8,010 vs 7,661 shannons; 22,530 vs 21,546).
- What was restored from H2: **nothing**. H2/package/F2, source loss, A2 and B2 were never reached. This is not B2-FAIL-RESTORE/CATCHUP/MULTISCRIPT/PORTABILITY or evidence of a failed Candidate B2. A source-side DAO finding blocks the controlled experiment; hence B2-INCONCLUSIVE rather than claiming B2-FAIL-DAO for an arm that never ran.
- Boundary: Pocket's DAO application reader/cache calculation. Native indexing and DAO position facts matched the public chain. Native max-withdraw math applies the input it receives; the caller supplies the wrong occupied capacity. The actual unlock builder uses the correct 102-CKB constant. No incorrect unlock or lost funds was demonstrated.

**D2 has no demonstrated H02 job.** Correcting a Pocket calculation argument does not establish missing state authority, portability or an external reusable responsibility. D2 remains excluded. Leading product interpretation remains **POCKET FEATURE**, provisionally supported by B1; B2 extended acceptance is still unqualified. Do not infer a standalone product or reusable layer from this issue.

## Required PM decision

Do not proceed to physical-phone validation. Resolve the SOURCE DAO correctness gate first. PM may authorize a separately reviewed Pocket fix and an explicitly revised build pin/experiment, or explicitly narrow a subsequent acceptance contract to canonical position/mapping while carrying the known estimate defect as a limitation. No scope exclusion or production fix was silently applied in R2, and the approved APK was not replaced.

After that decision, use the retained real fixture and approved sequential fresh-userdata plan. Do not recreate three permanent runtimes. The existing SOURCE is stopped and retained for diagnosis, not declared lost or eligible for retirement. Current host space after shutdown exceeded the 10 GiB threshold, but storage readiness does not override the scientific gate. No new transaction should be sent merely to restart this investigation.

## Evidence and tooling

Primary evidence: `runs/wo3b2/result.json`, canonical `oracle-{initial,funded,deposit,halt}.json`, three `chain-events/*/confirmation.json` files, `source/dao-settled/`, `source/preH2-restart/`, both `dao-compensation-audit-*.json`, `source/signing-initial.json`, `source/gate-regression.json`, `source/HALTED.json` and `source/evidence-seal.json`. Original reports are retained under `runs/wo3b2-r2/previous-b2-reports/`. Intermediate position-only PASS markers remain for provenance and are explicitly superseded as full acceptance claims.

Only new `b2r2_*` test helpers and these six authorized reports were changed. Production source/approved APK, preexisting H02 scripts, B1/R1/storage evidence and private fixture were preserved. The new Java observer adds only allowlisted public DAO fields; the local signing helper emits only public challenge/key/signature. Python syntax checks and actual V1 signing passed. Five retained-state regression cases enforce fail-closed compensation/export checks. The account continuation, export/restore, negative-package and retirement helpers remain prepared rather than qualified end-to-end on A2/B2; no B2 package-negative result is claimed.

Biggest remaining unknown: whether stale two-account/DAO state converges correctly through independent normal recovery and sanitized restore once a correct source/explicit acceptance contract is available. Mature DAO unlock and physical V2 authentication also remain outside this run.

**STOP. Await PM review.**
