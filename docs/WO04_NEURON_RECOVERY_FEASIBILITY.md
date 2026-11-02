# WO04: Neuron Recovery Feasibility and Independent Opportunity Investigation

Research date: 30 October 2026. Source findings are pinned to Neuron `develop` commit `a926e3383d3a3e305b3bde7d233474515ef01a2e`, released `v0.204.1` commit `d3a7467d218e4b6f777326682a83fec802669c00`, and the current `rc/v0.209.0` source revision `484a46dadde2a0adfd7975d0159be898b199cf80` where explicitly noted. No source checkout, build, sync, wallet access, or production change was made.

## Executive summary

Neuron already has a materially useful equivalent of the most basic Waymark Lite idea: when a mnemonic is imported, its account public key is derived deterministically, default addresses are regenerated, and the historical scan starts without the “new wallet: start at current tip” shortcut. In Light Client mode Neuron also records per-Script start and synced heights and replays the Script range from the Light Client. This means an ordinary seed restore can recover historical activity without importing source-device state, although the scan boundary may be broad and the local transaction/indexer/application caches are rebuilt.

A fresh destination does not appear to inherit the former computer’s per-Script progress, descriptions, local labels, multisig records, wallet transaction cache, or Light Client database through the supported mnemonic/keystore import flows. That is a real state migration distinction, but this investigation did not find a controlled measurement showing that reusing those stores would improve recovery materially over Neuron’s current supported restore. Copying a whole Neuron data directory is not an acceptable recommendation: it couples encrypted wallet files, app metadata, network databases and schema-specific caches, and would carry device-local encrypted key material even if it does not disclose the mnemonic.

There is a current user report for `v0.209.0` of wallet synchronization stopping after a transient SQLite BUSY error with node and indexer already at tip. That supports investigating sync-worker interruption and error recovery in Neuron itself. A saved-state package does not fix a terminated sync loop or SQLite contention, and the report is user-provided rather than independently reproduced.

**Verdict: LIMITED OPPORTUNITY.** Neuron already supports seed recovery plus historical scan; Waymark’s strongest distinctive prospect would be a small, supported export/import of narrowly selected public per-Script scan metadata (and perhaps validated wallet cache records) to reduce repeated work on a new computer. That opportunity is plausible but unproven, and should not be developed until a same-version, same-fixture baseline/candidate experiment shows a measurable advantage. A separately scoped Neuron sync-resilience fix may be more directly relevant to the current public complaint, but it is not a Waymark state-transfer contribution.

## Environment and source identity

- Available space at inspection: 20.13 GB on `C:`. No Neuron or CKB Light Client source checkout was present in the Waymark `repos` directory; the only checkout there is `pocket-node`. No repositories or caches were copied or changed.
- `https://github.com/nervosnetwork/neuron` is the official repository linked from Nervos Network’s organization; `develop` resolved to `a926e338…` on 12 September 2026. The release API identified `v0.204.1` (10 April 2026), whose tag resolves to `d3a7467d…`.
- The repository also has `rc/v0.209.0` at `484a46dad…`; the latest published release API still returned `v0.204.1`. Do not treat 0.209.0 as released. The wallet package manifest at `develop` declares `0.204.1`; the corresponding `v0.209.0` report links the same relevant implementation files to its release-candidate commit, but a complete code diff of all recovery behavior was not established in this read-only source pass.
- `packages/neuron-wallet/.ckb-version` says `v0.209.0`; `.ckb-light-version` says `v0.5.4` at current develop. These are bundled client version selectors in the development tree, not proof of the binaries in the older 0.204.1 installer. Release-specific bundled binary versions remain to be checked from release artifacts/manifest. Lumos dependencies in the develop wallet manifest are pinned at `0.23.0`; CKB types at `0.109.1`.
- Source was read via GitHub raw/content/tree endpoints rather than a clone. GitHub API rate limiting ended some later reads; claims below are limited to code that was successfully inspected and linked. Relevant line links are pinned to SHA.

## Neuron architecture

The wallet controller derives a BIP39 seed and CKB account extended public key from the mnemonic. It creates an encrypted Neuron keystore using the entered password. Wallet metadata stores the extended public key separately from the keystore file. Address generation is deterministic from that public key; addresses and their Script metadata are persisted locally. Importing a mnemonic is marked `isImporting=true`; only creation of a brand-new wallet attempts to use the current RPC tip as its starting block. Thus seed import is intentionally historical recovery, not a watch-only or “start at tip” flow.

Wallet state spans several stores. The code identifies a key/value wallet-list store, per-wallet keystore JSON files, address metadata, and network-specific TypeORM/SQLite chain databases. Chain entities include transactions, inputs/outputs, indexer transaction-hash cache, sync progress, sync info, cell-local information, descriptions, asset-account/DAO-related data and multisig records. Settings choose separate `full` and `light` data locations; Light Client node data is held under network-specific `chains/light/testnet` and `chains/light/mainnet` paths. The bundled Light Client has its own on-disk state and registered Scripts; Neuron’s Light RPC reads registered Scripts and their block positions. Neuron’s synchronizer then asks for transaction activity over `[saved syncedBlockNumber, registered script blockNumber]`, stores transaction hashes and advances per-Script progress.

For full-node mode, there are distinct workloads:

1. **Full-node chain synchronization:** obtain and validate CKB chain data to the tip.
2. **Indexer synchronization:** build/query the indexer’s chain-wide searchable index.
3. **Wallet-specific historical scanning:** query Neuron-derived Scripts and obtain relevant transactions over covered history.
4. **Application database reconstruction:** persist wallet transaction/Cell/history/description/DAO projections and UI state.

A wallet-state import could only reduce some wallet-specific scanning and app reconstruction. It cannot make a fresh full node download/verify the chain or make a fresh indexer build its chain-wide index.

## Existing recovery capabilities

- **Mnemonic recovery:** `importMnemonic` follows the same deterministic seed/key derivation as creation, then creates local password-protected key material and generated address records. Account index/address derivation is reproducible; names, local descriptions, active wallet selection and other user metadata are not encoded in the phrase.
- **Keystore backup/import:** the backup operation writes a JSON keystore file. It is encrypted by the user password but is still secret-bearing wallet material and must be handled as a key backup. Import reconstructs the wallet key/account, not its old transaction, DAO or sync cache.
- **Extended public key export/import:** watch-only import can reconstruct address ownership but cannot sign. Xpub export is privacy-sensitive because it links derived addresses and transaction history; it is not a recovery checkpoint or a signing backup.
- **Historical start:** newly created wallets try to start at current tip. Mnemonic import does not set that shortcut, leaving the imported address/script scan to cover prior history. UI exposes wallet start block update functionality; source contains `startBlockNumber` wallet metadata, but this pass did not establish whether ordinary users can choose an arbitrarily low height or precisely how that setting is applied for all sync modes. Historical selection is therefore only partially verified.
- **Persistent progress:** Light Client mode stores per-Script `lightStartBlockNumber`, `syncedBlockNumber`, and local saved block number in the chain DB. The Light synchronizer retrieves registered filters and asks for the transaction range since the last saved script height. Full synchronizer stores cached transaction hashes and processed block state for its own replay pipeline. Interruptions therefore have local checkpoints on the same installation; a fresh installation lacks them and must rebuild.
- **Rescan/reset:** source exposes a clear-node-cache operation that stops Light Client, deletes its configured data directory and cleans local DB state before restarting. It demonstrates an explicit reset/recovery path, but not cross-device restore. Network switching and cleanup code also operate on DB state.
- **Backup scope:** inspected backup flow exports wallet keystore only. No supported complete application-data backup/restore or portable recovery package was identified in the inspected controller/service/API paths. This is a bounded search result, not proof that no platform-level folder backup or third-party procedure exists.

## Verified recovery gaps

1. **No supported selective cross-computer state import was found.** The public mnemonic and keystore restore paths reconstruct keys/addresses but do not accept former sync progress, discovery verdicts, transaction cache, DAO/application projections or Light Client database state.
2. **A fresh Light Client destination has no source node DB.** It must initialize its own Light Client state and register derived scripts, then scan the historical range exposed by its normal recovery policy. Neuron does persist and resume scan progress once created on that destination.
3. **Application history is a projection/cache, not seed material.** Transactions, local labels, descriptions, DAO views and related history tables reside in local stores and must be queried/rebuilt when absent. Exact coverage and user-visible restoration semantics have not been runtime tested in WO04.
4. **Sync interruption can be an independent current problem.** Open report #3508 describes `v0.209.0` internal full-node mode with node and indexer at tip but Neuron wallet cache stuck after `SQLITE_BUSY`; report says synchronization loop stopped and UI kept stale progress. The reporter’s source links and logs provide detailed evidence, but the event has not been independently reproduced and does not establish prevalence.

The amount of unnecessary work is unknown. No Neuron runtime recovery timing, profile, or matched state comparison was run. Do not borrow Pocket timing results or assume Neuron has Pocket’s empty-account discovery behavior.

## Waymark compatibility

| Capability | Pocket/Waymark | Neuron today | Remaining gap |
| --- | --- | --- | --- |
| Seed-based wallet recovery | Demonstrated on Pocket | Deterministic mnemonic import | Basic capability exists in both |
| Historical start-height selection | Research fixture used explicit account floors; Lite seeds a coarse hint | Imported mnemonic skips new-wallet tip shortcut; exact supported user control not established | Need inspect UI path and test actual floor |
| Account discovery | Pocket derives accounts and probes candidates | Address generation from account xpub; CKB lock Scripts scanned; multisig has separate flow | No evidence Neuron has Pocket-style account-index discovery |
| Preserved discovery results | Full proof restored Pocket discovery rows | No portable result import identified | Potential gap, but equivalence and safe coverage unknown |
| Persistent scan checkpoints | Pocket native and Room progress included | Local per-Script Light progress and full sync cache persist | Same-install interruption largely addressed; fresh-device transfer absent |
| Light-client DB recovery | Pocket package included logical native snapshot | Embedded CKB Light Client has its own node-data directory, no import path identified | Could be expensive, version-sensitive; no proven performance gain |
| Transaction history recovery | Package omitted app tx/DAO caches; rebuilt normally | Chain DB stores tx/input/output/indexer cache | Fresh app cache rebuilt by script scan; could be selectively portable only with validation |
| DAO reconstruction | Verified in Waymark fixture | DAO/account data and chain history are local; Neuron has DAO flows | Must test exact position and cache reconstruction; unknown incremental value |
| Canonical-chain verification | Waymark verified common hash/state | CKB node/light client verify chain; sync consumes canonical node/indexer results | A snapshot importer still needs anchor/reorg validation; no portable proof found |
| Cross-device migration | Waymark research-only trusted-self package | Keystore, mnemonic, xpub workflows; no full state migration found | Supported selective migration is the potential differentiated work |
| Recovery after interruption | Pocket experiment cold restart | Per-script and cache checkpoints stored locally; issue #3508 indicates worker failure may halt progress until reset | Test resume behavior and fix error-handling independently |

Pocket-specific components that do not transfer directly include Android Room schema, JNI registration behavior, Pocket’s discovery/reconciliation policy, native SQLite schema, and Pocket app cache semantics. Reusable concepts are seed-independent public identity matching, selected non-secret state, checkpoint anchoring, destination-native key protection, catch-up, exact state comparison and cold restart. Neuron would need a Neuron-owned exporter/importer and compatibility policy; Waymark’s package is not compatible.

## Security considerations

- **Network and identity:** bind every Script/progress row to the network/genesis hash, exact derived Script/hash type, wallet public identity and account/address derivation scheme. Neuron currently has separate full/light and network connections, but copied rows without this binding risk cross-network or wrong-wallet associations.
- **Coverage and chain anchor:** record start and checked-through height plus block hash and the scan algorithm/version. A saved height alone cannot establish that all Scripts were registered or checked. Verify anchor against the destination chain, detect reorgs, and rescan the affected suffix. Never treat absent cached activity as proof of no funds.
- **Stale state and completeness:** import only from a quiesced, transactionally consistent source. Catch up from anchor and compare; support interrupted import idempotently. Omitted or newly derived scripts must still be scanned.
- **Schema/version compatibility:** source DB entities have years of migrations and separate light/full database names. Whole-file copy risks migration mismatch, WAL inconsistency, foreign-key mismatch and incompatible Light Client state. A versioned logical export is safer than copying SQLite files, but still requires validation and bounded import.
- **Secrets/privacy:** never transfer mnemonic, private key, keystore JSON, password, OS credential or device keystore material as “state.” Keystore export is explicitly secret-bearing. Even xpubs, Scripts, transaction IDs, labels, balances and DAO data are privacy-sensitive and reveal wallet activity.
- **Malicious/corrupt package:** hashes only detect accidental changes if the expected digest is trusted; an authenticated self-export still does not prove correct source scanning. Validate every row, cap resource use, reject unsupported versions, and preserve normal scanning as fallback.
- **Canonical data:** node/indexer remain authoritative. Imported transaction projections and Cells must be reconciled, and duplicates/missing rows checked. Cold restart must prove importer and sync state are durable.

No production protocol is proposed because the opportunity has not passed the value test.

## Evidence table

All source links below are pinned to `a926e3383d3a3e305b3bde7d233474515ef01a2e` unless the row says otherwise. Line anchors are useful navigation points; GitHub may render nearby lines differently as files evolve.

| Claim | Repository / pin | File and function | What it establishes |
| --- | --- | --- | --- |
| Current development identity | `nervosnetwork/neuron`, develop `a926e338…` | [wallet controller](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/controllers/wallets.ts#L50) | Official repository’s development revision was inspected; release data separately identifies `v0.204.1`. |
| Mnemonic creates seed, extended key and account xpub | same | [wallets.ts, importMnemonic/createByMnemonic](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/controllers/wallets.ts#L56) | Import derives CKB account key material from mnemonic and creates local wallet. |
| New wallet vs import start behavior | same | [wallets.ts, createByMnemonic](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/controllers/wallets.ts#L90) | Only non-import path attempts current tip; import does not set that shortcut. |
| Keystore backup and xpub export are separate operations | same | [wallets.ts, backupWallet/exportXPubkey](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/controllers/wallets.ts#L345) | Keystore JSON backup and public extended-key export exist; neither is a state archive. |
| Wallet metadata and encrypted keystore separated | same | [wallet service](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/services/wallets.ts#L1) | Service stores wallet list metadata and per-wallet keystore files separately. |
| Per-Script progress fields | same | [sync-progress entity](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/database/chain/entities/sync-progress.ts#L24) | Script hash/type and start/local/synced block fields are persisted. |
| Light sync replays Script range and advances progress | same | [light synchronizer](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts#L120) | Retrieves Light RPC scripts, asks for transactions over saved-to-current range, updates progress. |
| Current package and client selectors | same | [package manifest](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/package.json), [.ckb-version](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/.ckb-version), [.ckb-light-version](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/.ckb-light-version) | Develop declares wallet 0.204.1 and selects CKB 0.209.0 / Light Client 0.5.4. Release installer’s exact bundled versions remain unverified. |
| Current reported full-mode wallet sync stall | `nervosnetwork/neuron`, issue #3508, source commit `484a46dadde2a0adfd7975d0159be898b199cf80`, opened 31 Aug 2026 | [issue report](https://github.com/nervosnetwork/neuron/issues/3508) | User reports `v0.209.0` node/indexer at tip but wallet cache stalled after SQLite BUSY. Not independently reproduced; not evidence of state-import benefit. |
| Prior Waymark findings and limits | local Waymark checkout, existing research | [How it works](how-it-works.md), [Pocket proof](pocket-proof.md), [Lite/Full follow-up](lite-full-recovery/README.md) | Pocket-only proof, tested timing conditions, security boundary and explicit lack of Neuron compatibility. |

## Opportunity assessment

| Dimension | Assessment |
| --- | --- |
| User benefit | Potentially meaningful if a typical Neuron Light Client restore spends substantial time repeating Script history work or rebuilding a large app cache; not measured. |
| Technical feasibility | Moderate. Neuron already exposes the relevant per-Script identity/progress and cache entities, but importer must be integrated with its DB migrations, node RPC and sync orchestration. |
| Distinctiveness | Selective cross-device progress/state import appears distinct from existing mnemonic/keystore/xpub backup. Basic historical recovery itself is already present. |
| Integration effort | A proof fixture is modest; a supported, versioned feature with validation, migration, reorg handling and UX is materially larger. Whole DB copying is not a viable shortcut. |
| Maintainer relevance | Current open sync interruption report indicates interest in wallet-sync reliability. It does not establish maintainer demand for migration/import, and no maintainer response or approval is claimed. |
| Evidence quality | Source-level gap established; value and performance unknown. One current user report is specific but not independently reproduced. No Neuron experiment was run. |

## Recommended next action

**LIMITED OPPORTUNITY.** Do not build a production feature or port the Pocket package. The next useful action is one bounded Neuron experiment only if it can use a disposable TESTNET wallet and the same supported release candidate/build on both arms.

### Smallest decisive experiment

1. Pin one ordinary Neuron build and exact bundled Light Client version. Use the same disposable TESTNET mnemonic-derived wallet and generated Scripts. Keep source and target chain state fixed.
2. Arm A: fresh destination, normal supported mnemonic recovery with fresh password-protected key material; measure separately from Light Client startup and chain readiness. Allow normal scan to reach a fixed target.
3. Arm B: independent fresh destination/security, same Neuron build and fixture, importing only a versioned logical export of public Script identity and validated per-Script scan boundary/progress (not source keystore, full DB or unverified transaction rows). The candidate must exceed the current normal import behavior by reusing prior-device coverage, not merely selecting the same known start height.
4. Keep the Light Client chain-ready boundary identical. Record node/LC tip readiness, Script registration, per-Script scanned heights, transaction cache processing and application reconstruction as separate timestamps. This separates wallet work from full-node/indexer synchronization.
5. At a common canonical TESTNET block, compare exact owned Scripts, transaction hashes/history, live Cells and balances; include DAO position if the fixture has DAO activity. Then cold restart each destination and repeat acceptance.
6. Candidate passes only if it is faster in repeated controlled trials without missing history/Cells, incorrectly completing discovery, crossing networks, or relying on source signing material. If normal Neuron import already reaches equivalent coverage at similar cost, stop: no state-transfer project.

Estimated minimal test complexity: **medium**, about several focused engineering days for fixture harnessing, logical export/import instrumentation and exact comparison, assuming the disposable wallet and reference oracle are already available. This is a planning estimate, not measured Neuron work. A production feature would be substantially larger because it needs schema/version policy, checkpoint/reorg logic, privacy and corruption handling, UX, support and migration tests.

A cheaper preliminary source check before that experiment is to inspect the `v0.204.1` release installer manifest/config for exact bundled client binaries, and trace the UI/controller path for arbitrary start-height edits. This report does not represent either fact as established where source evidence was incomplete.
