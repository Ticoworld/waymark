# WO-3B1-R2 Candidate B: PASS

Normal key recovery followed by the sanitized same-version H package converged correctly after the deliberately stale event. B removed U, discovered the post-H transaction and both new owned outputs, rebuilt application caches, and retained exact state through a normal restart.

## Isolation and activation

Fresh independent registry `runs/wo3b1-r2/candidate/avd`, AVD `H02_P0_API36_X64`, serial `emulator-5580`. Same qualified API36/x86_64/2048 MiB/two-vCPU/WHPX/HOST-GPU/headless/no-snapshot profile and same v1.8.5 APK digest `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. A was stopped before B booted. SOURCE had been sealed since 21:46:19 UTC and was never reopened.

B used the normal automatic phrase/PIN flow, TESTNET and CUSTOM floor 22,369,937. Independent destination wallet UUID: `48d199fa-779b-44f4-a44a-4a106120eb0f`. The restore plan matched destination-derived public addresses, exact Scripts, account path and discovery identities, then translated source metadata IDs to this new UUID. Existing destination key records were byte-digest checked before/after the allowed Room changes; source key/PIN/Keystore material was never included. Normal PIN unlock and later restart also succeeded.

Input: `package-H-immutable/`, **1,895,341 bytes**, profile `h02-p0-b1-one-account-v1`, H **22,646,283**, manifest SHA-256 `f89fc4feeb019b47b625be8df71f5ef9cd64acdf2104cd793f113e0c9530fd12`. After activation and before Pocket launch, installed native store SHA-256 exactly equaled H payload SHA-256 **`93792af4a841e5db03190aabb1749d4510b6665117a080ec12997387119fa719`**. Thus B began with the stale U-bearing package, not a post-F source or Control DB.

Only logical native state and approved public app/discovery/progress/preferences were restored. Destination-owned secrets stayed in place. TESTNET transaction/balance/header/DAO caches were cleared for normal reconstruction. Stage/commit used the existing quiesce/disable/journal procedure. All version, APK, network/genesis, schema, hash and public mapping gates passed.

## Stale-state convergence and restart

The H package contains U as live and has three historical transactions. The only post-H transaction is `0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7`, confirmed at 22,646,305. It spends exactly U and creates owned outputs :0 and :1. The independent final oracle shows U non-live (`get_live_cell` literal status `unknown`) and the committed transaction supplies its spend evidence.

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


First B exact acceptance: **22:17:24.996210 UTC**. Native verified tip 22,646,547; global/primary and Room saved progress 22,646,545; registration start H. Zero matched work, all 51 discovery rows EMPTY. No history replay from the September floor was observed. Normal startup resumed the primary Script at H.

After force-stop/disable, normal enable/launch/PIN and catch-up, exact acceptance passed again at **22:18:49.360314 UTC**, with the same semantic hash. Final native verified tip **22,646,557**, global/primary and Room saved progress **22,646,553**, latest registration start **22,646,545**, zero matched work, all discovery EMPTY. U remains absent and all four final Cells/history/balance remain correct. No new signing transaction was needed to test restore.

## Measured time

Timer: **2026-10-05T22:13:56.222130+00:00** before first Pocket launch through **2026-10-05T22:18:49.361601+00:00** after restart acceptance. Android provisioning/APK installation is outside the requested first-launch timer. All package operations are inside it.

| Requested phase / observation | Seconds | Meaning |
|---|---:|---|
| T_key_recovery | 35.107705 | Normal supported keys/security setup |
| Network/coverage UI | 46.365276 | Normal TESTNET switch/restart and CUSTOM floor |
| T_package_transfer | 0.642551 | Approved plan/destination projection/native payload transferred to app-private staging |
| T_validation | 0.630665 | Initial host package validation; later mapping/rechecks are also included in total package time |
| T_restore: staging | 1.303640 | Transfer completion to staged-state validation |
| T_restore: activation | 1.962656 | Activation begin to commit completion |
| Total package operation | **8.480067** | Includes validation, quiescence, helper setup, destination mapping/rechecks, transfer, staging, activation and enable |
| Other package overhead | 3.940555 | Included in package total, not omitted from recovery time |
| T_light_client_start | Not isolated | Recorded launch-request to normal unlock interval **9.826991 s**; native-ready instant was not separately instrumented |
| T_post_H_catchup | Not isolated | Unlock through catch-up/app reconciliation/exact acceptance is **106.083915 s** inclusive |
| T_app_reconciliation | Not isolated | Included in the preceding interval; exact regenerated app state is checked |
| First exact F acceptance from launch | **208.774346** | **3 min 28.774 s** |
| Restart/check interval | 84.365502 | Normal unlock, settled observations and exact persistent-state check |
| T_total | **293.139849** | **4 min 53.140 s** |

There is also 2.909268 s between correct coverage request and package operation start, plus marker/dispatch overhead; T_total includes every gap. Timings are observed inclusive wall-clock intervals, not isolated chain algorithms. Watcher sampling and exact checks add overhead. No production-user speed multiplier is claimed.

## Negative gates and evidence

All nine disposable real-package variants were refused **before device activation**: corrupt payload, missing app payload, wrong network, wrong genesis, unsupported Pocket version, unsupported Room schema, unsupported native schema, manifest digest mismatch and payload hash mismatch. For semantic negative cases, the test deliberately recomputes the test-copy trusted digest so rejection reaches the semantic gate. Production restore used the independently retained original manifest digest. No full recovery was repeated for rejected packages.

Evidence: `candidate/activation-receipt.json`, `candidate/events.jsonl`, `candidate/catchup-first.jsonl`, `candidate/first-restart.jsonl`, two frozen observations and `*-acceptance.json`, `candidate/result.json`, `negative-packages/*/result.json`, `comparison.json`, `oracle-F.json`, `oracle-validation.json`, `public-final-check.json`. `r2_compare.py` reads the retained H package and both accepted public semantic results to enforce U membership/removal and A/B equivalence. It never reads sealed SOURCE native/Room state.

Candidate was disabled after the last exact check, then its emulator stopped. No physical phone, D2, production source change, extra account, DAO, cloud integration or B2 execution. **LIMITED PERFORMANCE FIXTURE**.

The previous environmental B1-INCONCLUSIVE reports are preserved with checked SHA-256 hashes in `runs/wo3b1-r2/previous-b1-reports/`. Original run artifacts, R1 diagnosis and qualified profile remain unchanged.
