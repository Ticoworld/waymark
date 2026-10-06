# WO-3B2-R2 comparison

**B2-INCONCLUSIVE: no A2/B2 comparison exists.** The blocker moved from host storage to a reproducible, pre-backup Pocket DAO compensation error in SOURCE. B1 remains PASS; no B1 timing run was repeated.

Pocket v1.8.5 / code 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`; APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. TESTNET only. API 36 x86_64, 2048 MiB, two vCPUs, WHPX, Intel Iris Xe host GPU, headless, no snapshots. Explicit ADB serial `emulator-5580`. No SwiftShader, production source changes, physical Samsung access or D2. B1 evidence remains unchanged.

| Dimension | SOURCE observation | Control A2 | Candidate B2 |
|---|---|---|---|
| Normal recovery / both public identities | PASS | Not run | Not run |
| Supported parent/account relationship | PASS | Not run | Not run |
| Two populated Scripts / exact native Cells | PASS | Not run | Not run |
| Spendable balances / covered history | PASS | Not run | Not run |
| Real DAO principal/owner/deposit metadata | PASS | Not run | Not run |
| DAO cached compensation | FAIL, reproduced after restart | Not run | Not run |
| Full canonical SOURCE acceptance | FAIL | N/A | N/A |
| Restart of position/mapping/history | PASS | Not run | Not run |
| H2 / post-H2 / F2 | Not reached | Not run | Not run |

Semantic equivalence of A2/B2: **not established**. SOURCE's two position-only snapshots agree with canonical Cells/history while reward estimates remain wrong. A2/B2 could conceivably reproduce the same erroneous estimate, which would not meet canonical correctness. No such outcome is claimed.

## Timing and storage

Normal SOURCE key/security recovery: 44.061 s. Initial TESTNET/custom registration: 107.766 s after first launch. First exact pre-funding check: 2,272.801 s; populated-state position-only check: 2,778.325 s. These intervals include automation correction, discovery replay, variable peer stalls, instrumentation and operator investigation. They are preparatory observations, not controlled reconstruction measurements. A2 total, B2 total, package size/export/restore/catch-up: **not measured**.

Free space: 14.800 GiB before SOURCE, lowest sampled 9.294 GiB during SOURCE, 11.301 GiB after shutdown. No cleanup/retirement ran. A2/B2 pre-launch space is unmeasured because neither role began. Only one runtime was created; it is retained because source correctness was incomplete. The 10 GiB pre-launch guard and 1.5 GiB live reserve were respected.

Performance fixture remains LIMITED. No production speed claim or new speed ratio is supportable. `oracle-halt.json` rechecks that all fixture Cells/history remained unchanged after the deposit; tip 22,647,505 is an audit observation, not the experiment's F2.
