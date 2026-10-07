# Draft: DAO reader overstates compensation by using plain-Cell occupied capacity

**Prepared for review; not sent.** Pocket v1.8.5 / versionCode 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`, Android debug APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`.

A standard DAO deposit's compensation estimate uses 61 CKB occupied capacity in the reader, although this Cell occupies 102 CKB. The resulting overestimate is persisted in `dao_cells.compensation`. It occurs before and after restart.

Exact public TESTNET fixture:

- Outpoint: `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2:0x0`.
- Capacity: 100,000,000,000 shannons (1,000 CKB); data `0x0000000000000000`.
- Lock: code_hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash_type `type`, args `0x2da024570462b0e2421d87abcbfebd4567d52ad5`.
- DAO type: code_hash `0x82d76d1b75fe2fd9a27dfbaa65a039221a380d76c926f378d3f81cf3e7e13f2e`, hash_type `type`, empty args.
- Deposit block: 22,647,433, hash `0x7cb42962be61200f1b21caec71cdf4be5387b706b647bf8bfaa869346ce8a2e5`, epoch `0x7080128003681`.
- Comparison block: 22,647,478, hash `0x92579b1939123c32c33dc77d1fedb3fbd2853d917061a0c08556ac0fca3fcdb7`.
- Deposit AR: 11,926,643,449,081,918; comparison AR: 11,926,646,310,766,507.

Expected occupied capacity is `(8 + 32 + 1 + 20 + 32 + 1 + 0 + 8) * 100,000,000 = 10,200,000,000` shannons. Expected compensation is `floor((100,000,000,000 - 10,200,000,000) * AR_comparison / AR_deposit) + 10,200,000,000 - 100,000,000,000 = 21,546` shannons. Public node `calculate_dao_maximum_withdraw` returns `0x1748773c2a` (principal + 21,546) for this outpoint and comparison hash.

Observed post-restart cache: **22,530** shannons, exactly reproduced by substituting **6,100,000,000** occupied shannons. Excess: 984 shannons. Room does not store the estimate's header hash; the matching height is inferred, while the captured native tip was one block later. Before restart the same error appeared: cached 8,010 versus canonical 7,661 at block 22,647,449. This is not introduced by restart. Both amounts round to `+0.00 CKB` in the current two-decimal UI, so the exact discrepancy is in the underlying estimate/cache, not a visibly different number in this small fixture.

Root cause at the pinned commit: `android/app/src/main/java/com/rjnr/pocketnode/data/gateway/DaoDepositReader.kt`, `resolveOneDeposit`, lines 243 and 263 pass `61_00000000L` to `nativeCalculateMaxWithdraw` in the withdrawing and deposited branches. Native arithmetic correctly applies the supplied argument. `android/shared/src/commonMain/kotlin/com/rjnr/pocketnode/data/gateway/models/DaoConstants.kt:26` already defines `DEPOSIT_OCCUPIED_SHANNONS = 10_200_000_000L`. DAO adds 33 bytes of type Script and 8 bytes of data to the ordinary 61-byte Cell.

Reproduce without this wallet's secret or a new transaction:

1. Fetch the public transaction and the two headers from `https://testnet.ckb.dev` using `get_transaction` and `get_header_by_number`.
2. Extract AR as unsigned little-endian bytes 8..15 of each header's `dao` field. Count occupied field bytes from the output and raw data using CKB's occupied-capacity rule.
3. Evaluate `(capacity - occupied) * AR_comparison / AR_deposit + occupied` with integer floor. With 102 CKB it returns 100,000,021,546; with the reader's 61 CKB it returns 100,000,022,530.
4. Cross-check `calculate_dao_maximum_withdraw` with params `[{"tx_hash":"0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2","index":"0x0"},"0x92579b1939123c32c33dc77d1fedb3fbd2853d917061a0c08556ac0fca3fcdb7"]`.
5. A reader regression can stub the Cell and headers above into `resolveOneDeposit`'s native dependencies and check compensation against 21,546. For app-level reproduction with an already owned standard DAO deposit, refresh DAO and inspect its debug Room row alongside the observed tip interval; restart and refresh again. Current-tip amounts will differ from these historical values.

Impact: overstated reward cards/totals, confirmation estimates and potentially the derived APC once its elapsed-time threshold is met; incorrect estimate persisted/recalculated in Room. Ownership, principal and lifecycle status do not depend on compensation. The Android unlock path at `GatewayRepository.kt:3193` independently recomputes using the correct 102-CKB constant; `TransactionBuilder.buildDaoUnlock` spends that fresh maximum minus fee. Phase-1 withdraw preserves principal. This trace finds no affected constructed withdrawal/unlock amount from this reader defect; a mature unlock was not executed as part of diagnosis.

Suggested minimal correction: use the existing DAO occupied-capacity constant in both reader branches. Add fixed-header regressions for deposited/withdrawing estimates, plus cache refresh/restart coverage. No production fix has been applied in this report.
