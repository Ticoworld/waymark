# WO07-R9: Real Neuron Recovery

Date: 2 November 2026

## Decision

**PARTIAL.** The genuine R8 Neuron-owned TESTNET Script now has one confirmed received transaction. Neuron v0.204.1's actual `LightSynchronizer.initSyncProgress()` and `upsertTxHashes()` discovered it, wrote a cache row under the real Neuron wallet UUID before advancing the app discovery checkpoint, and the packaged Queue/TransactionPersistor persisted its live owned output. The cache and transaction/output state survived closing and reopening the disposable SQLite database.

This is ordinary Neuron synchronization, not D2 recovery. No D2 artifact was made for the R8 Script or imported into an independent Neuron destination. The test therefore does not demonstrate reuse of prior-device work, cursor preservation through import, complete wallet history, spending recovery, interrupted replay, or a speed advantage. The receive-only fixture has no known signing credentials and only one incoming transaction.

## Wallet and transaction

The wallet was created through Neuron's actual packaged v0.204.1 controller and wallet/address services under the isolated profile `%TEMP%\\wo07-r8-neuron-profile-real-testnet`. Its identity and public account-0 Script were independently reopened and recorded in [R8](WO07_R8_OWNED_WALLET_SYNC.md). The Neuron-assigned wallet UUID is `1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0`; the default lock Script is code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`, args `0xa2ade6127fcbb7f1ccfe4a886f6b1e9c5c92d837`. No mnemonic, password, keystore contents, or xpub is included here. Treat this wallet as receive-only; no claim is made that its discarded credentials are recoverable.

Faucet claim `706994` completed without a new claim being initiated. Its transaction is `0x42dc0f3efabc9134fc2244f5c01c3b52768ba8d23f29c78d839208afa844e435`, at height `22,944,379`, block hash `0x4e5c9e8562027923c11a8608b10c399dccb59f145e047eb0f58a8a8b5b56f52c`. Two public TESTNET RPCs and the local Light Client agreed on the header. Output 0 is the Neuron-owned Script, capacity `1,000,000,000,000` shannons (10,000 CKB), and an independent `get_live_cell` check returned it live. The R8 report had recorded the faucet request as pending; the later confirmation is new evidence.

The local source client was official CKB Light Client v0.5.4, binary SHA-256 `fe38b58d85239149bd9aab81f9f90dff3ee8d7d01d09435be6621e6525f0cab8`, source pin `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`. It ran from a fresh copy of the R7 authority store at `%TEMP%\\wo07-r9-owned-source`, with RPC `127.0.0.1:19087` and P2P `127.0.0.1:19150`. Its Script cursor advanced beyond the faucet transaction. The source transaction/header were obtained by the released client; no full-chain download was started.

## Neuron execution

The headless harness uses the extracted packaged Neuron v0.204.1 backend at `%TEMP%\\wo07-r6-neuron-asar`, with the R8 isolated profile. It derives the Script from Neuron's persisted address metadata and verifies the selected network is Light TESTNET with the expected genesis. It sets Neuron's supported wallet start height to `22,944,378` (H-1), removes only this disposable wallet's sync-progress rows, and invokes the packaged `LightSynchronizer.initSyncProgress()`.

The actual `LightSynchronizer.upsertTxHashes()` made grouped RPC requests to the local v0.5.4 client. The harness observed 91 grouped calls across registered scripts and exactly one matching faucet transaction. It verified the real wallet ID in `IndexerTxHashCache`, then called the actual `updateSyncedBlockOfScripts()` only after cache insertion. The owned Script discovery checkpoint advanced from `22,944,378` to `22,944,565`; the native Script cursor was also beyond H. This was a normal historical scan from H-1, not imported state. Therefore historical filtering was performed and no work saving is claimed.

Neuron's packaged Queue and `TransactionPersistor.saveFetchTx()` processed the actual confirmed transaction. The Queue fetched the transaction/header and its external previous transaction through the Light RPC. The application DB contained:

| Record | Observed state |
| --- | --- |
| Transaction | Exact faucet hash, block height/hash, status `success` |
| Wallet-scoped cache | One row for the actual wallet UUID/hash; block `22,944,379`; `isProcessed=true` |
| Owned output 0 | Exact Script and capacity; status `live` |
| Owned input rows | None |

The missing input row is consistent with Neuron's `TransactionPersistor.shouldSaveDetail()` filtering: it stores detailed input rows for input locks relevant to the tracked wallet scripts. This receive transaction spends an external faucet cell, not an R8 wallet cell. The Queue fetched the previous transaction to process the confirmed transaction, but this fixture does not exercise a wallet-owned Cell being spent. The result is not a complete transaction graph or spend-recovery test.

## Restart and checkpoint limits

After the Queue drained, the harness destroyed and reopened the Neuron Light SQLite connection. An independent verifier using Neuron's TypeORM entities read back the same successful transaction, live output and processed cache row. The wallet's 90 progress rows survived. For the default Script the persisted fields were start `22,944,378`, synced `22,944,565`, and local-saved `22,944,378`.

The unchanged local-saved height is a harness limitation: the Electron main-process address-generation IPC was stubbed, so the app's follow-up address/local-save bookkeeping did not run. Discovery checkpoint advancement is not a claim that all wallet application work or address discovery is complete. No cold restart of the full Neuron application was performed. No interrupted cache processing, duplicate replay, imported-cursor preservation, or H/H+1 candidate handoff was tested.

## Why D2 recovery did not run

The existing experimental D2 `v054_rocksdb` adapter is destination-import-only; its source `export()` returns `UnsupportedProfile`. The R7 Pocket artifact belongs to a different Script and was not assigned to this wallet. No R8-specific artifact exists.

Producing one requires a v0.5.4 native RocksDB source exporter that writes the D2 artifact's Script indexes, matching transaction records/closure, genesis and handoff anchor. At inspection there was no existing compiled adapter target; the prior RocksDB target had been absent. C: had only about 5.49 GiB free during this run, so a repeat multi-gigabyte RocksDB build would risk the required 4 GiB reserve. I did not compile or invent a substitute artifact. The real transaction is available, but its matching export/import recovery path remains the necessary missing step.

The existing D2 trust limit also remains: an authenticated or hash-valid source package does not prove that the source omitted no matching historical Script transactions. A destination must continue to trust the user's own source snapshot for completeness or independently scan to establish completeness.

## Resource use and preserved evidence

The disposable client store was copied from R7; R7's original store and reports were not changed. C: had `5,887,688,704` bytes free after the probes and `6,054,707,200` bytes after stopping the disposable Light Client (about 5.64 GiB final), above the 4 GiB reserve. No Neuron source build, Rust build, full-chain download, new faucet claim, real user profile access, or cleanup was performed.

New R9 workspace files:

- `tools/wo07-r9/prepare-testnet-client.js` creates a separate client store/config from the R7 fixture and refuses an existing destination.
- `tools/wo07-r9/owned-sync-baseline.js` runs the genuine Script's ordinary Neuron sync/cache/queue path against the local v0.5.4 RPC.
- `tools/wo07-r9/inspect-owned-db.js` independently reads the disposable Neuron DB using Neuron's entities.
- `docs/WO07_R9_REAL_NEURON_RECOVERY.md` records this result.

Reproduction, with the prior R2/R6/R7/R8 temporary fixtures still available:

```powershell
node tools/wo07-r9/prepare-testnet-client.js `
  "$env:TEMP\\wo07-r7-imported-store" "$env:TEMP\\wo07-r9-owned-source"

& "$env:TEMP\\wo07-r6-v054-client\\ckb-light-client.exe" run `
  --config-file "$env:TEMP\\wo07-r9-owned-source\\config.toml"

node tools/wo07-r9/owned-sync-baseline.js `
  "$env:TEMP\\wo07-r6-neuron-asar" `
  "$env:TEMP\\wo07-r8-neuron-profile-real-testnet" `
  "1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0" `
  "http://127.0.0.1:19087"

node tools/wo07-r9/inspect-owned-db.js `
  "$env:TEMP\\wo07-r6-neuron-asar" `
  "$env:TEMP\\wo07-r8-neuron-profile-real-testnet" `
  "1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0"
```

Use a fresh isolated client destination for a repeat. The Neuron harness intentionally uses the disposable R8 profile and existing wallet; it is not an isolated app-profile creator.

## Next decisive action

Implement and test the smallest v0.5.4 RocksDB **source exporter** in the isolated D2 checkout, using the confirmed Neuron-owned Script and transaction. Before building, either obtain a build target with at least the 4 GiB reserve remaining throughout or use an already available compatible build cache; do not delete unrelated files to make room. Export from a quiescent copied source store, then import into a separate independently anchored Light Client destination. Verify the imported Script cursor and H/H+1 range, run Neuron initialization before/after the import barrier, and prove no cursor rewind. Only then run cache replay and compare the ordinary baseline against the candidate at the same canonical tip. Add a genuine wallet spend fixture before claiming spent/live transition recovery.

## Pinned implementation references

- Neuron source `a926e3383d3a3e305b3bde7d233474515ef01a2e`: `packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts` (`initSyncProgress`, `upsertTxHashes`, cache-before-progress order), `packages/neuron-wallet/src/services/sync-progress.ts`, `packages/neuron-wallet/src/block-sync-renderer/sync/queue.ts`, `packages/neuron-wallet/src/services/tx/transaction-persistor.ts`, and `packages/neuron-wallet/src/database/chain/entities/{indexer-tx-hash-cache,sync-progress,input,output,transaction}.ts`.
- Packaged runtime: Neuron `v0.204.1`, extracted backend used by R6/R9.
- Light Client source `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`, release `v0.5.4`.
- D2 adapter revision `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`; isolated experimental file `crates/d2-script-handoff/src/v054_rocksdb.rs` remains destination-import-only.
- Earlier proofs are preserved in [R4](WO07_R4_NEURON_APPLICATION_REPLAY.md), [R5](WO07_R5_GENUINE_NEURON_RECOVERY.md), [R5A](WO07_R5A_NEURON_STARTUP_RESOLUTION.md), [R6](WO07_R6_HEADLESS_NEURON_REPLAY.md), [R7](WO07_R7_VERIFIED_HEADER_AND_REAL_QUEUE.md), and [R8](WO07_R8_OWNED_WALLET_SYNC.md).
