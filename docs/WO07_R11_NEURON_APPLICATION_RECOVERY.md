# WO07-R11: Neuron Application Recovery

Date: 2 November 2026

## Verdict

**APPLICATION RECOVERY PROVEN**, for one receive-only Script and one confirmed TESTNET transaction using a **full native Light Client store copy** and a simulated clean application state. Neuron v0.204.1's actual synchronization initializer, grouped RPC query, cache service, Queue and `TransactionPersistor` rebuilt the missing application transaction/output state under the real R8 wallet UUID. Duplicate discovery left one cache row; the cache drained; `localSavedBlockNumber` advanced through the transaction; and the SQLite state matched after reopen. The official v0.5.4 client retained the transferred Script cursor and transaction through a cold restart.

This is not a complete wallet recovery, a supported mnemonic restore, a selective D2 handoff, or evidence of faster recovery. The test contained one receive and no wallet-owned spend. History completeness, balances beyond this one known output, reorg handling, independent authority for the copied historical state, and performance remain unproven.

## Fixture and isolation

The genuine R8 identity was preserved: Neuron wallet UUID `1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0`, with 30 Neuron address metadata rows and account-0 Script hash `0x28535e1e70eb2ae8c56a829e1f9d3777fdf6b310c9c1dff17e4ae01917e45e62`. The Script is the default lock with code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`, args `0xa2ade6127fcbb7f1ccfe4a886f6b1e9c5c92d837`.

The known transaction is `0x42dc0f3efabc9134fc2244f5c01c3b52768ba8d23f29c78d839208afa844e435`, at height `22,944,379` (`0x15e1a7b`), block hash `0x4e5c9e8562027923c11a8608b10c399dccb59f145e047eb0f58a8a8b5b56f52c`. Output 0 has capacity `1,000,000,000,000` shannons (10,000 CKB), matches the Neuron Script, and was live in the public TESTNET RPC check recorded in R9.

Neuron was not launched and no personal profile was accessed. The R8 disposable profile was copied to `%TEMP%\\wo07-r8-neuron-profile-real-testnet-r11-phase2`. In that copy only, the setup script removed the one known R9 transaction row, its one output row, associated input/tx-lock/description rows if present, its wallet-scoped cache row, and the wallet's 90 sync-progress rows. It retained the Neuron wallet identity and 30 address rows. Before reset it verified the copied DB contained exactly one transaction, one wallet cache entry, one output, and no input rows. Afterwards it verified zero transaction/cache/progress rows and all 30 address rows. The encrypted keystore file was copied with the disposable profile but never opened, decrypted, or used to sign. This is explicitly a **simulated clean application state**, not a mnemonic-based supported restore.

## Two-phase initialization result

The successful sequence used separate native stores:

1. The R11 app copy had no transaction, cache, or progress rows. A separate R7-derived v0.5.4 client copy did not yet register the R8 Script. The client had no bootnodes and no active peers.
2. Neuron's actual packaged `LightSynchronizer.initSyncProgress()` ran against that client. It registered the 90 wallet Scripts in `partial` mode, including the exact R8 lock Script at `0x15e1a7a` (22,944,378, H-1), and issued an empty `delete` call. Neuron's actual `SyncProgressService` created 90 progress rows. The target row had `syncedBlockNumber=22,944,378` and `localSavedBlockNumber=22,944,378`; the app still had zero transaction/cache rows.
3. The pre-import client was stopped. A new native destination root received a byte-hash-verified copy of the R10 synchronized v0.5.4 store: 22 files, 2,024,534 bytes before startup. This store already contained the exact Script index, transaction, header, and continuation cursor. It had a fresh network directory and enabled TESTNET peers; the R10 source store was not modified.
4. Neuron's actual `initSyncProgress()` ran again. The app progress rows made the native Script recognizable by its exact Script args. It issued `set_scripts([], 'partial')` and `set_scripts([], 'delete')`; neither call changed the target. Its cursor remained `0x15e1eb8` (22,945,464) before and after initialization. This confirms the two-phase ordering avoids the cursor rewind seen with an empty progress DB.
5. The actual `upsertTxHashes()` queried the imported indexed range beginning at `0x15e1a7a` and ending at the native cursor. It found the faucet transaction. A second upsert before checkpoint advancement did not duplicate the cache row. Only after the cache row existed did the harness call Neuron's existing `updateSyncedBlockOfScripts()`.
6. Neuron's packaged Queue fetched the real transaction and header, resolved its external previous transaction, and called the real `TransactionPersistor.saveFetchTx()`. The main-process IPC transport was stubbed, but its actual handler target, `WalletService.checkAndGenerateAddress()`, ran. The Queue completion callback then advanced local-save progress normally; no height was assigned manually.

The exact app `syncedBlockNumber` advanced to `22,945,464` after cache insertion, while `localSavedBlockNumber` remained at the start floor until queue completion. After persistence, local-saved advanced to `22,944,379`, the transaction block. The distinction remained intact.

## Empty-progress startup failure

R11 also exercised the simpler, unsafe order: attach the transferred native store while the fresh application DB has no matching progress rows, then call the actual Neuron initializer. Before initialization the target cursor was `0x15e1e90`; Neuron sent 90 `partial` Script registrations and reset the target to `0x15e1a7a`. With peers enabled, the client then advanced the filter cursor from the floor to `22,945,378`, repeating historical filtering. The imported index stayed queryable and the app transaction still reconstructed, but that order did not preserve the completed filtering work.

Therefore the integration boundary is concrete: **a transferred Script must have a legitimate Neuron progress row before the post-transfer initializer runs**. The demonstrated route is to initialize progress first through Neuron, stop the client, transfer the native store, then restart. A production integration would still need an atomic lifecycle barrier and clear error recovery around these steps.

## Application state, duplicate handling, and restart

After the successful two-phase replay, the disposable Neuron DB contained:

| Record | Result |
| --- | --- |
| Transaction | One exact faucet transaction, status `success`, block/height matched |
| Wallet cache | One row under the real wallet UUID, block `22,944,379`, `isProcessed=true` |
| Owned output | One output, exact Script, capacity `1,000,000,000,000`, status `live` |
| Input rows | None; the receive spends a faucet-owned input, not an R8 wallet Cell |
| App progress | Start H; discovery synced `22,945,464`; local-saved `22,944,379` after queue completion |
| Duplicate upsert | Two discovery calls produced one cache record and one app transaction/output |

The same transaction/output/cache/progress snapshot was read before and after closing and reopening the Neuron SQLite connection (`restartExact=true`). The separate Light Client was cold-stopped and restarted. The ordinary RPC then returned the exact transaction and committed block hash again, with the Script still registered and its cursor intact.

For this one-result fixture, the recovered transaction hash, block, owned output Script, capacity, and live status match the ordinary R9 baseline and the public-chain check. This does not compare a complete transaction history or balance set.

The `[H,H+1)` query was empty. The real transaction at H+1 appeared exactly once in `[H+1,H+2)`; `[H-1,H)` was empty. The half-open boundary is therefore correct for this fixture. This does not test an actual transaction at H, a D2 H cursor, a reorg, or wallet spending.

## Continuation and trust limits

The successful destination used a peer-enabled config with the R10 chain store copied in. Its Script cursor advanced from the imported value to `22,945,464` before application replay, and a cold restart later reported a newer tip (`0x15e1ec0`). This demonstrates ordinary continuation from the copied checkpoint. It does not independently validate the historical source store or prove that the source included every matching Script transaction. The complete chain state and Script index were copied together. D2's trusted-self completeness limit remains.

Neuron persisted no input row for the faucet-owned input because its persistor stores detailed input rows only when the input lock is relevant to tracked wallet Scripts. This receive-only fixture cannot establish spent/live transition recovery or a complete transaction graph. No full-wallet balance comparison, DAO state, app-wide Electron restart, or pending-cache interruption test was run.

## Selective D2 versus native copy

For this small fixture, a 2.02 MB full native-store copy carried enough state to replay the one owned Script. This shows selective D2 export is not necessary to demonstrate this narrow integration path. A full-store copy also carries chain data, all registered Script views, cursors and other device history; its privacy, size, cross-version portability, independent chain-authority and reorg costs were not tested at representative scale. Selective D2 remains useful when a user needs a smaller, Script-scoped artifact, but no R11 D2 artifact was created or imported.

No matched timing comparison was run. The successful replay harness reported 1,450 ms from immediately before Neuron initialization through DB reopen, but it excludes app-profile preparation, native-store transfer, earlier Light Client catch-up and ordinary baseline work. The empty-progress run performed filtering after resetting the cursor. Do not treat either figure as recovery speed evidence.

## Reproduction and resources

New R11 scripts:

- `tools/wo07-r11/prepare-app-copy.js` creates a new R8 profile copy, verifies its exact one-record starting fixture, and removes only the specified records/progress from the copy.
- `tools/wo07-r11/prepare-preimport-client.js` creates an offline R7-derived client copy with file-hash verification.
- `tools/wo07-r11/initialize-progress-before-import.js` invokes Neuron's actual initialization before native state is attached.
- `tools/wo07-r11/prepare-client-copy.js` creates the peer-enabled R10 native-store copy.
- `tools/wo07-r11/recover-app-copy.js` executes the actual Neuron init, duplicate upsert, cache update, Queue, persistor, local-save callback and DB reopen checks.
- `tools/wo07-r11/probe-boundaries.js` verifies H/H+1 RPC ranges.

The tested sequence was:

```powershell
node tools/wo07-r11/prepare-app-copy.js `
  "$env:TEMP\\wo07-r6-neuron-asar" `
  "$env:TEMP\\wo07-r8-neuron-profile-real-testnet" `
  "$env:TEMP\\wo07-r8-neuron-profile-real-testnet-r11-phase2"

node tools/wo07-r11/prepare-preimport-client.js `
  "$env:TEMP\\wo07-r7-imported-store" `
  "$env:TEMP\\wo07-r10-native-copy2" `
  "$env:TEMP\\wo07-r11-preimport-node"

# Start the offline preimport client in another shell, then:
node tools/wo07-r11/initialize-progress-before-import.js `
  "$env:TEMP\\wo07-r6-neuron-asar" `
  "$env:TEMP\\wo07-r8-neuron-profile-real-testnet-r11-phase2" `
  http://127.0.0.1:19100

# Stop preimport client before copying native state.
node tools/wo07-r11/prepare-client-copy.js `
  "$env:TEMP\\wo07-r10-native-copy2" `
  "$env:TEMP\\wo07-r9-owned-source" `
  "$env:TEMP\\wo07-r11-native-store-phase2"

# Start the peer-enabled final client in another shell, then:
node tools/wo07-r11/recover-app-copy.js `
  "$env:TEMP\\wo07-r6-neuron-asar" `
  "$env:TEMP\\wo07-r8-neuron-profile-real-testnet-r11-phase2" `
  http://127.0.0.1:19100

node tools/wo07-r11/probe-boundaries.js `
  "$env:TEMP\\wo07-r6-neuron-asar" http://127.0.0.1:19100
```

The official CKB Light Client binary was v0.5.4, SHA-256 `fe38b58d85239149bd9aab81f9f90dff3ee8d7d01d09435be6621e6525f0cab8`, source pin `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`. Neuron packaged backend was v0.204.1; source pin `a926e3383d3a3e305b3bde7d233474515ef01a2e`.

At final check, C: had about 4.98 GB free, above the 4 GiB reserve. The test used only small disposable client/profile copies; no Rust or Neuron build, full-chain download, new faucet claim, unrelated cleanup, PR, or upstream publication occurred. All Light Client processes were stopped. R7 through R10 sources and evidence were preserved.

## Next action

Treat the two-phase lifecycle as a research proof, not a production feature. The next decisive test is a **matched baseline versus two-phase full-store recovery** with identical wallet Script coverage and target chain hash, measuring native transfer size/cost, source and destination preparation, historical filter work, transaction RPC replay, app reconstruction, continuation and validation separately. Add at least one confirmed wallet spend before evaluating spent/live correctness. Do not port a selective D2 exporter unless representative full-store size/privacy or portability measurements show a real disadvantage.

## Pinned source references

- Neuron `LightSynchronizer.initSyncProgress()`, `upsertTxHashes()`, cache-before-progress ordering, and start-height logic: [pinned source](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts#L127).
- Neuron progress initialization and the separate saved/synced fields: [SyncProgressService](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/services/sync-progress.ts#L9), [SyncProgress entity](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/database/chain/entities/sync-progress.ts#L10).
- Neuron Queue and persistence: [queue.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/queue.ts#L124), [transaction-persistor.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/services/tx/transaction-persistor.ts#L198).
- R10 full native-store portability boundary: [WO07-R10](WO07_R10_CROSS_DEVICE_HANDOFF.md); R9 ordinary owned Script baseline: [WO07-R9](WO07_R9_REAL_NEURON_RECOVERY.md).
