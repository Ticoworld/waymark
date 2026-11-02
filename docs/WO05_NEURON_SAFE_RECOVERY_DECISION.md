# WO05: Neuron Safe Recovery Decision

Research date: 30 October 2026. Primary source pin: Neuron `develop` `a926e3383d3a3e305b3bde7d233474515ef01a2e`. Release baseline: `v0.204.1` / `d3a7467d218e4b6f777326682a83fec802669c00`. Later source checked: `rc/v0.209.0` / `484a46dadde2a0adfd7975d0159be898b199cf80`. The examined recovery and sync files have no diff between develop and that RC commit. The release notes identify bundled CKB v0.204.0 and CKB Light Client v0.5.4; develop's version selectors are not substituted for the release versions. This was a read-only source investigation. No Neuron build, chain sync, real-wallet access, source modification, PR or external contact occurred.

## Decision

**REVISE DIRECTION.** Do not implement a Neuron checkpoint-only importer or a Waymark state bundle on the current evidence. Progress-only transfer is unsafe for an empty wallet database. The smallest safe alternative is Neuron's existing ordinary mnemonic restore plus its existing user-selected Light Client start height, with normal scan/reconstruction. This already provides the only safe way identified here to narrow the scan: begin at a chosen historical point and let Neuron query and rebuild from there.

A verified result-data importer is technically conceivable, but it must carry enough indexed results and dependencies to reconstruct Neuron's wallet database, then verify the result against the chain. If verification repeats the full Script scan, it removes the proposed speed advantage. If it does not, it relies on a source completeness claim and creates a funds/history omission risk. No source evidence or timing currently shows that this larger mechanism gives a net benefit over choosing a suitable existing start height. No controlled test is justified until a source/destination fixture demonstrates that normal restore from a safe known floor remains substantially slower than necessary.

The only specific unresolved fact that could change this decision is whether, on a representative wallet and fixed Neuron Light Client version, normal restore from the earliest known wallet activity still performs a large amount of irrelevant scanning/reconstruction that can be avoided without repeating an equivalent verification query. The cheapest resolution is a disposable TESTNET baseline measurement using the UI start-height control and exact database-versus-chain acceptance; no importer is needed for that baseline.

## Source and change check

The existing sparse source checkout is in the system temp directory, pinned to `a926e338…`; it was not placed in the Waymark repo. `git diff` between that commit and `484a46dad…` showed no changes in `light-synchronizer.ts`, `sync-progress.ts`, `sync-progress` entity, sync queue, transaction persistor, wallet controller or PageContainer start-height UI. Develop resolves to `a926e338…`; `rc/v0.209.0` resolves to `484a46dad…`. WO04's latest published release was `v0.204.1`; its release notes specify CKB v0.204.0 and Light Client v0.5.4. This report uses source implementation common to the pins and does not claim the unreleased `v0.209.0` is generally available.

## Synchronization data path

1. **Script registration and coverage.** `LightSynchronizer.initSyncProgress()` derives Neuron's default, ACP and legacy ACP lock Scripts from local address metadata, chooses the wallet start boundary, calls Light RPC `setScripts(..., 'partial')`, and creates per-Script progress records. The Light Client node database owns the registered Script filters and their current block positions. Neuron's SQLite owns the application mapping from Script hash to wallet ID and its own scan/persistence positions.
2. **Discover transaction hashes.** On each pass, `upsertTxHashes()` gets the registered Scripts and Neuron's matching `SyncProgress`. For each Script it calls Light RPC `get_transactions` over `[syncStatus.syncedBlockNumber, registeredScript.blockNumber]`, paginating results. It inserts every returned transaction hash, tx index, block, lock hash, address and wallet ID into `IndexerTxHashCache`.
3. **Advance the Script position.** `updateSyncedBlockOfScripts()` writes the Light Client's current registered-script block position to Neuron's `syncedBlockNumber`. `synchronize()` does the hash query/cache insertion first, then updates that position. This ordering is important: progress alone is not the historical result set.
4. **Fetch and persist records.** The block queue groups unprocessed cached hashes by block. It waits until the Script progress is at least that block, confirms the Light Client has the transaction, fetches the transaction and header from the connected CKB RPC, fetches previous transactions needed to resolve input Cells, and passes each transaction to `TransactionPersistor.saveFetchTx()`. It then marks the hash processed. The persistor stores transaction fields, inputs, outputs, statuses, cell relations and selected detailed lock/type data. Spending transactions update earlier outputs from live to dead. DAO output data and deposit outpoints are represented in output records when provided/reconstructed. Address-gap generation can add addresses discovered through transaction references.
5. **Balances/history/DAO.** Balance and live Cell queries use persisted output records plus the CKB indexer for relevant Scripts; history uses transaction/input/output records; DAO views use output DAO data, deposit outpoints and chain-derived state. The chain DB is application state/cache, not an independent authority. The connected CKB chain/RPC supplies canonical transactions and headers; the Light Client's script-filter store supplies the historical query results. A progress number cannot reconstruct the records it says were scanned.
6. **Restart.** The sync queue and worker are restarted from the local databases. Unprocessed indexer-cache entries can be processed after restart; per-Script sync positions and saved local sync positions are persisted. This is same-install crash recovery. It does not make a progress-only export sufficient on an empty destination.

## Question 1: What progress-only loses

In the example, Computer A has scanned through block 200,000. Computer B receives only Script identity and a 200,000 checkpoint, with an empty Neuron wallet DB. Neuron will query from 200,000 onward. The transactions found between 100,000 and 200,000 are not in B's `IndexerTxHashCache`; their transaction bodies are not in B's transaction table; their input/output rows, live/dead relationships, histories, balances and DAO links are not there either. A later spend after 200,000 may refer to an earlier output that B never constructed, so the destination can fail to associate the spend with the earlier Cell. It can show missing history or a wrong live Cell/balance/DAO position. It cannot safely infer those records from the checkpoint.

If B ignores the transferred checkpoint and starts at 100,000 or earlier, it can reconstruct those records normally. In that case the transferred progress did not save the historical Script scan. Thus **Option A, progress only, is rejected** except as an untrusted scan-start hint, never as a completed-coverage assertion.

The checkpoint schema itself is not self-sufficient. `sync_progress` fields include Script hash, args, code hash, hash type, script type, wallet ID, light start, local saved height, synced height, cursor, deletion flag and address type. `IndexerTxHashCache` separately carries transaction hash, lock hash, wallet ID, block number and processed flag. Transaction, input and output tables form additional dependent records.

## Question 2: Smallest additional information

For an immediately usable wallet database, there is no “checkpoint plus a few fields” package. At minimum it needs:

- every owned Script identity and account/address association, with network/genesis, script type and derivation/address scheme;
- coverage start and end per Script, and a verifiable chain anchor for the covered range;
- the complete matching transaction set, including block number/index and canonical block/hash association;
- transaction bodies and headers, and the previous-output bodies/data required to resolve inputs (including dependencies that do not themselves match a wallet Script);
- the reconstructed per-transaction inputs and outputs, statuses/live/dead relations, DAO deposit links/data, and any records needed for current wallet-specific queries;
- indexer-cache completion/processed state and any local address-discovery results needed so Neuron does not silently omit Scripts;
- network, schema/format and Neuron/Light Client compatibility identifiers.

A more conservative package could carry only per-Script identity, checked boundary and a manifest of matching hashes, then have the destination fetch all matching bodies and reconstruct every projection. But fetching or independently validating that manifest against the Light Client still repeats the expensive Script query. In that design the hash manifest adds trusted assertions and complexity without demonstrable saved work. Exporting and importing logical records directly is safer than whole SQLite files, but still requires dependency-complete import, migration handling and verification. Copying the complete app directory or SQLite files is rejected: it can carry encrypted key material and device-local metadata, depend on WAL consistency and schema versions, and may cross the full/light/network DB boundary.

## Question 3: Destination verification

The destination must not trust a source statement that “Script X was scanned through height Y.” To accept transferred results it would have to:

- derive every expected Script locally from the freshly restored public account identity and reject unknown or missing identities;
- require exact network/genesis and format/version match;
- check every transaction hash against its recomputed body hash, validate the claimed block/header, and confirm headers/transactions on the destination's canonical chain;
- independently query each Script over the claimed range and compare the complete ordered result set, or have an equivalent authenticated completeness proof supported by Neuron/CKB Light Client. The inspected Neuron interfaces expose range queries, not such a compact completeness proof;
- rebuild wallet transaction/input/output records using Neuron's own code and compare owned Scripts, all matching history, live Cells, balances and DAO relations to canonical RPC/indexer results;
- catch up from the verified checkpoint to target, handle reorgs by invalidating/rescanning the affected suffix, and cold restart before acceptance.

Transaction inclusion proofs alone do not prove completeness of a Script query: they prove included items, not that no matching item was omitted. A self-authored digest detects corruption only when separately trusted; it is not evidence that the source scan was complete. Without a completeness proof, the only conservative verification is to repeat the historical Script query, removing most of the candidate's potential query-work savings.

## Option comparison and avoided work

| Option | Safe on an empty destination? | Work it may avoid | Decision |
| --- | --- | --- | --- |
| A. Progress only | No, if used to skip covered history. Yes only if ignored as a checkpoint and rescanned from a safe lower bound. | At most historical Script range queries, but omits their output records; rescanning gives no saving. | Reject as recovery state. |
| B. Progress plus selected historical records | Potentially, if dependency-complete, canonical, complete for all Scripts and reconstructed through Neuron's normal persistence logic. | Could avoid repeated Light Client `get_transactions` over covered ranges and application DB reconstruction, but not necessarily validation. | Technically possible, not currently justified. Verification likely repeats the query absent a completeness proof. |
| C. Advisory information | Safe only as a conservative starting-height hint; unsafe as proof of completed coverage. | Can narrow history scan if the user knows a correct floor, but does not avoid work after that floor. | Existing UI already supports this. No distinct Waymark advantage established. |

The Light Client's chain/network synchronization is separate from wallet Script queries. With an external Light Client, the node and its chain state must still initialize/catch up. For Neuron full-node mode, full CKB synchronization and its chain-wide indexer synchronization are not replaced by a wallet package. Wallet-specific Script scanning is the `get_transactions`/indexer query work. Application reconstruction is fetching transaction/header/previous-output data and persisting Neuron's wallet projections. A package may move reconstruction cost to source export or destination import and add verification cost; count all of those in a candidate comparison.

## Existing start-height control

The WO04 uncertainty is resolved at the inspected develop/RC pins:

- `WalletsController.importMnemonic()` calls `createByMnemonic(..., isImporting: true)`. New wallet creation alone asks RPC for current tip as `startBlockNumber`; mnemonic import does not.
- `PageContainer` sees an imported-wallet local flag and opens the start-height dialog in Light Client mode.
- The dialog accepts a numeric height, caps it to known best tip, and warns when the chosen number is earlier than the initial value. The wallet update API accepts it only for Light Client. If lowering the saved start height, controller code clears Light Client node cache so old coverage does not survive inconsistently, then sync restarts.
- This is a user-selected floor, not previous-device progress or a verified historical-activity boundary. Too-high values can omit earlier transactions. Starting lower allows Neuron's ordinary source-query and record-persistence path to rebuild history.

Thus the remaining candidate must outperform this existing mechanism by reusing verified transaction results without repeating the same range query. A copied start height by itself is not a differentiated recovery feature.

## Work-saving conclusion

No measured Neuron timing is available. The code shows what could be avoided, but not whether it is substantial for a typical wallet. Option A saves only the hash-query work by skipping it and thereby loses the query results needed by the empty DB. Option B could avoid both historical Script query and record reconstruction only if complete records are trusted/verified; current Neuron source has no compact range-completeness proof. Requerying the same range to verify defeats the first saving. Option C is already available in Neuron and is only beneficial when the user knows a correct safe floor; it does not establish old coverage.

**The report cannot claim a meaningful safe time saving today.** A controlled importer experiment is premature. First obtain baseline evidence that, with Neuron's supported user-selected start point set to the earliest known activity, important work remains that cannot be avoided by existing controls. If a large repeated cost remains and a canonical completeness-verification route is shown to cost materially less, revisit Option B. Otherwise stop Neuron Waymark.

## Smallest decisive experiment if prerequisites are met

This is not authorized or run by WO05. Before a candidate arm is justified, a read-only/runtime baseline must establish the issue. If that evidence crosses the threshold, use:

1. One pinned released Neuron version and exact bundled Light Client version; same disposable TESTNET mnemonic-derived wallet, same populated Script set (including account/address paths, DAO activity if relevant), and fixed common target block/hash.
2. Arm A: fresh destination and fresh password/key protection; normal mnemonic restore; use Neuron's existing UI start-height control at the verified earliest activity floor; let normal Light Client registration and wallet reconstruction finish.
3. Arm B: independent fresh destination/security; same build and fixture; import the smallest dependency-complete logical state candidate, excluding all source signing/keystore/device secrets. Count source export time, destination import time, all destination validation time and catch-up separately.
4. Keep Light Client chain readiness separate from wallet work. Timestamp Light Client startup/tip, Script registration, per-Script historical query progress, transaction fetch/header/previous-output work, DB persistence and final app/DAO readiness. For full-node mode separately record full node tip and indexer tip; do not attribute either to wallet-state reuse.
5. At identical canonical block hash compare derived owned Scripts and addresses, complete transaction hash/history set, input/output relationships, live Cells, balances, and exact DAO positions/deposit links where applicable. Then cold restart each destination and repeat the full comparison.
6. Require repeated runs or randomized arm order. Candidate must have lower end-to-end time including export/import/verification, with no missing or extra history/Cells and no reliance on unverified source completion claims. If it cannot beat the supported start-height baseline without reducing verification, stop.

The smallest practical prerequisite is a disposable TESTNET wallet and canonical oracle at a known floor/target. No accurate runtime estimate is available; likely several focused days to instrument and compare the two flows if the fixture/oracle already exists. A production importer would be much larger. Since WO05 finds no sufficient candidate advantage yet, do not schedule this two-arm importer test now.

## Evidence table

All Neuron links below are pinned to `a926e3383d3a3e305b3bde7d233474515ef01a2e`; the checked RC comparison is `484a46dadde2a0adfd7975d0159be898b199cf80`. Relevant recovery/sync files are unchanged between those commits.

| Finding | Source evidence | Establishes |
| --- | --- | --- |
| Light query uses saved Script position and inserts transaction cache before progress update | [light-synchronizer.ts, `upsertTxHashes` / `synchronize`](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts#L91) | Script transaction range query, cache insertion and subsequent synced-height update order. |
| Progress record fields | [sync-progress.ts entity](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/database/chain/entities/sync-progress.ts#L10) | Script identity, wallet ID, start/local/synced heights, cursor and flags are distinct from tx records. |
| Progress initialization and reads | [sync-progress.ts service](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/services/sync-progress.ts#L9) | New rows initialize positions; local saved and synced progress are separately queried/reset. |
| Transaction hashes are wallet/block scoped and processed separately | [indexer-cache-service.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/indexer-cache-service.ts#L245) | Cache is an input queue, not just a height checkpoint. |
| Transactions are fetched, previous outputs resolved, then persisted and marked processed | [sync queue](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/queue.ts#L124) | Chain RPC data feeds DB reconstruction; queue processing follows. |
| Transaction persistence computes output status and stores input/output links and DAO fields | [transaction persistor](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/services/tx/transaction-persistor.ts#L198) | Records needed for transaction history, live/dead state and DAO linkage are derived/persisted. |
| Lowering start height clears old Light Client cache and restarts | [API controller](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/controllers/api.ts#L390) | Lowered floor causes Light Client cache clear and resync instead of retaining incompatible later coverage. |
| Imported wallet opens start-height dialog | [PageContainer hook](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-ui/src/components/PageContainer/hooks.ts#L30), [dialog](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-ui/src/components/SetStartBlockNumberDialog/index.tsx#L56) | Existing Light Client UX accepts a block number capped at known tip. |
| Mnemonic import differs from new wallet | [wallet controller](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/controllers/wallets.ts#L69) | New wallet gets current-tip starting point; import does not take that branch. |
| Store separation | [ORM config](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/database/chain/ormconfig.ts#L75), [clean operation](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/database/chain/index.ts#L17) | Network/mode DBs hold app cache entities; clearing records and progress are distinct. |
| Transaction/output dependency fields | [output entity](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/database/chain/entities/output.ts#L8), [input entity](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/database/chain/entities/input.ts#L8), [indexer cache entity](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/database/chain/entities/indexer-tx-hash-cache.ts#L1) | Exact cache records include statuses, cell outpoints/data/DAO links and processing markers. |
| Relevant source stable through `v0.209.0` RC | develop and `484a46dad…` pinned file diff | The inspected sync/start-height behavior did not materially change in the RC. |

## Exact next action

Do not implement or run a state importer. If a disposable TESTNET fixture already exists, run only a normal Neuron recovery using its supported start-height prompt, instrumenting Light Client readiness separately from Script query and application reconstruction. Record exact transaction, live Cell, balance, ownership and DAO state at a fixed chain hash plus cold restart. Proceed to a candidate state-transfer experiment only if that baseline demonstrates substantial avoidable wallet work and a cheaper-than-rescan completeness verification is identified. Otherwise stop Neuron Waymark.
