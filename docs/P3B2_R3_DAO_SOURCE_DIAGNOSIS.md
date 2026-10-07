# WO-3B2-R3 DAO source diagnosis

**DAO-POCKET-DISPLAY-BUG.** The oracle's 102 CKB occupied capacity is correct for this exact Cell. Pocket v1.8.5's DAO reader supplies 61 CKB, producing an overstated compensation estimate that is then stored in Room. The defect exists before restart and before any H02 export or restore. The pinned transaction path independently uses 102 CKB; this discrepancy does not feed its withdrawal/unlock output amount. That impact conclusion is from code tracing, not an executed mature unlock.

B2 can continue on the unchanged approved build **only after PM approves the explicit active-position acceptance contract below**. R3 does not revise the existing gate or resume B2. The R2 SOURCE result remains historically INCONCLUSIVE under its original compensation-inclusive gate.

Pocket: v1.8.5, versionCode 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`. Approved APK: `runs/wo2/gradle/app/outputs/apk/debug/app-debug.apk`, SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. The checkout remains clean. SOURCE is the retained API-36 x86_64 host-GPU runtime at `runs/wo3b2/source/avd/H02_P0_API36_X64.avd`, stopped with Pocket disabled. It was not booted, wiped, migrated, exported, or declared lost during R3. No wallet secret was read; no transaction, recovery, cleanup, phone access, D2 work, production patch, or external message occurred.

The initial resumed disk reading was 12,121,845,760 bytes (11.29 GiB); the automated preservation capture recorded 12,177,276,928 bytes (11.34 GiB). These are separate host samples, not reclaimed storage. Final free space is recorded in `runs/wo3b2-r3/preservation-after.json`. The 69 files in the existing SOURCE evidence seal were hash-verified. All 33 retained AVD files were inventoried by path, size and last-write time, without copying their contents. The runtime's logical file size is 2,908,960,702 bytes. Its evidence seal still prohibits retirement.

The exact position and comparison boundaries follow. All values are public TESTNET facts; mainnet was not queried or conflated with this position.

| Fact | Value |
|---|---|
| TESTNET genesis | `0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606` |
| Deposit transaction | `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2` |
| Output | `0x0` |
| Capacity | `0x174876e800` = 100,000,000,000 shannons = 1,000 CKB |
| Data | `0x0000000000000000` (8 bytes; active deposit) |
| Lock code_hash | `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8` |
| Lock hash_type / args | `type` / `0x2da024570462b0e2421d87abcbfebd4567d52ad5` |
| Type code_hash | `0x82d76d1b75fe2fd9a27dfbaa65a039221a380d76c926f378d3f81cf3e7e13f2e` |
| Type hash_type / args | `type` / `0x` |
| Owner lock Script hash | `0x29958c7362d950f80cdb5994d47e408b38a4d2cc5e41f7a0087214ff3f421a24` |
| Deposit block | 22,647,433 (`0x1599289`) |
| Deposit block hash | `0x7cb42962be61200f1b21caec71cdf4be5387b706b647bf8bfaa869346ce8a2e5` |
| Deposit epoch | `0x7080128003681` = 13,953 + 296/1,800 |
| Deposit timestamp | 1,791,246,343,189 milliseconds |
| Pocket account | account 1, `m/44'/309'/1'/0/0`, UUID `36ac4ecb-c83e-4a00-96db-09f2d6be58a7` |
| Parent | account 0, UUID `043746a4-de6d-4911-8e00-5d663bdb0e37` |
| Room state after restart | DEPOSITED; exact principal/outpoint/header/epoch/owner; withdraw/unlock metadata null |
| Current public observation | `get_live_cell(..., true)` = **live**, exact output/data match |

Public RPC `https://testnet.ckb.dev` returned the same full transaction and deposit header as the sealed R2 confirmation. Capture time was 2026-10-06 01:02:45 UTC; separately observed live chain tip was 22,647,707, hash `0x1ae6e33f7f8177cfbd368eb67ce520dd20f4a24ccc2c1ae8044e96a110748755`. That advancing public tip is **not** the boundary of the old Room estimate.

The frozen post-restart native tip is **22,647,479**, hash `0x99ef14db02815b107748ffc902bb91293e2791364f5906dea0ffc6507eadff21`. Native global/per-Script progress and both Room saved cursors are 22,647,478. The compensation comparison uses the explicit historical header **22,647,478**, hash `0x92579b1939123c32c33dc77d1fedb3fbd2853d917061a0c08556ac0fca3fcdb7`. Room stores a timestamp, not a compensation-as-of header. This matching estimate height is an **inference from exact integer agreement**, not an observed return value of Pocket's `nativeGetTipHeader()` call. Both the comparison header and actual captured native tip are calculated below.

The occupied-capacity rule was checked independently against [CKB v0.200.0, `capacity.rs`](https://github.com/nervosnetwork/ckb/blob/52c2be1a104edbf0ee1b6e261ada7d0db10af740/util/gen-types/src/extension/capacity.rs): `Script::occupied_capacity` adds raw args length + 32 + 1; `CellOutput::occupied_capacity` adds 8 + data capacity + lock + optional type. [`Capacity::bytes`](https://github.com/nervosnetwork/ckb/blob/52c2be1a104edbf0ee1b6e261ada7d0db10af740/util/occupied-capacity/core/src/units.rs) converts one byte to 100,000,000 shannons. [RFC 0023](https://github.com/nervosnetwork/rfcs/blob/62a6e08e16a995ab94562581978ceac3726c31e6/rfcs/0023-dao-deposit-withdraw/0023-dao-deposit-withdraw.md) gives the same 102-byte breakdown for this Script shape. These upstream sources were archived with commit-pinned URLs and SHA-256 hashes under `runs/wo3b2-r3/references/`.

| Occupied field | Bytes | Capacity |
|---|---:|---:|
| Capacity u64 | 8 | 8 CKB |
| Lock code_hash + hash_type + raw args | 32 + 1 + 20 | 53 CKB |
| DAO type code_hash + hash_type + raw args | 32 + 1 + 0 | 33 CKB |
| Raw output data | 8 | 8 CKB |
| **Total** | **102** | **10,200,000,000 shannons** |

This is occupied field size, not total Molecule wire length. The helper serializes the exact CellOutput using the archived `blockchain.mol` schema: lock Script 73 bytes, type Script 53 bytes, CellOutput 150 bytes; separate raw data is 8 bytes (12 with its Bytes length prefix). Table offsets/size prefixes are serialization overhead excluded by the protocol occupied-capacity functions. Full serialized output hex is retained in `calculation.json`. The plain untyped, empty-data Cell shape occupies 8 + 53 = **61 CKB**; the present DAO Cell adds 33 + 8 = **41 CKB**. All eight zero data bytes still count.

The deterministic helper [b2r3_dao_diagnosis.py](../scripts/b2r3_dao_diagnosis.py) takes capacity, Scripts and data from the canonical transaction, then canonical header DAO fields. It loads the observed Room compensation only **after** computing the independent answer. DAO AR is unsigned little-endian bytes 8 through 15 of the 32-byte DAO field. For capacity C, occupied O, deposit rate A and comparison rate B:

```text
counted = C - O
maximum = floor(counted * B / A) + O
compensation = maximum - C
```

This is also the [CKB node's `DaoCalculator::calculate_maximum_withdraw`](https://github.com/nervosnetwork/ckb/blob/52c2be1a104edbf0ee1b6e261ada7d0db10af740/util/dao/src/lib.rs#L290) implementation. For an active deposit, substituting a current/historical comparison header is an accrued estimate, not proof that phase-2 withdrawal is immediately available. No withdrawal transaction or maturity claim is made here.

| Header | DAO field | AR integer |
|---|---|---:|
| Deposit 22,647,433 | `0x04ecec36750abd583e302512385f2a00cf32854877be6e0a006f105808917b09` | 11,926,643,449,081,918 |
| Before-restart estimate comparison 22,647,449 | `0xa4af6aaeba0bbd58a7d2ca4e385f2a00d38cddb8e8be6e0a003f7a111f917b09` | 11,926,644,466,569,895 |
| Before-restart captured native tip 22,647,450 | `0xde8be205cf0bbd58c92c9552385f2a000613e3cfefbe6e0a00dc107d20917b09` | 11,926,644,530,162,889 |
| After-restart estimate comparison 22,647,478 | `0x36a2fe96080ebd58ab07b7bc385f2a00f2db7d54b6bf6e0a00088a4148917b09` | 11,926,646,310,766,507 |
| After-restart captured native tip 22,647,479 | `0x707e76ee1c0ebd58be6181c0385f2a001964836bbdbf6e0a00a520ad49917b09` | 11,926,646,374,359,486 |

Every header's canonical hash was re-queried by height. Before-restart hashes are `0x05f0c405b311661a8951d2303959c486a045bcce5a1334a245ec0f8ab4e71482` at 22,647,449 and `0x4cca95fbde27262baf7b258d7e859a6e0ea20005d4815b157da32a6376284f1a` at 22,647,450. Full headers, raw transaction, live-cell response and public tip are in `chain.json`.

| Fixed header | Correct reward, O = 102 CKB | Reader reward, O = 61 CKB | Observed Room reward |
|---|---:|---:|---:|
| 22,647,449 | 7,661 | 8,010 | 8,010 before restart |
| 22,647,450 | 8,139 | 8,511 | No estimate anchored directly to this tip |
| 22,647,478 | **21,546** | **22,530** | **22,530 after restart** |
| 22,647,479 | 22,025 | 23,031 | No estimate anchored directly to this tip |

All rewards above are shannons. At 22,647,478, correct counted capacity is **89,800,000,000** shannons (898 CKB); Pocket counts **93,900,000,000** (939 CKB). Exact arithmetic:

```text
102 CKB: floor(89,800,000,000 * 11,926,646,310,766,507
              / 11,926,643,449,081,918) = 89,800,021,546
          maximum = 100,000,021,546; compensation = 21,546
          division remainder = 7,816,338,280,994,772

 61 CKB: floor(93,900,000,000 * 11,926,646,310,766,507
              / 11,926,643,449,081,918) = 93,900,022,530
          maximum = 100,000,022,530; compensation = 22,530
          division remainder = 4,905,999,284,387,460
```

The excess is **984 shannons = 0.00000984 CKB**, about 4.57% of this small reward, not 4.57% of principal. Room `lastUpdatedAt` is 1,791,246,670,723 after restart and 1,791,246,438,408 before restart. The earlier sealed audits enumerate every header from deposit through each captured tip: neither observed cache amount matches any correct 102-CKB result in its range; each matches the 61-CKB formula exactly. Thus ordinary cache age or comparing adjacent tips does not explain the excess.

A second independent check used the read-only public-node RPC `calculate_dao_maximum_withdraw(outpoint, comparison_header_hash)`, documented in the archived `rpc/src/module/experiment.rs`. At all four non-deposit comparison headers its result equals the helper's **102-CKB** maximum exactly. At 22,647,478 it returned `0x1748773c2a` = 100,000,021,546 shannons. Requests and responses are preserved in `rpc-crosscheck.json`. The helper also reproduces RFC 0023's published worked example (200,155,259,131 shannons maximum) and supports deterministic offline replay.

The pinned application trace is below. Paths are relative to `repos/pocket-node`; file hashes are recorded in `code-provenance.json`. Prefixes: **app** = `android/app/src/main/java/com/rjnr/pocketnode/`; **shared** = `android/shared/src/commonMain/kotlin/com/rjnr/pocketnode/`; **native** = `external/ckb-light-client/light-client-lib/src/`.

| Path and location | Responsibility and finding |
|---|---|
| app `data/gateway/DaoDepositReader.kt:69`, `:153`, `:242`, `:262` | `list` enumerates owned DAO Cells/spends. `resolveOneDeposit` passes literal `61_00000000L` in **both** withdrawing and deposited branches; stores `maxWithdraw - capacity`. This is the wrong argument. |
| shared `data/gateway/models/DaoConstants.kt:21`, `:26` | Existing `DEPOSIT_OCCUPIED_SHANNONS = 10_200_000_000L`, with correct 102-byte explanation. |
| shared `data/transaction/TransactionBuilder.kt:63` | `MIN_CELL_CAPACITY = 61_00000000L` is the ordinary Cell minimum. This explains the byte shape represented by 61; it does not prove the author's intent or that this symbol was copied. The DAO reader uses its own literal. |
| native `jni_bridge/dao.rs:63`, `:83` | JNI forwards occupied capacity unchanged. |
| native `bridge_core/dao.rs:33`, `:93`, `:142` | `parse_ar` reads bytes 8..16 LE; `calculate_max_withdraw` applies `(C-O)*B/A+O`. It does not infer DAO occupancy or add omitted bytes. The formula is correct for supplied inputs. |
| app `data/gateway/DaoDepositReader.kt:300`, `:308`, `:332`, `:352` | Compensation also feeds per-deposit APC after one elapsed day. Status is independently derived from data, epochs and pending flags. Final model stores nonnegative compensation. APC distortion is a code-path implication, not observed for this minutes-old deposit. |
| shared `data/gateway/models/DaoModels.kt:105` | `determineDaoStatus` uses withdrawing/pending flags and current/unlock epochs; no compensation dependency. |
| app `data/gateway/GatewayRepository.kt:2594`, `:2841`, `:2851`, `:2893` | `getDaoDeposits` scans live native data, deduplicates and merges. `mergeWithCachedDaoDeposits` writes live results through to Room, skips duplicate cached live keys, and handles out-of-window/in-flight rows by identity/status. |
| app `data/gateway/DaoCellMapping.kt:25`, `:40`, `:57`, `:60`, `:70` | `toDaoCellEntity` copies compensation unchanged; `toCachedDeposit`/`toOutsideWindowDeposit` can read it unchanged. No interest calculation in mapping. |
| app `data/gateway/DaoSyncManager.kt:93`, app `data/database/dao/DaoCellDao.kt:18`, app `data/database/entity/DaoCellEntity.kt:28` | Upsert/persistence stores the supplied compensation. There is no compensation-as-of header field. Restart refresh calls the same reader and writes a newly wrong estimate; it does not turn a previously correct value into an incorrect one. |
| app `ui/screens/dao/DaoViewModel.kt:113`, `:131`; app `data/gateway/GatewayRepository.kt:2970` | Refresh and overview sum compensation into display totals; principal `totalLocked` separately sums capacity. |
| app `ui/screens/dao/components/DaoDepositCard.kt:53`; app `ui/screens/dao/DaoScreen.kt:360`, `:389`, `:396`, `:453`, `:609` | Reward card, earned amount, unlock confirmation total and aggregate reward consume the estimate. `formatCkb` rounds to **two decimal CKB places**. Both small rewards in this fixture display `+0.00 CKB`; the retained UI observations do not demonstrate a visibly different formatted number. |
| app `ui/screens/dao/DaoViewModel.kt:231`, `:258`, `:289`, `:462` | Withdraw/unlock handlers pass the outpoint (and authenticated key) to the repository, not the displayed compensation/total. Button gating uses pending actions/status. |
| app `data/gateway/GatewayRepository.kt:3037`, `:3066`, `:3093`; shared `data/transaction/TransactionBuilder.kt:553`, `:597` | Phase-1 withdraw reconstructs the deposit Cell from principal/identity and preserves its exact capacity; a separate ordinary Cell pays the fee. Cached compensation is not an input. |
| app `data/gateway/GatewayRepository.kt:3149`, `:3193`, `:3214`, `:3239`; shared `data/transaction/TransactionBuilder.kt:641`, `:666` | Phase-2 unlock fetches deposit/withdraw headers, **recomputes using the 102-CKB constant**, and passes that maximum to the builder. Output = fresh maximum minus fee. Planned fee also uses that fresh maximum, not Room compensation. |
| app `data/gateway/GatewayRepository.kt:1415`, `:1423`, `:2409` | Ordinary spend selection excludes typed DAO Cells. Confirmed unlock history amounts use actual transaction outputs, not cached reward. |

This establishes a calculation defect in the application **reader**, with display/cache consequences. It is not an oracle error, restart-only cache corruption, or a demonstrated functional withdrawal defect. Ownership, account mapping, outpoint, principal, live/spent set, headers, epoch and active-deposit stage agree with the canonical chain and persisted across the R2 restart. No dependency from this erroneous compensation to transaction construction, maturity/since calculation, or spendability was found in the pinned Android path. A real mature withdrawal/unlock was **not executed**; this report does not certify every DAO lifecycle path or unrelated wallet behavior.

The smallest proposed correction is to replace the two `61_00000000L` arguments in `DaoDepositReader.resolveOneDeposit` with the already-defined `DaoConstants.DEPOSIT_OCCUPIED_SHANNONS` for this supported standard DAO Cell shape. No schema, native arithmetic or transaction-builder change is needed for this defect. Both deposited and withdrawing reader branches should have a regression using real header AR values; assert reader reward and unlock maximum use the same occupancy. Refresh/write-through and restart should preserve/recalculate the corrected value. This is a **proposal only**; production code and the approved APK remain unchanged. The unsent [Pocket bug draft](P3B2_R3_POCKET_DAO_BUG_DRAFT.md) is ready for PM review.

The proposed B2 DAO contract is intentionally narrower than a complete DAO calculation/lifecycle certification:

1. Require the canonical deposit outpoint, exact capacity/data/lock/type, owning derived account and parent association, deposit block/hash/epoch, TESTNET, covered history and native registration/progress to agree in SOURCE, A2 and B2. Account 0 must not acquire account 1's DAO row or balance.
2. Require the live DAO Cell and its Room/application representation to remain **DEPOSITED**, with correct principal and null withdrawal/unlock metadata while no canonical transition exists. Ordinary spendable balance excludes its principal. Require these facts after refresh and restart; a missing, duplicated, cross-mapped, falsely completed/unlockable or canonically spent position fails.
3. Preserve all existing two-account, exact-live-Cell, historical coverage, post-H2 stale-spend/catch-up, signing-readiness and restart requirements. No generic waiver of DAO cache reconciliation is allowed. A real later lifecycle transition remains NOT TESTED unless separately undertaken under a later authorization.
4. Report canonical compensation separately from the known v1.8.5 reader estimate. Keep the compensation/cache rows in evidence. Compare SOURCE/A2/B2 estimates using the **same 61-CKB algorithm at a common header or tightly observed fresh-refresh header interval**; do not require raw equality between observations at different tips. Because Room omits an as-of hash, record native tips around the observed refresh and require agreement within that bounded interval. An unexplained B-only difference, failure to refresh the old H2 estimate, or canonical metadata overridden by stale cache still fails/reopens diagnosis. If no defensible interval can be established, do not silently accept the estimate.
5. Label any later PASS as active-DAO-position continuity with a known pre-existing reward-estimate defect. Do not claim correct earned-value display, APC, mature unlock execution or full DAO lifecycle acceptance from it. SOURCE still requires a fresh canonical recheck under the approved revised contract before H2; R3 does not grant that PASS retroactively.

These conditions distinguish state continuity from a shared pre-existing reader error and retain detection of recovery-specific divergence. The present finding gives D2 no demonstrated job: it is an application call argument, not missing portable state authority. **PM's next decision is whether to approve this revised contract on the same APK and authorize a later B2 continuation, or pursue a separately pinned Pocket correction first.** Separately decide whether to send the prepared bug report; nothing has been sent.

R3 evidence is under `runs/wo3b2-r3/`: `preservation-before.json`, `chain.json`, `references.json`, `references-supplement.json`, `calculation.json`, `rpc-crosscheck.json`, `code-provenance.json`, `preservation-after.json` and `evidence-manifest.json`. Public calculations are reproducible with `python scripts/b2r3_dao_diagnosis.py calculate`; this replays the saved chain inputs offline and verifies the RFC vector. `crosscheck` repeats the four read-only public RPC calculations. The preserved R2 audits, snapshots and reports were read, not rewritten. Final verification passed: existing tracked-file hashes, all 69 sealed evidence files, AVD metadata, clean pinned Pocket checkout and approved APK hash. Its free-space sample was **12,172,378,112 bytes (11.34 GiB)**. No emulator process was running at the final host check. No Android build or runtime test was needed or performed in R3.

**STOP. B2 remains paused for PM review.**
