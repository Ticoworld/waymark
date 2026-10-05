# H02 LOCAL INVENTORY

Date: 2026-10-05 (Africa/Lagos)
Workspace inspected: C:\Users\timot\Desktop\2026\CKB
Phase: H02-P0, local inventory only, pending PM review.

No repository was cloned, fetched, checked out, reset, cleaned, patched, built or tested during this inventory. No application or database was opened for execution. Existing repository files were read only; Git commands used --no-optional-locks. This report is the only file created. No H02 directory or Git repository was created.

Scope: recursive Git-marker discovery under the workspace, including ignored _work/ and nested repositories; Git remotes, branches, HEAD, status, worktree registrations and selected diffs; tracked reports, manifests, scripts, patches and result summaries; direct existence checks of raw evidence. Generated dependency/build/cache directories were pruned during repository discovery (.git internals, node_modules, target, build, dist, vendor, .gradle, .build, Pods, virtual environments and caches). This is not an exhaustive inventory of every disk or build artifact. The report also checks explicitly referenced Ubuntu WSL evidence and known external research/credential locations. Secret contents were not read.

## 1. EXISTING REPOSITORIES

Found 37 Git roots/worktree paths. These are not 37 independent complete clones: the count includes linked worktrees and two unborn scratch repositories.

“Clean” below means no tracked changes or nonignored untracked files reported by Git. It does not mean ignored databases, logs or build outputs are absent. All listed existing repositories remain read-only for H02-P0. Read-only reuse means source/report inspection, not running importers or opening evidence databases in write-capable tools.

All recorded fetch/push URLs agree for a given remote. The Neuron ev1 reference is marked blob:none by Git; do not assume every historical blob is available offline.

| Full path | Remote(s), fetch URL; push is identical unless noted | Branch and HEAD | State | Experiment classification and reuse |
|---|---|---|---|---|
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port | origin: https://github.com/Ticoworld/ckb-script-port.git | master<br>9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835 | DIRTY: 1 untracked example; tracked source clean | D2 product source; one untracked experiment driver. Read-only reuse: YES. H02: separate workspace. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\ckb-sdk-rust | origin: https://github.com/nervosnetwork/ckb-sdk-rust.git | master<br>1fbf3d4c9b35ef90bdb9e6621a8d26edde6325ce | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\ev1-neuron | origin: https://github.com/nervosnetwork/neuron.git [blob:none] | develop<br>a926e3383d3a3e305b3bde7d233474515ef01a2e | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\g3-1-pocket-node | origin: https://github.com/RaheemJnr/pocket-node.git | main<br>6eda0b7a4601050b011591d41cc702f0dc7a7c38 | DIRTY: 159 untracked files; tracked source clean | Pinned Pocket source plus 159 untracked evidence files; no tracked source diff. Read-only reuse: YES. Preserve captures; fresh H02 worktree. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\rp2b-patch-base-20260831 | None configured | master<br>No commit | Unborn repository; no committed HEAD | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\rp2b-patch-base-20260831b | None configured | master<br>c739e803b90aaa36ec91e15a8afb60cd698cc02c | DIRTY: 2 status entries | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\rp2b-patch-base2\src | None configured | master<br>b6fb60a1bd8b96201c9580f6e89576cf09765820 | DIRTY: 3 status entries | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\rp2b-patch-base3\src | None configured | master<br>e5ab6e7ef956e1494d2deb517e42c577f68d2b2b | DIRTY: 3 status entries | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\rp2b-patch-base4\src | None configured | master<br>ddba9878200ca28af4aad20c8fcc5238370c6819 | DIRTY: 3 status entries | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\rp2b-patch-base5\src | None configured | master<br>a0768981d12ce9251afc9bcf408593a3db328030 | DIRTY: 3 status entries | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\rp2b-patch-base6\src | None configured | master<br>9084d62317e49a55ff417694afbc118a8534338a | DIRTY: 3 status entries | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\rp2b-patch-check\src | None configured | master<br>No commit | Unborn repository; 121 untracked files | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\rp2b-verify-20260831 | None configured | master<br>31f42893a0e7ed49cabea43397be133168c635ce | DIRTY: 11 status entries | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\rp2c-patch-base | origin: https://github.com/nervosnetwork/ckb-light-client.git | (detached HEAD)<br>a14703cfc33710986bccee011133aac34662bc0d | CLEAN (tracked + nonignored untracked status) | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\rp2d-r1-base-clean | origin: https://github.com/nervosnetwork/ckb-light-client.git | (detached HEAD)<br>12e29522ab7e078ada704d4ac04cbc0498009b7b | DIRTY: 7 status entries | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\upstream\ckb-light-client | origin: https://github.com/nervosnetwork/ckb-light-client.git | (detached HEAD)<br>12e29522ab7e078ada704d4ac04cbc0498009b7b | DIRTY: 118 tracked entries + 2,791 untracked files; see section 5 | Instrumented D2 upstream harness, heavily dirty. Read-only evidence: YES. Fresh clean source required for H02 tests. |
| C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\upstream\ckb-light-client\_work\rp2d-r1-patch-base | origin: https://github.com/nervosnetwork/ckb-light-client.git | (detached HEAD)<br>6143bcd343a0aab3ba8d55354c0fc46fca08cb7c | CLEAN (tracked + nonignored untracked status) | Experimental scratch/patch base (including committed experiments). Read-only evidence: YES. Do not use as a clean H02 baseline. |
| C:\Users\timot\Desktop\2026\CKB\fiber-latch | origin: https://github.com/Ticoworld/fiber-latch.git | master<br>ce60df74ae38f7d0ec8a1620b3cd007e4abb25ce | CLEAN (tracked + nonignored untracked status) | Outside the direct H02 reuse boundary; experiment status not investigated. Read-only inspection: YES. Leave unchanged; not an H02 test base. |
| C:\Users\timot\Desktop\2026\CKB\fiber-latch-test-flake | origin: https://github.com/Ticoworld/fiber-latch.git | fix/reconciliation-test-flake<br>009e84a009d08d7e17bca507f6bb0c2a79f6c547 | CLEAN (tracked + nonignored untracked status) | Outside the direct H02 reuse boundary; experiment status not investigated. Read-only inspection: YES. Leave unchanged; not an H02 test base. |
| C:\Users\timot\Desktop\2026\CKB\fiberflow | origin: https://github.com/Ticoworld/fiberflow.git<br>upstream: https://github.com/chukwuma619/fiberflow.git | fiberlatch-integration<br>96a96e26c7c3aeac9fcef486073586f88c3c6986 | CLEAN (tracked + nonignored untracked status) | Outside the direct H02 reuse boundary; experiment status not investigated. Read-only inspection: YES. Leave unchanged; not an H02 test base. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\repos\cellora | origin: https://github.com/Antismart/cellora.git | (detached HEAD)<br>a534c38f248c0406eeafee94adadb8c2c9072f8a | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\repos\ckb-light-client | origin: https://github.com/nervosnetwork/ckb-light-client.git | (detached HEAD)<br>12e29522ab7e078ada704d4ac04cbc0498009b7b | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\repos\light-client-snapshots | origin: https://github.com/phroi/light-client-snapshots.git | (detached HEAD)<br>3c5006d1ddb711939822a50e3c42d62b3ba5d7b3 | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\repos\neuron | origin: https://github.com/nervosnetwork/neuron.git | develop<br>9bca6e7d1e1885ad92410f172dbe9e7b958f0637 | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\repos\pocket-node | origin: https://github.com/RaheemJnr/pocket-node.git | (detached HEAD)<br>6eda0b7a4601050b011591d41cc702f0dc7a7c38 | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\PV1\repos\ckb-light-client | origin: C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\repos\ckb-light-client | develop<br>12e29522ab7e078ada704d4ac04cbc0498009b7b | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\PV1\repos\fiber-ffi | origin: https://github.com/joii2020/fiber-ffi.git | dev.ckb-light-cli<br>774ea9020bde7905acd9f0eec2c9acd46bfbd91d | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\PV1\repos\pocket-node | origin: C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\repos\pocket-node | main<br>6eda0b7a4601050b011591d41cc702f0dc7a7c38 | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\R-DEFERRED-ACTION\repos\btc-assets-api | origin: https://github.com/RGBPlusPlus/btc-assets-api.git | develop<br>a6f3af7aba7c83bed0c9d559367fb84eb690781e | CLEAN (tracked + nonignored untracked status) | Outside the direct H02 reuse boundary; experiment status not investigated. Read-only inspection: YES. Leave unchanged; not an H02 test base. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\R-DEFERRED-ACTION\repos\CrowdCell | origin: https://github.com/alesfer001/decentralized-kickstarter.git | main<br>805d75f403dafeced25c8ddb41e55c2e890bfa08 | CLEAN (tracked + nonignored untracked status) | Outside the direct H02 reuse boundary; experiment status not investigated. Read-only inspection: YES. Leave unchanged; not an H02 test base. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\d2-portability-proof | None configured | main<br>bec39d6764e2622139d4f0a93613126f64d4f5a5 | CLEAN (tracked + nonignored untracked status) | Historical PB1 prototype, not current D2 product. Read-only reuse: YES. Do not modify for H02. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\d2-portability-proof\_upstream\ckb-light-client | origin: https://github.com/nervosnetwork/ckb-light-client.git | develop<br>12e29522ab7e078ada704d4ac04cbc0498009b7b | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\grant_find\d2-portability-proof\_upstream\light-client-snapshots | origin: https://github.com/phroi/light-client-snapshots.git | master<br>3c5006d1ddb711939822a50e3c42d62b3ba5d7b3 | CLEAN (tracked + nonignored untracked status) | Reference source; no uncommitted experiment source changes detected. Read-only reuse: YES. Use a separate workspace if testing later. |
| C:\Users\timot\Desktop\2026\CKB\iBytes | origin: https://github.com/toastmanAu/iBytes.git | main<br>703ec09b1075fd34020cdfe7eff88eaa89c1b744 | DIRTY: 2 modified tracked files + 3 untracked examples | D2 experiment changes in wrapper/examples. Read-only reuse: YES. H02: fresh isolated checkout/worktree. |
| C:\Users\timot\Desktop\2026\CKB\iBytes\references\ckb-light-client | origin: https://github.com/Ticoworld/ckb-light-client.git<br>upstream: https://github.com/nervosnetwork/ckb-light-client.git | verified-historical-header-lookup<br>d6e1b491271b1a1d1c3577f3e6a95082bb3bdecb | CLEAN (tracked + nonignored untracked status) | Committed original historical-header prototype used by experiment wrapper. Read-only reuse: YES. Preserve branch/worktree family. |
| C:\Users\timot\Desktop\2026\CKB\iBytes\references\ckb-light-client-v2 | origin: https://github.com/Ticoworld/ckb-light-client.git<br>upstream: https://github.com/nervosnetwork/ckb-light-client.git | verified-historical-header-lookup-v2<br>f93dd5683a6c19d47850723d1d7d31b8cc37d734 | CLEAN (tracked + nonignored untracked status) | Committed PR #297 v2 candidate; clean is not merged/released. Read-only reuse: YES. Separate H02 worktree. |
| C:\Users\timot\Desktop\2026\CKB\remit | origin: https://github.com/Ticoworld/remit.git | feat/remit-mvp<br>976e690ad9cc3f9b5853a4483e7e7de83fd47c07 | DIRTY: 10 status entries | Outside the direct H02 reuse boundary; experiment status not investigated. Read-only inspection: YES. Leave unchanged; not an H02 test base. |

Important repository families:

- D2 master is 9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835. Its only nonignored untracked file is crates/d2-script-handoff/examples/ibytes_sqlite_handoff.rs. There is no tracked source diff.
- D2 also retains pre-public-history-backup at c8f6583ca8ca2ae2dfe8b850ac1048662d57a566. Older accepted G3 commit IDs in reports belong to this preserved history. For example, 6d9840902a4ce794b8ebe9a3ad38f816f864edf8 is contained by that branch. Do not remove it or treat the historical IDs as nonexistent because current public history uses different IDs.
- The _work/upstream/ckb-light-client repository owns three additional registered worktrees: _work/rp2c-patch-base, _work/rp2d-r1-base-clean, and _work/upstream/ckb-light-client/_work/rp2d-r1-patch-base. Their .git files depend on the parent Git metadata.
- iBytes/references/ckb-light-client owns the linked ckb-light-client-v2 worktree. Preserve both paths and their shared Git metadata.
- PV1/repos/pocket-node and PV1/repos/ckb-light-client have local-path origins pointing to D-BOOTSTRAP checkouts. They are not additional independent upstream authorities.

Non-Git top-level material also exists:

- C:\Users\timot\Desktop\2026\CKB\grant_find: research container, not itself a Git repository.
- C:\Users\timot\Desktop\2026\CKB\fiber-local-node: existing node/runtime data; not an H02 fixture.
- C:\Users\timot\Desktop\2026\CKB\fiber-local-toolchain: ckb-cli-v2.0.0, fiber-v0.8.1 and downloads.
- C:\Users\timot\Desktop\2026\CKB\my-ckb-app: application source and dependencies, but no Git root found.
- C:\Users\timot\Desktop\2026\CKB\.env and C:\Users\timot\Desktop\2026\CKB\key: existing sensitive-looking files; contents not inspected.

## 2. EXISTING D2 EVIDENCE

Evidence root: C:\Users\timot\Desktop\2026\CKB\ckb-script-port

Authority is established from report scope, Git history and supporting artifacts, not filename timestamps alone.

The current overall checkpoint is docs/D2_FINAL_CORE_PROOF_2026-10-01.md, committed at 9e8d6f6 on October 1. It states that core proof is complete for this stage and feature work is frozen pending upstream review. The prior production change is 56bcb95, which adds the bounded verified-header lookup fallbacks to D2. This inventory does not reopen those completed proofs.

| Existing material, relative to D2 root | Role and current interpretation | H02 reuse |
|---|---|---|
| README.md; docs/D2_V1.md | Product/API contract and supported profile, not a wallet recovery contract. D2_V1 last changed in d274224, September 8; read alongside the later core report and current code. | Reuse the contract and limits without expanding D2 scope. |
| docs/D2_FINAL_CORE_PROOF_2026-10-01.md | Latest committed overall proof/freeze report: iBytes recurrence, sparse H=72,000 boundary, funded transfer/spend equivalence, whole-store-copy control, limitations and local evidence register. | Primary starting record. |
| docs/PDEF1_D2_PRODUCT_SCOPE_FREEZE.md | Earlier scope freeze. | Historical boundary; not authorization to implement H02. |
| docs/G1_ACCEPTANCE_MATRIX.md | Product acceptance matrix, updated by G1-R1. | Completed lifecycle/contract acceptance. |
| docs/G1_R1_LIFECYCLE_EVIDENCE.md | Production facade plus pinned upstream protocol workers: H+1 continuation, negative refilter control, shallow reorg, importer races. | Reuse observations, runner design and instrumentation concepts. |
| docs/G2_SCALE_REALISM_REPORT.md; docs/G2_ACCEPTANCE_MATRIX.md | Synthetic scale/resource qualification. The report was corrected in e7ad806 on September 17. | Use the corrected complete-path comparison, not its broader introductory wording alone. |
| docs/G3_0_REFERENCE_CONSUMER_SELECTION.md | Selection/research history. | Background, not proof of adoption. |
| docs/G3_1_POCKET_REFERENCE_INTEGRATION.md | Initial Pocket source integration analysis. | Registration, native storage and app metadata mapping; later execution report controls actual execution claims. |
| docs/G3_1R1_POCKET_EXECUTION_EVIDENCE.md | Authoritative executable Pocket reference record. Current public-history file change: cdb63d8, September 10. | Reuse captured inputs, negative control, continuation/restart observations and same-store-copy comparison. |
| docs/G3_1_ACCEPTANCE_MATRIX.md | Acceptance record including execution qualification and failed/retried attempts. | Read with G3-1R1; do not turn failed setup attempts into current blockers. |
| docs/G3_FINAL_REFERENCE_PRODUCT_CHECKPOINT.md | Final bounded Pocket reference freeze, current public-history commit afd799f, September 11. | Preserves distinction between host-side D2 and Pocket app consumption; no app adoption claim. |
| docs/CKB_LIGHT_CLIENT_HISTORICAL_HEADER_LOOKUP_PROPOSAL_2026-10-01.md | Original maintainer-facing proposal and experiment design. | Historical rationale; local committed v1/v2 branches now supersede its “uncommitted patch” description. |
| docs/CKBUILDER_ISSUE_33_DRAFT_UPDATE_2026-10-01.md | Draft communication. | Preserve as draft; existence is not evidence it was posted. |
| docs/audits/D2_SOURCE_AUDIT.md; D2_RP1_REAL_UPSTREAM_REPROOF_PLAN.md; D2_RP2A/B/C/D reports | Earlier proof and audit lineage. | Supporting history; do not replace current product contract with experimental RP2 code. |

The production package exists at crates/d2-script-handoff/:
artifact.rs, operations.rs, error.rs, limits.rs, upstream.rs and pocket.rs.

Its crate version is 0.1.0. The core dependency/profile is pinned to official light-client commit 12e29522ab7e078ada704d4ac04cbc0498009b7b. The separate Pocket adapter is explicitly pinned to Pocket 6eda0b7a4601050b011591d41cc702f0dc7a7c38 / embedded light client 0.5.4 / kv-v1. These pins do not establish arbitrary-version compatibility.

Existing execution infrastructure:

- scripts/run-g1-cross-backend.ps1
- scripts/run-g1-r1-process-race.ps1
- scripts/run-g1-r1-protocol.ps1
- scripts/run-g1-r1-reorg.ps1
- scripts/run-g2-scale.ps1
- scripts/run-g2-protocol.ps1
- scripts/run-g2-interruption.ps1
- scripts/run-g2-reorg.ps1
- experiments/rp2-real-upstream/: schemas, manifests, observer/verifier code, comparison scripts and staged RP2 runners.
- patches/rp2/0001 through 0007: observer/negative controls; typed handoff; spendable fixture; cross-backend transport; reorg/crash tests; exclusive-import safety seam; commit-edge observability.
- benchmarks/ev1/r4/: separate controlled-protocol package and upstream.patch.

These scripts can create or mutate stores, apply patches and run processes. They were inspected, not executed. Future reuse requires new result roots and explicit PM-approved scope.

Verified raw evidence still exists under ignored paths, including both G1 direction continuation.json files, _work/g2-scale-realistic-20260909b/summary.json and both final stress summary.json files. They parsed as JSON during read-only inventory. Presence/parsing does not constitute a test rerun.

Historical research also exists at:
C:\Users\timot\Desktop\2026\CKB\grant_find\d2-portability-proof
and
C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP
and
C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\PV1.

PB1 has REPORT.md, README.md, source/tests, a Java RocksDB bridge and evidence/benchmark.json, multi-script.json, result.json and fail-closed material. It is a historical prototype, not the current Rust product or current H02 benchmark.

## 3. EXISTING POCKET WORK

Three usable local source checkouts were found before considering any download:

1. C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\g3-1-pocket-node
   Origin: https://github.com/RaheemJnr/pocket-node.git
   main at 6eda0b7a4601050b011591d41cc702f0dc7a7c38.
   No tracked source changes; 159 nonignored untracked evidence files.

2. C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\repos\pocket-node
   Same upstream origin and HEAD; detached; clean.
   Best existing clean source donor for the historical Pocket pin.

3. C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\PV1\repos\pocket-node
   Origin points to the preceding local checkout; main at the same HEAD; clean.
   Reference duplicate with existing local provenance.

Pocket's external/ckb-light-client is vendored source inside each Pocket checkout, not another independent Git repository. The inspected light-client-lib/Cargo.toml declares 0.5.4.

The D2 Pocket evidence directory is:
C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\g3-1-pocket-node\_g3-1r1-evidence

It contains 182 files total, including ignored logs as well as the 159 untracked files reported by the nested Pocket repository. The parent D2 repository ignores the whole _work/ tree. An apparently almost-clean D2 git status therefore conceals important captures.

Confirmed present:

- pocket-testnet-real-pocket-source-1.db (current file size 1,875,968 bytes)
- pocket-testnet-real-room-source-1.db (147,456 bytes)
- pocket-testnet-real-d2-r1-final.artifact (1,767 bytes)
- pocket-testnet-d2-clean-startup.log
- pocket-testnet-d2-clean-continuation.log
- pocket-testnet-d2-posth-restart.log
- pocket-testnet-d2-android-measure.log
- additional baseline/destination/restart DB captures, WAL/SHM companions, UI XML, screenshots, logs and conformance artifacts.

The G3 report identifies a Samsung SM-S9180, arm64-v8a, SDK 36; a debug Pocket build; H=22,370,055; host-side production D2; Pocket runtime continuation and restart. The capture is not an existing encrypted off-device H02 recovery implementation. Room captures contain an encrypted key_material row per the existing report; they must remain private evidence.

C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\g3-1-pocket-node-v1.8.3.apk also exists. The report distinguishes that release package from the debug build used for execution. Do not relabel it v1.8.5 or a current H02 test binary.

Local freshness limit: all three Git checkouts remain at the August 27 experiment pin. The newer Pocket research commit a23b4eb7d6408300a754f5711a0065b88b89ebfd is absent from all three checked object databases. Inspected local tag lists stop at v1.8.3; no v1.8.5 test checkout was found. No fetch was performed. A later approved update can use an existing repository/object store; a duplicate network clone is not justified.

## 4. EXISTING IBYTES WORK

Repository: C:\Users\timot\Desktop\2026\CKB\iBytes
Origin: https://github.com/toastmanAu/iBytes.git
Branch: main
HEAD: 703ec09b1075fd34020cdfe7eff88eaa89c1b744
Commit: August 31, “ci: align dependency audit policy.”
Embedded wrapper crate: rust/ckb-light-client-mobile, version 0.1.0.

This is the local base used for the D2 recurrence work; the reflog contains its clone at this HEAD. Reproduction requires the preserved local experiment changes, not merely checking out this commit:

Modified tracked files:
- rust/ckb-light-client-mobile/Cargo.toml: adds historical_header_lookup and handoff_resume_check example targets.
- rust/ckb-light-client-mobile/src/mobile.rs: adds the JSON request/poll bridge for historical-header proof lookup (and a small import-list change).

Untracked experiment examples:
- rust/ckb-light-client-mobile/examples/nonempty_state_checkpoint.rs
- rust/ckb-light-client-mobile/examples/historical_header_lookup.rs
- rust/ckb-light-client-mobile/examples/handoff_resume_check.rs

The manifest points through ../../references/ckb-light-client/light-client-lib. The original reference pin in docs/REFERENCE_SHAS.md is 12e29522ab7e078ada704d4ac04cbc0498009b7b. The current referenced checkout is the v1 historical-header branch at d6e1b491271b1a1d1c3577f3e6a95082bb3bdecb, whose parent is exactly that pin.

Thus the experiment lineage is:
iBytes 703ec09 + local wrapper/examples
→ upstream 12e29522 + original historical-header prototype, now committed as d6e1b49
→ D2 pinned adapter + local ibytes_sqlite_handoff.rs driver.

The October 1 report describes the bridge as uncommitted at the time. That description is historically useful but not the current Git state. No claim is made that today's mutable wrapper file hashes prove the exact historical executable bytes.

Do not silently substitute PR #297 v2:
- v1 request types are serializable structures containing height, candidate hash and anchor.
- v2 uses an opaque process-local request handle without the same serialization derives.
- The current iBytes JSON wrapper serializes/deserializes the v1 request.
Source inspection therefore identifies an adaptation requirement; the v2 worktree is not a drop-in path replacement. No compatibility build was run.

docs/REFERENCE_SHAS.md explicitly treats references/ as read-only. Keep this source family intact.

Other useful local iBytes material:
- CHAIN_PROVIDER_AND_SYNC.md
- docs/LIGHT_CLIENT_DEVICE_ACCEPTANCE_2026-08-30.md
- ios/Sources/iBytesApp/Services.swift
- ios/SyncPolicy/Sources/iBytesSyncPolicy/ScriptSyncPolicy.swift
- Rust mobile wrapper and existing sync_check example.
The physical-iPhone acceptance record belongs to iBytes' own development build; it is not a D2-on-iOS test.

Ubuntu WSL evidence was confirmed at:
/home/timot/ibytes-recurrence
Windows view: \\wsl.localhost\Ubuntu\home\timot\ibytes-recurrence

Existing evidence includes:
- run-20260930T132441Z/store/db.sqlite
- phase3-copy-destination-B/store/db.sqlite
- phase3-main-db-only-control/db.sqlite
- phase3-fresh-import-policy/store/db.sqlite, with WAL/SHM
- verified-lookup-source.log
- handoff-H72000-S-B.d2 (286 bytes)
- d2-fresh-destination/store, lookup.log and resume.log
- nonempty-state-A.d2 (1,020 bytes)
- nonempty-source/store
- nonempty-birthday-source/store, cells.json and source-snapshot.json
- nonempty-control/: store, cells.json and post-spend-cells.json
- nonempty-d2-destination/: store, cells.json, post-spend-cells.json and post-restart-cells.json
- wrong-proof/store.

Several stores retain nonempty WAL files. Preserve the database and its companions as one evidence set. No SQLite connection, checkpoint, integrity command or replay was run during inventory.

## 5. EXISTING CKB-LIGHT-CLIENT / PR #297 WORK

Clean historical official sources already exist at:
- C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\repos\ckb-light-client
- C:\Users\timot\Desktop\2026\CKB\grant_find\d2-portability-proof\_upstream\ckb-light-client

Both have official nervosnetwork origin and HEAD 12e29522ab7e078ada704d4ac04cbc0498009b7b. The PV1 copy is clean at the same revision but its origin is local.

The D2 harness source at:
C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\upstream\ckb-light-client
has the same recorded HEAD but is NOT a clean upstream checkout. Git reports 118 tracked status entries and 2,791 untracked files, mostly under its own _work/. Ignoring end-of-line differences reduces the substantive tracked diff to 16 files (603 insertions, 30 deletions in the inspected diff). There are also untracked observer/handoff/test files. Do not infer that all 118 entries are semantic changes, or that the directory is suitable as vanilla upstream.

The name rp2d-r1-base-clean is misleading today: it has a modified tests/utils/chain.rs plus six untracked files, including .rej patch rejects. Preserve it as historical patch-work evidence, not as a clean test source.

PR #297 source family:
- Main fork checkout: C:\Users\timot\Desktop\2026\CKB\iBytes\references\ckb-light-client
- Linked v2 worktree: C:\Users\timot\Desktop\2026\CKB\iBytes\references\ckb-light-client-v2
- origin: https://github.com/Ticoworld/ckb-light-client.git
- upstream: https://github.com/nervosnetwork/ckb-light-client.git

| Local branch | Commit | Meaning |
|---|---|---|
| verified-historical-header-lookup | d6e1b491271b1a1d1c3577f3e6a95082bb3bdecb | Original prototype on parent 12e29522; clean working tree; used by the current iBytes wrapper path. |
| verified-historical-header-lookup-v2 | f93dd5683a6c19d47850723d1d7d31b8cc37d734 | PR #297 candidate; clean linked worktree; matches the head identified in the preceding live research. |
| develop | 9ce5fc6507ce1379dd8bd4b947426078bb2062e8 | Official base object and local branch already present; no download needed to access this revision. |

v2 has two commits after 9ce5fc6: 2e6ca43 (implementation) and f93dd56 (API documentation). The inspected diff is six files, +1,360/-47, covering proof handling, peer/request state, service API/types and tests.

No standalone .patch named 297 was found. The committed fork branch/worktree is the stronger reusable source representation. The RP2 patches and EV1 upstream.patch are different experiment instrumentation and must not be confused with this PR.

This inventory did not contact GitHub or refresh refs. Local branch availability is confirmed; current merge/review status should be rechecked only when PM authorizes the next phase. Nothing here asserts that PR #297 has merged.

## 6. RELEVANT BENCHMARKS

| Evidence | Local location | Valid reuse and limitation |
|---|---|---|
| EV1 R4 controlled protocol comparison | C:\Users\timot\Desktop\2026\CKB\ckb-script-port\benchmarks\ev1\r4 | Tracked run.sh, parse-results.py, upstream.patch, fixtures.md, expected-schema.md and README. Reuse instrumentation/measurement definitions in a fresh result root. |
| Published R4 measurements | benchmarks/ev1/r4/results/REPORT.md; sparse-summary.json; moderate-summary.json | Sparse: 45.17 s baseline / 12.79 s D2 destination and total. Moderate: 28.62 s baseline / 6.29 s destination / 6.42 s total. Controlled pinned protocol/SQLite fixtures; not mobile/Internet/mainnet performance. |
| G2 native-filter replay and scale | docs/G2_SCALE_REALISM_REPORT.md; scripts/run-g2-scale.ps1; _work/g2-scale-*/summary.json | Corrected September 17: complete D2 path wins control/sparse but loses moderate/dense/unique/shared stress local replay cases on both measured backends. This differs from R4's protocol comparator. |
| G2 resource/closure stress | _work/g2-scale-stress-unique-20260909b; _work/g2-scale-stress-shared-20260909b | Existing final summaries, artifact-size and RSS/operation evidence. Not whole-wallet phone recovery. |
| G1/RP2 lifecycle controls | scripts/run-g1-*; experiments/rp2-real-upstream/; _work/g1-r1-* | Existing correctness, lifecycle and protocol-request observations. Do not reopen as H02 performance tests. |
| Pocket staging/continuation | docs/G3_1R1_POCKET_EXECUTION_EVIDENCE.md; nested _g3-1r1-evidence | Reported native+Room ADB copy: 1,884,160 + 147,456 bytes in 0.24 s. This refers to that captured transfer set, not every current DB filename. 142 ms launch invocation is not full restore time. |
| iBytes same-version copy | /home/timot/ibytes-recurrence/phase3-* and final D2 report | Existing positive copy control and fresh-import-policy rewind control. Preserved metadata determines continuation. No end-to-end H02 speed result. |
| PB1 tiny prototype comparison | C:\Users\timot\Desktop\2026\CKB\grant_find\d2-portability-proof\evidence\benchmark.json | Historical toy/prototype result; do not promote above later production evidence. |

The G2 introduction contains broader wording than its corrected complete-path section. For H02 comparison, use the corrected section and raw summaries, not an isolated introductory sentence.

Earlier EV1 R1/R2/R3 attempts and their build/run logs remain under D2 _work/. They include incomplete or superseded attempts and should remain evidence, not be selected by newest folder name alone.

The tracked R4 documentation uses /tmp run/build paths for reproduction. The current Ubuntu /tmp scan found no matching ev1/d2/ckb/ibytes/consumer/pocket/h02 entries. Therefore full old ephemeral R4 raw run roots were not confirmed locally; public summaries and the runner/patch package are present. Linux build caches under /home/timot/ev1-*, d2-target, d2-phase45-target, ibytes-target and ckb-light-client-target also exist, but are not immutable experiment source pins.

No H02 lost-device A/B/C or two-arm current-Pocket recovery benchmark was found.

## 7. LOCAL FILES WE MUST PRESERVE

Preserve these before any later checkout, cleanup, migration or experiment. This instruction is about retaining existing evidence; no backup/copy operation was performed now.

1. D2's untracked crates/d2-script-handoff/examples/ibytes_sqlite_handoff.rs.
2. Both modified iBytes files and all three untracked examples listed in section 4.
3. D2's pre-public-history-backup branch and the Git metadata linking all existing worktrees.
4. Entire C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\g3-1-pocket-node\_g3-1r1-evidence, including ignored logs and DB WAL/SHM companions.
5. D2 _work/g1-*, _work/g2-*, _work/ev1-*, _work/logs, helper scripts/build logs, historical source snapshots and patch scratch trees. Their classification as ignored/disposable does not authorize deleting them.
6. experiments/rp2-real-upstream/run/, run-rp2c/, run-rp2d/ and run-rp2d-r1/: local databases, crash/process logs, JSONL events, artifacts and manifests.
7. Uncommitted instrumentation and untracked test files in _work/upstream/ckb-light-client and the dirty RP2 scratch repositories, including .rej files.
8. Ubuntu /home/timot/ibytes-recurrence in full, including network identity directories. The report lists public-data evidence only; secret contents remain excluded.
9. C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\evidence and scratch; PV1/evidence and scratch. D-BOOTSTRAP includes REVISIONS.txt, importer-run.json and probe2/3/4 records. PV1 has evidence/summary.json.
10. C:\Users\timot\Desktop\2026\CKB\grant_find\d2-portability-proof\evidence, including packages, work data, fail-closed results and revision records; preserve .tools/ as existing reproduction support.
11. C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\g3-1-pocket-node-v1.8.3.apk and any existing debug build outputs as historical artifacts, not current release claims.
12. C:\Users\timot\AppData\Local\iBytes-D2-disposable exists and is the documented protected disposable-account location. Contents were not read. Also retain the documented WSL verified-lookup-network/secret_key without exposing it.
13. C:\Users\timot\Desktop\2026\CKB\.env and C:\Users\timot\Desktop\2026\CKB\key; contents were not read.
14. C:\Users\timot\.codex\attachments\b089f93a-49f6-40ef-a674-83fd1cf41bb7\Pasted text.txt is the prior evidence pack supplied in this conversation. Preserve it as handoff context, not a replacement for the Git/source inventory.
15. C:\Users\timot\AppData\Local\Temp\ckb-independent-research-20261005 exists from the preceding research. It contains downloaded source archives and selected current Pocket files, not a newly discovered complete Pocket Git checkout. It is supplementary research evidence, not the preferred H02 source workspace.

Current SHA-256 fingerprints of the six local experiment source files (recorded for preservation, not as claims about historical executable hashes):

| File relative to C:\Users\timot\Desktop\2026\CKB | Bytes | SHA-256 |
|---|---:|---|
| ckb-script-port/crates/d2-script-handoff/examples/ibytes_sqlite_handoff.rs | 4270 | afda6b79e5d6889d57c199edbe7133fb82f5b23371fa3f7de1c14ab0e8886d61 |
| iBytes/rust/ckb-light-client-mobile/Cargo.toml | 1235 | f16a286cdebe6c7af04f91c0f87237cdaa437e2bd4cc4d6d908b6012be295f3d |
| iBytes/rust/ckb-light-client-mobile/src/mobile.rs | 31038 | d9006b0741a7ad7b8ac03de7bbdb35d5ffc8cd4391f0f5c69f7d24ab0fc4bd9a |
| iBytes/rust/ckb-light-client-mobile/examples/handoff_resume_check.rs | 3290 | f2b57d68bbd953c0666092fc784338c7a89dba45a44454bb3098d44fa8455682 |
| iBytes/rust/ckb-light-client-mobile/examples/historical_header_lookup.rs | 4633 | 6e54ddfff08f148d2b37cf65b34bcb85e4b85d099fb3fd9f8d88fad710d99ebb |
| iBytes/rust/ckb-light-client-mobile/examples/nonempty_state_checkpoint.rs | 7537 | a984188ef5abe6b6d84c11f1ba6ed895f81d9c87f5705e159b62d2f24bbdc852 |

## 8. WHAT IS MISSING LOCALLY

Missing or not demonstrated, with the distinction kept explicit:

- No H02-specific directory, repository, code or local H02/PCK-P2 named file was found in the scanned workspace before this report. H02-P0 does not exist yet.
- No current Pocket Git checkout at the previously researched a23b4eb7 revision. The repository family exists; the newer revision is missing from the checked object stores.
- No verified Pocket v1.8.5 H02 test binary. The historical release APK and debug-flow evidence are older.
- No implemented off-device wallet-state package/recovery flow or whole-wallet lost-device benchmark was found in the inspected H02-relevant material.
- No evidence that the iBytes v1 JSON bridge is compatible unchanged with PR #297 v2; source inspection shows a concrete request-type difference.
- No independently verified cross-version Pocket recovery matrix, multi-populated-Script/DAO H02 acceptance result, or production mobile D2 integration is supplied by these existing files.
- Some earlier Linux /tmp raw benchmark and consumer-search workspaces are no longer present in the targeted scan. Do not assume historical report paths still exist merely because they are named.
- Additional iBytes reference repos listed in docs/REFERENCE_SHAS.md were not found as Git checkouts under references/. They are not established prerequisites for the bounded H02 inventory/decision and should not be downloaded automatically.
- Device availability, current installed wallet state, current TCP 8114 connectivity and build-tool readiness were not tested. These remain unassessed, not proven missing.
- No latest upstream freshness claim follows from offline Git refs. Inventory-only scope intentionally avoided network fetches.

The needed source families—D2, iBytes, Pocket, official light client and the PR #297 fork—are all already represented locally.

## 9. WHAT, IF ANYTHING, NEEDS TO BE CLONED

Nothing needs to be cloned for H02-P0 inventory or PM review.

No duplicate repository download is required. For a later current-Pocket experiment, PM may authorize fetching the chosen newer commit/tag into a designated writable source setup and creating an isolated working tree. Fetching a missing revision is different from downloading another duplicate repository.

Known reusable source donors:
- Historical Pocket: the clean D-BOOTSTRAP/repos/pocket-node checkout.
- Historical official light client: clean D-BOOTSTRAP/repos/ckb-light-client or d2-portability-proof/_upstream/ckb-light-client.
- PR #297 / newer official base: the existing iBytes reference fork's local objects and v2 branch.
- D2 library/report source: existing ckb-script-port, with its local example preserved separately.
- iBytes experiment: current base plus explicitly preserved local diffs/examples and original v1 reference branch.

An isolated checkout/worktree is safer than modifying any evidence-bearing tree. Creating a linked worktree updates the parent repository's Git metadata even if its source files remain untouched. If PM requires the source repositories to remain byte-for-byte unchanged, a later isolated local checkout using existing objects is preferable to attaching a worktree directly to them. Neither operation has been performed.

## 10. SAFE WORKSPACE RECOMMENDATION FOR H02-P0

Recommended future root:
C:\Users\timot\Desktop\2026\CKB\H02-P0

This path was checked and does not exist. Do not create it until PM reviews this inventory.

Suggested later separation, conditional on PM scope:
- docs/ for the approved experiment contract and provenance.
- worktrees/ or repos/ for isolated mutable test checkouts.
- evidence/ for newly produced run artifacts.
- runs/ for disposable per-run stores, never reusing old D2/iBytes capture paths.

No new project repository is required by the inventory itself.

Read-only source/evidence references:
- Entire existing ckb-script-port tree, including ignored _work/ and experiments.
- Entire existing iBytes tree and both reference light-client worktrees.
- All grant_find evidence and reference sources.
- Ubuntu /home/timot/ibytes-recurrence and protected account/network identity material.
- Unrelated CKB projects and node directories.

Safe to modify later: only newly isolated H02 working copies/result roots explicitly designated by PM. None of the existing evidence-bearing repositories is approved as an H02 mutation target. Clean donor checkouts are suitable for reading/pinning source; “clean” is not permission to repurpose them.

Reuse the completed D2 proof register, production adapters, Pocket storage/app-state map, iBytes ordinary-copy control and historical-header source. Do not start by recloning, replaying every completed D2 test, or modifying Pocket/D2 to fit a preconceived H02 architecture.

Inventory stop condition reached. Await PM review. No clone, implementation, H02 code creation or repository modification is authorized by this document.

## H02 LOCAL INVENTORY VERDICT

Existing ckb-script-port: YES — C:\Users\timot\Desktop\2026\CKB\ckb-script-port; master at 9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835; one untracked experiment example; preserve all ignored evidence.
Existing iBytes: YES — C:\Users\timot\Desktop\2026\CKB\iBytes; main at 703ec09b1075fd34020cdfe7eff88eaa89c1b744; two modified files and three untracked experiment examples.
Existing Pocket checkout: YES — three, all at 6eda0b7a4601050b011591d41cc702f0dc7a7c38; clean reference donor at C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\repos\pocket-node; device evidence in D2 _work/g3-1-pocket-node.
Existing official ckb-light-client checkout: YES — clean official-origin copies at C:\Users\timot\Desktop\2026\CKB\grant_find\ckb-boundary-probes\D-BOOTSTRAP\repos\ckb-light-client and C:\Users\timot\Desktop\2026\CKB\grant_find\d2-portability-proof\_upstream\ckb-light-client, both at 12e29522ab7e078ada704d4ac04cbc0498009b7b; additional instrumented/copy/worktree sources also exist.
Existing PR #297 fork/worktree: YES — C:\Users\timot\Desktop\2026\CKB\iBytes\references\ckb-light-client-v2; verified-historical-header-lookup-v2 at f93dd5683a6c19d47850723d1d7d31b8cc37d734; clean; shares Git metadata with the preserved v1 fork checkout.
Existing H02-specific workspace: NO — none found in the inspected workspace; only this inventory file has now been created.
Repos actually missing: NONE of the required repository families. The newer Pocket revision/test build and H02-specific implementation/results are absent; those are not missing repository families.
Recommended H02 working directory: C:\Users\timot\Desktop\2026\CKB\H02-P0 — proposed only, not created.
Repositories that must stay read-only: all existing D2, iBytes, Pocket, official/forked light-client, historical proof and research checkouts; preserve their worktree metadata and ignored evidence.
Repositories safe to modify later: only PM-designated new isolated H02 working copies; no existing evidence repository is nominated for in-place edits.
Duplicate download required? NO
Reason: all required source families and PR #297 source already exist locally. Reuse pinned local sources and preserve evidence; obtain a missing newer revision only through a later PM-approved update, not another duplicate clone.
