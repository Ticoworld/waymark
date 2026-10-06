# WO-3B2-R2 SOURCE result

**Full SOURCE correctness: FAIL at canonical DAO compensation. B2-INCONCLUSIVE before H2.** Two-account recovery, mapping, native history/live Cells, spendable balances, deposited-position metadata and restart succeeded. The cached DAO reward estimate is wrong, so the PM instruction ?Do not continue if SOURCE itself is incorrect? stops backup and A/B execution.

Pocket v1.8.5 / code 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`; APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. TESTNET only. API 36 x86_64, 2048 MiB, two vCPUs, WHPX, Intel Iris Xe host GPU, headless, no snapshots. Explicit ADB serial `emulator-5580`. No SwiftShader, production source changes, physical Samsung access or D2. B1 evidence remains unchanged.

## Freshness, environment and storage

Only SOURCE ran, under `runs/wo3b2/source/avd`, AVD `H02_P0_API36_X64`; 6 GiB userdata. `disk-before.json` proves no userdata/encryption backing before boot. `boot-retry1/provision.json` proves the approved APK hash/version, absent pre-install package, and absent Room DB/native TESTNET store/Pocket preferences/key-backup directory before first launch. No prior guest keys or snapshot were reused.

First fresh boot had one SystemUI service ANR **before Pocket installation**. The original refusal was preserved. A 200.48-second Android-only qualification then passed seven Settings/Home/system-server checks without new ANRs/crashes. Continued provisioning required that exact preserved baseline and >=180 seconds of stable observations. Host GPU/configuration was unchanged. This exception is documented, not counted as a completely ANR-free first boot. Native sync later paused when proved peers were unavailable, then resumed without intervention. No new Android ANR was observed at the stall check.

| Storage point | Bytes | GiB |
|---|---:|---:|
| Before SOURCE | 15,891,755,008 | 14.800 |
| Lowest recorded during SOURCE | 9,979,498,496 | 9.294 |
| After stopped emulator shutdown | 12,134,785,024 | 11.301 |

The 10 GiB pre-launch threshold passed. No extra cleanup occurred; samples stayed above the 1.5 GiB live reserve. ?Lowest recorded? is sampled, not a continuous peak measurement. Shutdown freed transient emulator backing; **no runtime-retirement script was executed**. The incomplete SOURCE userdata is retained for diagnosis, as required by the low-space plan. A2/B2 were not created.

## Recovery, coverage and exact position checks

Normal phrase/PIN flow was automatic; first key/security completion took 44.061 seconds from first Pocket launch. TESTNET/CUSTOM registration was requested at 107.766 seconds. Account 1 came from Pocket's supported Add account flow, not row insertion. The actual public keys were also checked by decrypting only local V1 key rows inside the emulator app UID and signing a random public challenge with the shipped Pocket signer; independent host verification matched both expected Scripts. No key bytes crossed that boundary. This proves emulator V1 signing readiness, not physical-phone V2 authentication.

Immediately after account creation, Home/Settings had stale active-account context. An attempted account-1 coverage setting was saved against account 0. The first frozen check rejected `coverage-mode`. Normal account switching and Settings corrected both policies; an allowlisted preference observation and subsequent frozen snapshots verified account 0 CUSTOM 22,369,937 and account 1 CUSTOM 22,647,000. The new continuation helper explicitly switches through Home and verifies the public address before changing coverage. No production workaround or DB write was used.

Discovery finished with 50 EMPTY probes and one RESTORED account-1 candidate. The remaining probes caused a normal historical replay after restart, as B1 had also observed. Exact initial account-0 reconstruction passed before any new transaction. Two real populated Scripts and the DAO position then matched `oracle-deposit.json`, including per-account Room history and spendable balance. The account histories are disjoint because funding uses a separate relay.

After the populated-state restart: native verified tip 22,647,479; global minimum/filter progress and both owned registrations 22,647,478; both Room saved cursors 22,647,478; latest registration starts 22,647,468; zero pending matched work. These resume cursors differ from the preserved historical coverage floors. Selected account is 1, network TESTNET, strategy ALL_WALLETS. Both public identities, parent mapping, exact live outpoints and known history remain correct. Complete rows and native logical snapshot are retained at `source/preH2-restart/`.

## Canonical DAO compensation failure

The real deposit is owned by account 1 and correctly cached as DEPOSITED, with principal 100,000,000,000 shannons, deposit block 22,647,433/hash/epoch matching the canonical header. Its compensation field does not match the canonical occupied-capacity formula:

`reward = floor((capacity - occupied) * AR_tip / AR_deposit) + occupied - capacity`

AR is the little-endian accumulated rate in bytes 8?15 of the canonical header's DAO field. This Cell occupies **102 CKB**, not 61 CKB.

| Frozen observation | Room compensation | Matching canonical header for Pocket's 61-CKB calculation | Correct 102-CKB reward at that header | Excess |
|---|---:|---:|---:|---:|
| Before restart | 8,010 shannons | 22,647,449 | 7,661 shannons | 349 shannons |
| After restart | 22,530 shannons | 22,647,478 | 21,546 shannons | 984 shannons |

The audit fetched every canonical header from the deposit through each frozen native tip, verified contiguous parent links and both canonical anchors, and found **no** header whose correct 102-CKB calculation equals either stored value. Each value exactly matches the 61-CKB calculation at the indicated header. Room does not persist an estimate-as-of header: the matching height is inferred from the exact integer calculation, not represented as an observed app RPC call. Headers and all computed values are retained in `source/dao-compensation-audit-first.json` and `dao-compensation-audit-restart.json`.

Pinned source explains both observations: `android/app/src/main/java/com/rjnr/pocketnode/data/gateway/DaoDepositReader.kt:243` and `:263` pass literal `61_00000000L` to `nativeCalculateMaxWithdraw`. The native `bridge_core/dao.rs:142` applies the formula to the supplied occupied value without adding DAO bytes. `DaoConstants.kt:26` explicitly defines the correct DAO occupied capacity as 102 CKB. This is an existing **Pocket DAO reader/application-cache calculation defect**, before any H02 restoration; native chain state is correct. The actual unlock builder in `GatewayRepository.kt:3197` uses the correct constant. We have not demonstrated a bad unlock transaction, lost principal, or a consensus/native indexing defect.

The earlier `source/dao-acceptance.json` and `populated-state-first-acceptance` timing marker covered position/mapping/history only; they did not check compensation and are preserved as intermediate evidence, **not full SOURCE PASS**. The checker now explicitly returns POSITION_ONLY_PASS for that narrower check and refuses full acceptance/export without a canonical compensation audit. Both retained captures fail the full gate. Five regression cases passed, including rejection before any export RPC, ADB operation or package creation.

## Halt and preservation

No H2 selected, no package/security-package verdict, no post-H2 transaction, no F2, no source-loss declaration, no A2/B2. SOURCE was force-stopped/disabled and the emulator shut down at 2026-10-06 00:33:26 UTC. The runtime remains for diagnosis; no further DAO transition was attempted. `source/HALTED.json`, `result.json` and the 69-file `source/evidence-seal.json` record this boundary. The seal explicitly denies runtime retirement because full acceptance did not pass.

SOURCE preparation includes UI correction, network stalls, investigation and instrumentation; it is not an A2/B2 recovery-time measurement. No product-speed claim. Original failed B2 reports were archived with prior hashes in `runs/wo3b2-r2/previous-b2-reports/`; storage/R1/B1 evidence and preexisting helpers remain unchanged.
