# WO-3B2-R4 comparison

**A2 and B2 are canonically equivalent at F2: B2-PASS.**

Pocket v1.8.5/code 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`; approved APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. TESTNET. API 36 / x86_64 / 2048 MiB / 2 vCPUs / WHPX / Intel Iris Xe HOST GPU / headless / no snapshots. Explicit emulator serial `emulator-5580`. Physical Samsung untouched; D2 excluded; production Pocket source unchanged.

| Acceptance item | Control A2 | Candidate B2 |
|---|---|---|
| Normal key/account recovery and parent association | PASS | PASS |
| Both exact Scripts and distinct owned state | PASS | PASS |
| F2 live Cells, balances and covered histories | PASS | PASS |
| Account-0 stale-U removal/new state | PASS | PASS |
| Account-1 post-H2 activity | PASS | PASS |
| DAO canonical position and account association | PASS | PASS |
| Known reader compensation defect only | PASS | PASS |
| Per-Script/native/Room progress and settled discovery | PASS | PASS |
| Two-account local signing readiness | PASS | PASS |
| Restart semantic persistence | PASS | PASS |

Both canonical semantic hashes: `0f9c153bd08918b9231c4b32131f9552e9bb3a515833795e7066e017e749190e`. UUIDs, cache timestamps, native tips beyond F2, and tip-dependent compensation values are deliberately retained as observations rather than treated as equal wallet semantics. Known estimate values are independently matched to the same 61-CKB algorithm at each tightly bounded canonical header interval; raw reward numbers at different tips are not directly compared.

| Observation | Inferred estimate header | Pocket compensation (shannons) | Canonical compensation (shannons) | Cache age at capture (ms) |
|---|---:|---:|---:|---:|
| SOURCE H2 | 22652548 | 2560902 | 2449084 | 21969 |
| control r4-canonical-first | 22652907 | 2740637 | 2620971 | 36632 |
| control r4-canonical-restart | 22652930 | 2752152 | 2631983 | 38220 |
| candidate r4-first | 22653011 | 2792705 | 2670766 | 40388 |
| candidate r4-restart | 22653038 | 2806222 | 2683693 | 30958 |

A final independent public-chain recheck at tip 22653056 confirmed the exact F2 live sets, histories and capacities remain unchanged. Raw evidence: `runs/wo3b2/oracle-final-recheck.json`.

| Measurement | Value |
|---|---:|
| A2 total, including restart acceptance | 2239.181 s |
| B2 total, including restart acceptance | 730.317 s |
| H2 package | 1,904,717 bytes |
| Package export | 4.398 s |
| Package restore including gates/activation | 15.961 s |

**LIMITED PERFORMANCE FIXTURE.** This run tests correctness across richer wallet state. Totals include host/UI accommodations, discovery replays, auditing and restart. No production speed claim or generalized multiplier is justified. Detailed event timestamps and bounded watcher samples are retained per arm.

Nine disposable-copy package tests rejected corruption, missing payload, wrong network/genesis, unsupported Pocket/Room/native versions, manifest-digest mismatch and payload-hash mismatch before activation. Results are under `runs/wo3b2/negative-packages/`. No production source changes were made.
