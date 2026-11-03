# Waymark: Reusing Synchronized Wallet State in Neuron

Updated: 3 November 2026

Waymark explores whether a wallet can recover its keys normally while reusing blockchain synchronization data from a previous installation. The Neuron experiment demonstrated that its existing processing pipeline can rebuild one owned TESTNET receive from a copied Light Client store, provided application synchronization records are initialized before that store is attached. This is an experimental mechanism, with full recovery, safety, and performance still to establish.

## Foundation: Pocket Node

Waymark was first validated with Pocket Node on Android. After normal key/account recovery and fresh destination security, a selected non-secret state package restored prior synchronization and discovery information. Baseline and state-assisted destinations matched checked history, live Cells, balances, account ownership, and an active DAO position. Both real-phone paths signed confirmed TESTNET transactions and passed cold restart; source signing secrets and Android Keystore material were not transferred.

Pocket Lite supplies restore hints while Full carries more saved state. A later comparison found the combined Full package faster on the tested fixture, but it also restored settled discovery metadata. Native-state reuse alone did not isolate the same benefit. Those single-run observations are not a general benchmark or evidence of Neuron acceleration.

## Neuron's startup limitation

The target was Neuron v0.204.1 with CKB Light Client v0.5.4. Neuron keeps application transaction records and `SyncProgress` separately from the Light Client's RocksDB indexes and Script cursors. Moving only a checkpoint cannot reconstruct the missing application records.

We observed that attaching an indexed native store before matching application progress exists can repeat historical filtering. Neuron's actual `LightSynchronizer.initSyncProgress()` sent partial `set_scripts` registrations for 90 wallet Scripts, resetting the owned Script cursor to the configured start height. The historical index remained queryable, but the completed filtering work was scanned again.

## Tested two-phase initialization

The successful sequence was:

1. Use Neuron's existing wallet/address identity and initializer to create legitimate `SyncProgress` records at the safe starting floor.
2. Stop the relevant workers and attach a verified copy of the previously synchronized native store.
3. Restart initialization, then replay indexed results through Neuron's normal transaction cache, Queue, and `TransactionPersistor`.

With the progress records present, initialization issued empty registration/deletion calls and preserved the transferred cursor. Neuron found the confirmed receive, durably cached it under the real wallet UUID, and persisted its transaction and live owned output. Repeating discovery left one cache row. Application records matched after SQLite close/reopen, and the Light Client retained its cursor and transaction after a cold process restart.

This ran headlessly using Neuron's packaged backend. The destination retained a copied disposable wallet identity and address metadata, with completed transaction/cache/progress rows removed before the test. It therefore simulated missing application state rather than demonstrating a fresh mnemonic restore. The native transfer was a full RocksDB store copy, not selective D2 import.

A separate restart test constructed a pending-cache state from the existing real cache row. In a new Node process, Neuron resumed it, persisted the receive, and marked the cache processed. This tested pending-work resume, not a process kill at the original write boundary.

## Correctness and claim boundaries

Neuron caches discovered hashes before advancing `syncedBlockNumber`; persistence and address processing precede cache completion and local-save advancement. `localSavedBlockNumber` must not be equated with the native cursor or treated as interchangeable with discovery progress.

The tests do not establish complete mnemonic restoration, wallet-owned spending recovery, full history/balance or DAO correctness, reorg safety, cross-version portability, or comprehensive crash safety. The receive-only fixture has no recoverable signing credentials. Installation rollback and a crash between transaction persistence and cache completion remain untested.

The copied store inherits source chain state and includes other registered Scripts and privacy-sensitive activity. Hash checks detect transfer corruption, not source completeness. A valid chain anchor does not prove that no matching transaction was omitted.

No matched recovery benchmark exists. Avoiding the observed cursor reset does not establish a total recovery-time advantage. A complete cold backup would retain both application and native state; that alternative was not tested. Neuron's inspected wallet-backup controller exports a keystore, not those complete databases.

## Feedback for Eval Exec

We would value your guidance on three points:

1. Does initializing `SyncProgress` before attaching native state fit Neuron's intended lifecycle? Is there a better supported pause/resume or migration boundary?
2. What consistency, version, canonical-chain, and crash-recovery checks would be required to reuse a transferred store safely?
3. Is this useful for a real Neuron recovery case, or does the recommended restore/backup workflow already address it? What benefit would justify comparison with ordinary restore and a complete cold backup?

If the use case is worthwhile, the next useful comparison is those three approaches with a recoverable wallet containing separated receives and an owned spend, at the same canonical tip. It must include preparation, transfer, filtering, reconstruction, catch-up, validation, and restart costs.

## Evidence and implementation references

The original reports and harnesses retain detailed observations, commands, limitations, and public TESTNET identifiers:

- Pocket: [phone recovery/signing proof](pocket-proof.md), [source and transaction evidence](evidence.md), and [Lite/Full timing attribution](lite-full-attribution.md).
- Owned Neuron fixture and ordinary sync: [WO07-R9](WO07_R9_REAL_NEURON_RECOVERY.md). Native-store portability: [WO07-R10](WO07_R10_CROSS_DEVICE_HANDOFF.md).
- Two startup orders, application reconstruction, duplicate discovery, and restart: [WO07-R11](WO07_R11_NEURON_APPLICATION_RECOVERY.md), with [initialization](../tools/wo07-r11/initialize-progress-before-import.js) and [replay harness](../tools/wo07-r11/recover-app-copy.js).
- Simulated pending-cache resume, safety gaps, and comparison limits: [WO07-R12](WO07_R12_RECOVERY_SAFETY_VALUE.md) and [restart harness](../tools/wo07-r12/restart-pending-queue.js).
- Separate selective D2 research: [native adapter result](WO07_R3_NATIVE_ROCKSDB_ADAPTER.md) and [eight-transaction Queue proof](WO07_R7_VERIFIED_HEADER_AND_REAL_QUEUE.md). That Pocket fixture had no established Neuron wallet ownership; the experimental v0.5.4 adapter remains import-only.

Examined Neuron source: `a926e3383d3a3e305b3bde7d233474515ef01a2e` ([LightSynchronizer](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts), [Queue](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/queue.ts), [TransactionPersistor](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/services/tx/transaction-persistor.ts)). Light Client source: `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25` ([native storage](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/storage/db/native.rs)).
