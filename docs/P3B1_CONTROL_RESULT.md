# WO-3B1-R2 Control A: PASS

Normal supported recovery on fresh independent userdata converged to the independent F oracle and remained correct across restarts. No sanitized package was supplied to A. SOURCE was already stopped/sealed and was not consulted.

## Environment and normal recovery

API36/default/x86_64 rev2, 2048 MiB, two vCPUs, WHPX, HOST GPU/Intel Iris Xe, headless/no audio/no snapshots, effective 6 GiB data partition. Registry `runs/wo3b1-r2/control/avd`; AVD `H02_P0_API36_X64`; serial `emulator-5580`. Fresh installation and responsive Android were checked before Pocket's first launch. Same Pocket v1.8.5/code27 at `b28979de744798ffb75367b031d4871ec3af1a12`; APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`.

Automated normal UI: retained private phrase, no-device-lock consent, new app PIN, background sync only while open, Settings network switch to TESTNET, normal unlock, CUSTOM height 22,369,937. No manual phrase entry, key-row injection, production modification or RPC-state import. The normal default RECENT window would miss this fixture; the correct floor is applied before measured reconstruction. Only one actual account is created. Its independent UUID is `0bbe6c2a-b173-413a-b273-cd64111bbe71`.

## Acceptance

Network TESTNET; account `m/44'/309'/0'/0/0`; CUSTOM coverage start **22,369,937**; accepted through F **22,646,322**. Exact capacity **1,999,999,998,000 shannons = 19,999.99998 CKB**. No DAO. Shared semantic SHA-256: **`13cb9e9b74c918a9fe27bb9a9205545125998bfcb86fb5f02408a23db754567a`**.

| Final live outpoint | Capacity (shannons) |
|---|---:|
| `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66:0` | 1,000,000,000,000 |
| `0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7:0` | 10,000,000,000 |
| `0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7:1` | 89,999,999,000 |
| `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894:1` | 899,999,999,000 |

Covered history (four unique transactions):

- `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66`
- `0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7`
- `0xb7503283af42a8fd1595306e2d5dd4a789e103980207fdafb5229b2e20b7113c`
- `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894`


Checks cover decoded public account/Script identity, exact native Cells/capacities, native and Room history, confirmed/nonlocal Room records, exact Room balance ownership, explicit coverage, primary/native/Room progress through F, zero matched work, no unexpected funded Script and no DAO. U `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894:0` is absent; both owned outputs of the post-H transaction are present.

First exact acceptance: 22:01:34.020656 UTC, native verified tip 22,646,434, global/primary/Room progress 22,646,432. Five discovery candidates were PENDING, 46 EMPTY. The ordinary restart registered the remaining five and performed another historical filter pass. This same behavior was observed on SOURCE before backup. The primary accepted wallet state persisted while Pocket disabled spending until discovery caught up.

Second exact acceptance: 22:11:04.349319 UTC, all 51 candidates EMPTY, same semantic hash. A further normal restart remained settled and produced the same hash. Final native verified tip **22,646,514**, global/primary filtered **22,646,513**, Room saved **22,646,512**, latest registration start **22,646,507**, no matched work. These cursors exceed F and resume coherently. Probe Scripts are Pocket's normal discovery metadata; no additional wallet/account was created or populated.

## Measured time

Timer: **2026-10-05T21:48:13.479538+00:00** before first Pocket launch to **2026-10-05T22:12:26.551481+00:00** after the last exact restart check. Android provisioning/APK installation precedes this timer. UTC marks and host monotonic readings are in `control/events.jsonl`.

| Requested phase / observation | Seconds | Meaning |
|---|---:|---|
| T_key_recovery | 35.589986 | First launch through normal keys/security setup |
| T_registration | 52.720044 | Observed network-switch/coverage UI interval; background registration itself is not separately instrumented |
| T_historical_reconstruction | Not isolated | First combined reconstruction/catch-up/app reconciliation/exact-check interval is **712.232130 s** from correct coverage request |
| T_catchup | Not isolated | Included in the scan/reconciliation interval; no invented independent value |
| T_app_reconciliation | Not isolated | Included above; initial UI balance updates when normal scan completes |
| First exact F-state acceptance from launch | **800.542161** | **13 min 20.542 s**, before the discovery-triggering restart |
| Second discovery pass plus restart/check interval | 570.329403 | First exact acceptance through after-first-restart exact acceptance |
| Final settled restart/check interval | 82.202266 | Includes unlock, two public settled observations and frozen exact check |
| T_total | **1,453.073830** | **24 min 13.074 s**, complete restart-qualified acceptance |

These inclusive observed intervals include helper/validation/polling time. Public watchers sample about every 33 seconds and exact checks quiesce the app. They are not pure internal LC runtimes. First-state timing and full continuation timing are both retained so discovery costs remain visible. The full restart endpoint adds **652.531669 s** after first exact acceptance.

## Evidence and disposition

`runs/wo3b1-r2/control/`: `boot/launch.json`, `boot/provision.json`, `events.jsonl`, `reconstruction-pass1.jsonl`, `first-restart.jsonl`, `final-restart.jsonl`, the three `*-acceptance.json` files, matching frozen public observations and `result.json`. The independent oracle is `oracle-F.json`. `comparison.json` validates the common semantic state against Candidate B, and `public-final-check.json` rechecks canonical H/F and unchanged public fixture state.

The Control emulator was stopped after PASS. No production source changes, physical phone, D2, extra account, DAO or additional transaction. **LIMITED PERFORMANCE FIXTURE**; no production speed conclusion.

The previous environmental B1-INCONCLUSIVE reports are preserved with checked SHA-256 hashes in `runs/wo3b1-r2/previous-b1-reports/`. Original run artifacts, R1 diagnosis and qualified profile remain unchanged.
