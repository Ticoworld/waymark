# WO07-R12: Recovery Safety and Value Gate

Date: 2 November 2026

## Decision

**RESEARCH VALID, PRODUCT CASE UNPROVEN.** R11 shows a two-phase full-native-store handoff can reconstruct one known R8 receive through Neuron's real cache, Queue and persistor when the destination application progress exists before the transferred store is attached. R11 also demonstrated the unsafe ordering: attaching the store to an empty progress database caused Neuron to issue 90 partial registrations and rewind the owned Script cursor to its wallet start height.

That is a useful mechanism proof, not a crash-safe product protocol. R12 did not inject process termination at each of the six requested windows, did not produce a matched recovery benchmark, and did not test a recoverable wallet with a spend. The existing evidence does not establish a material advantage over mnemonic restore plus a safe start height or a consistent cold backup. Do not advance to production integration yet.

## Preserved evidence and environment

R7 through R11 reports and scripts were read and left unchanged. The R8 disposable profile, R9 source, R10 native copy, R11 app/native copies and the R11 harness remain intact. The R8 fixture is receive-only; its mnemonic/password are unavailable and were not used. No personal profile was accessed.

Neuron source reference is `a926e3383d3a3e305b3bde7d233474515ef01a2e`, runtime v0.204.1. CKB Light Client is v0.5.4, source `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`. The D2 checkout remains `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`; its v0.5.4 RocksDB adapter remains destination-import-only. No build, network sync or new testnet transaction was run for R12.

At inspection C: had `4,969,320,736` bytes free, about 643 MiB above the 4 GiB reserve. The R11 disposable profile/native copies together occupied about 4.64 MB. No files were removed. `origin` is `https://github.com/Ticoworld/waymark.git`; all WO04-R12 report/tool artifacts shown by `git status` are untracked, so these results are present locally but are not committed. No commit was made.

## Interruption analysis

The table separates directly observed R11 behavior from source-level recovery expectations. None of the six rows below represents a forced power-loss or kill-at-instruction-boundary test.

| Interruption point | R12/R11 evidence | Safe continuation or fallback |
| --- | --- | --- |
| 1. App progress initialized, before native attachment | R11 executed progress initialization against a separate client before attachment. The app had 90 real Neuron progress rows at H-1 and zero transaction/cache rows. It did not kill the process at this boundary. | The app database remains a normal scan-ready state. Resume transfer from the immutable source, or leave the source unattached and let ordinary Neuron sync from the saved floor. The floor must not be advanced just because preparation started. |
| 2. During transfer preparation/validation | R10/R11 copy helpers hash-checked completed copies; no interrupted copy or failed validation was injected. R11 copied into a fresh destination path and preserved sources. | A partial staging directory is not a valid store. Keep source and current destination untouched; discard/quarantine the staging directory only after its ownership is confirmed, then recopy or use ordinary scan. A coordinator must validate a complete manifest before installation. |
| 3. After native attachment, before Neuron initialization | R11 attached a fresh network-root copy after app progress existed, then ran Neuron's actual initializer. It observed no matching `set_scripts` entries and the cursor stayed at `0x15e1eb8`. It did not crash between attach and init. | Restart is expected to be resumable when the matching Neuron progress rows are durable: rerun normal init and verify exact Script/profile/genesis/cursor. If rows are absent or inconsistent, do not continue from the advanced cursor; restore the previous native directory or reset to the ordinary safe start floor and rescan. |
| 4. After discovery, before cache persistence | R11 did not fault-inject inside SQLite save. Source order is `upsertTxHashes()` -> await `IndexerCacheService.upsertIndexerCache()` -> await `updateSyncedBlockOfScripts()`. Thus failure before cache save returns prevents the app discovery checkpoint write. | Retry from the old app checkpoint. A crash during a chunked DB write needs an explicit uniqueness/transaction check; Neuron cache rows have generated IDs and indexed fields, not a declared unique `(walletId, txHash, lockHash)` constraint. Do not assume every partial write is atomic. |
| 5. After cache persistence, before application transaction persistence | R12 reconstructed this durable state in a disposable profile clone from the genuine R11 cache row: one pending cache row, no transaction/output rows, synced progress already beyond the transaction, and local-saved progress at H. A new Node process with Neuron's actual Queue resumed it from the persisted cache, fetched the real transaction from the local v0.5.4 RPC, wrote one transaction/output, marked the cache processed, advanced local-saved, and matched after DB reopen. This is a simulated interruption state, not a kill at the original write boundary. | Pending-cache resume is executable for this one known transaction. A crash after persistor commit but before `isProcessed=true` can replay persistence; this exact duplicate-persistor window remains untested. |
| 6. During restart and chain catch-up | R11 cold-restarted the native client and reopened the completed app SQLite DB; the known transaction remained available. It did not interrupt catch-up, restart with pending cache, or test a reorg. | Resume from native state only after version/genesis and anchor checks. Reconcile the copied tip against the destination's current chain, then continue from the accepted point. On mismatch or unsupported version, fall back to ordinary scan. Reorg behavior remains unproven. |

### Pending-cache restart simulation

R12 added a bounded test for interruption point 5. It copied the completed R11 disposable application profile, retained its real wallet identity/address metadata and actual faucet cache row, then removed completed transaction/output records from that copy, set that existing cache row back to unprocessed, and restored `localSavedBlockNumber` to the R11-observed pre-queue H floor. No transaction or cache record was created. A separate copy of the final R11 native store was file-hash verified and configured with no bootnodes/peers.

In a new Node process, Neuron's packaged Queue and LightSynchronizer started against the pending profile and local v0.5.4 RPC. The synchronization loop found the persisted pending row. The ordinary queue fetched the real transaction, ran address generation through the actual WalletService handler, persisted one transaction and one owned output, marked the cache processed, and advanced local-saved from H to H+1. Final progress was synced=`22,945,471`, localSaved=`22,944,379`; one cache row was processed; one transaction/output existed; close/reopen comparison was exact. The native cursor began at or above the app's starting synced checkpoint and advanced by seven blocks during the offline client run. The known faucet result was not historically refiltered.

This is a constructed recovery state in a disposable DB clone, not an OS kill at the original DB write boundary. It validates the post-restart pending-cache path but not SQLite crash atomicity, a partial batch write, or a crash after `saveFetchTx()` commits but before `isProcessed=true`. An earlier attempt paired this R11 app checkpoint with the older R10 native cursor; Neuron regressed synced progress to the lower native cursor and recovered the transaction. That mismatched attempt is excluded from the pass result and shows why a coordinator must reject a native cursor below the recorded app checkpoint or explicitly choose ordinary rescan.

### Neuron ordering and crash implications

Pinned `LightSynchronizer.synchronize()` awaits cache insertion before updating each `SyncProgress.syncedBlockNumber`. `IndexerCacheService.upsertIndexerCache()` first reads existing hashes and then saves new rows. Neuron's Queue processes block-grouped unprocessed cache rows, fetches committed transactions/headers and previous transactions, calls `TransactionPersistor.saveFetchTx()`, performs address generation, and only then marks cache rows processed. This gives a recoverable ordering in principle, but not a transaction spanning the cache, app progress, transaction entities, address metadata and processed flag.

R11's two-phase lifecycle is the minimum demonstrated cursor-preservation condition:

1. Create the legitimate wallet/address identity and its real `SyncProgress` rows through Neuron.
2. Stop Neuron and Light Client workers; verify no process has either database open.
3. Copy the native store to a staging sibling directory while preserving the source.
4. Validate a manifest containing client/profile version, genesis, exact Script hashes and roles, source cursor, app progress floors, file hashes, and chain anchor.
5. Install the staged store atomically on the same volume, retaining a rollback directory.
6. Write a durable phase marker before each transition. Resume idempotently from the last verified phase; never infer completion from directory existence.
7. On startup, verify Neuron progress rows exist for every transferred Script before calling the normal initializer. If they do not, restore the prior store or deliberately use ordinary scan from a safe floor.
8. Replay imported discovery results. Keep app progress behind until all results have been durably queued. Wait for every relevant cache row to be processed and validate transaction/cell state before exposing recovery readiness.
9. Reconcile chain tip/anchor and then continue ordinary synchronization. Any failed identity, version, hash, or canonical-chain check triggers rollback/rescan, not checkpoint advancement.

The current R11 scripts do not implement this coordinator, atomic directory swap, durable phase journal, rollback, or readiness gate. R11's application progress had start H and `syncedBlockNumber` advanced to the native cursor after cache insertion; `localSavedBlockNumber` advanced to the transaction height only after Queue completion. These values must not be collapsed into a synthetic “complete” height.

Neuron's LightSynchronizer loop calls `notifyAndSyncNext()`, which queries persisted unprocessed cache rows and invokes `processNextBlockNumber()`. R12 exercised that resume path in a new process against the reconstructed pending-cache state. Queue sets `isProcessed=true` only after transaction persistence and address work. A kill after persistor commit but before that update can therefore repeat persistence; Neuron's normal idempotency for this exact crash window remains unverified.

## Recovery alternatives

| Approach | What it restores | R12 evidence and cost limits |
| --- | --- | --- |
| A. Ordinary mnemonic restore + supported start height | Keys and derived addresses from user-held recovery material; Neuron rebuilds app state by scanning from the chosen floor. | Existing Neuron path and R9 ordinary sync provide the baseline mechanism. The R8 receive was found with 91 grouped Script queries at a start floor one block before its only activity. This is a tiny range and cannot represent a wallet with long history. No comparable elapsed-time run exists. Requires credentials the R8 fixture no longer has. |
| B. Ordinary cold backup | Existing keys, Neuron app DB, native Light Client DB and associated profile state, if captured consistently while workers are stopped. | Neuron's UI “backup wallet” implementation exports the wallet keystore JSON; it is not a complete application/native-state backup. A quiescent copy of the entire isolated profile could preserve both app and native state, but R12 did not execute or validate a complete profile restore. It risks copying device-local paths/settings and sensitive transaction/privacy metadata. It is likely the strongest “same install or whole profile restore” control, but not proven cross-device recovery here. |
| C. Waymark two-phase full-native-store transfer | Previously indexed Light Client chain/Script data, followed by Neuron app reconstruction from legitimate app progress. | R10 reports 2,190,898 bytes copied before startup and 2,024,534 bytes after startup, an internally inconsistent decrease that was not reconciled. R11 used the latter reported store. Treat the footprint as roughly 2 MB, not a precise transfer measurement. R11 observed no filtering reset when app progress pre-existed and did observe reset/filtering when it did not. End-to-end preparation, recovery and validation were not timed. It carries all native Script views and chain metadata, not just the user's Script. |

No measured side-by-side result supports a recovery-speed claim. The R11 `1,450 ms` is only the instrumented app-init-to-SQLite-reopen interval; it excludes source synchronization, copying, validation, ordinary baseline scanning, and matched catch-up. R9's 91 grouped calls and R11's imported-range query counts are not comparable work units. Historical Script filtering was avoided in the successful R11 path for the already indexed Script range, but actual CPU/network savings were not measured. The one-transaction fixture near its start height is explicitly a small-fixture mechanism comparison only.

## Full-store portability, privacy, and trust

Full native-store copying was sufficient for the R11 single-Script mechanism. It also copies unrelated registered Script indexes, chain/header data, global cursors, peer-independent metadata and other activity. Store bytes do not contain signing keys, but transaction and Script data are privacy-sensitive. With multiple wallets/accounts, the copy carries all store content unless separately scrubbed; selectively deleting native rows risks breaking shared cursors, header mappings and transaction closure.

The v0.5.4 store is RocksDB and is not a stable cross-version interchange format. R10/R11 prove process/store reopening for this same released client version and architecture. They do not prove forward/backward version compatibility, corruption recovery, or that an incompatible client detects a semantically stale but readable store. A whole-file SHA manifest detects byte changes during copy but not a malicious or incomplete source snapshot. A stale snapshot can be queried, but it must be reconciled to current canonical chain state; R11's continuation and one known output check do not prove all old results remain canonical.

Selective D2 remains justified only if representative measurements show full-store size, privacy scope, portability, or restore validation is unacceptable. It would reduce transferred content but increases adapter/format and completeness-validation burden. Keep it as a research path; R12 does not justify another RocksDB build.

## Validation fixture gate

The current R8 wallet cannot sign because its mnemonic/password were not preserved. Do not reuse it for a spend. The minimum useful fixture is a new isolated Neuron TESTNET wallet whose mnemonic/keystore password are retained in a local password manager or encrypted offline vault, never in project files, logs or command arguments; at least two confirmed receives at separated heights; one confirmed spend signed by that wallet; and at least one remaining live owned output. Record public transaction/block/Script identifiers and independently query canonical Cell status. No transaction or faucet claim was initiated in R12. Any wallet spend/broadcast requires explicit authorization and a funded disposable fixture.

## Repository and resource audit

`git remote -v` reports `origin` at `https://github.com/Ticoworld/waymark.git`. The WO research reports and `tools/wo07-r*` artifacts are untracked in the current checkout (`git ls-files` returned no tracked WO07-R7–R11 artifacts). They were not committed or pushed. No mnemonic, password, private key, keystore, native database copy or peer identity was added by R12. Existing untracked local evidence should be reviewed and selectively committed by the project owner; do not bulk-add temp stores or wallet artifacts.

C: began with `4,969,320,736` bytes free during the R12 audit and ended with `4,949,319,680` bytes free, about 624 MiB above the 4 GiB reserve. R12 created disposable profile/native-store clones and retained them for reproduction. No builds, peer sync, downloads, full-chain data, or cleanup occurred.

## Reproduction: Pending Cache

The R12 additions are `tools/wo07-r12/prepare-pending-replay.js`, `prepare-pending-client.js`, and `restart-pending-queue.js`. They reuse only disposable R11 profile/store copies, refuse to overwrite destinations, and hash-check the copied native store. The source profile/database and R11 native store remain unchanged.

```powershell
node tools/wo07-r12/prepare-pending-replay.js `
  "$env:TEMP\wo07-r6-neuron-asar" `
  "$env:TEMP\wo07-r8-neuron-profile-real-testnet-r11-phase2" `
  "$env:TEMP\wo07-r12-pending-replay-profile-v2"

node tools/wo07-r12/prepare-pending-client.js `
  "$env:TEMP\wo07-r11-native-store-phase2" `
  "$env:TEMP\wo07-r9-owned-source" `
  "$env:TEMP\wo07-r12-pending-client-v3"

# Start the offline v0.5.4 client in another shell, then:
node tools/wo07-r12/restart-pending-queue.js `
  "$env:TEMP\wo07-r6-neuron-asar" `
  "$env:TEMP\wo07-r12-pending-replay-profile-v2" `
  http://127.0.0.1:19110
```

## Exact next action

Do not advance to product integration or claim speed. The next decisive work is a bounded, fault-injected coordinator test on disposable copies, followed by a recoverable funded TESTNET fixture:

1. Implement only a test coordinator with a durable phase journal, staging+manifest verification, same-volume atomic install/rollback, version/genesis/Script/progress checks, pending-cache drain, and ordinary-scan fallback.
2. Inject process termination at every journal transition and at the cache/persistor/processed-flag boundaries; after each restart, require either exact recovered state or an explicit full scan from the saved safe floor.
3. Obtain a recoverable wallet and an already authorized source of TESTNET funding. Build separated receive history and one wallet-owned spend without placing credentials in the repo.
4. At a fixed canonical hash, compare ordinary mnemonic restore, a quiescent whole-profile backup restore, and two-phase native transfer. Record total prep + transfer + verification + reconstruction time, bytes, historical filter requests, catch-up and restart behavior. Keep source-generated coverage trusted unless an independent completeness oracle scans it.

Advance only if the coordinator survives interruption without silent checkpoint loss and the matched test shows a specific benefit over cold backup or ordinary restore. Otherwise keep the mechanism as research evidence and stop Neuron product integration.

## Pinned source references

- Neuron synchronization order and cursor setup: `light-synchronizer.ts` at `a926e3383d3a3e305b3bde7d233474515ef01a2e`, especially `synchronize()`, `upsertTxHashes()`, `updateSyncedBlockOfScripts()` and `initSyncProgress()`.
- Cache persistence/deduplication and pending-block queries: `indexer-cache-service.ts` at the same Neuron pin; `IndexerTxHashCache` uses a generated primary key and indexed, non-unique `txHash`, `lockHash`, `walletId` and `blockNumber` columns.
- Queue retry, persistence and processed marker: `queue.ts`; `TransactionPersistor.saveFetchTx()` in the same pinned source.
- Neuron backup behavior: `controllers/wallets.ts` `backupWallet()` writes the encrypted keystore JSON through a save dialog; it does not export the application DB or Light Client store.
- Executable R11 observations and limitations: [WO07-R11](WO07_R11_NEURON_APPLICATION_RECOVERY.md); native-copy evidence: [WO07-R10](WO07_R10_CROSS_DEVICE_HANDOFF.md); ordinary owned Script baseline: [WO07-R9](WO07_R9_REAL_NEURON_RECOVERY.md).
