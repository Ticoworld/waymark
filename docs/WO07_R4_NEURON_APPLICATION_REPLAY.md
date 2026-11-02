# WO07-R4: Neuron Application Replay

Date: 31 October 2026

## Verdict

**OWNERSHIP OR FIXTURE BLOCKED.** Neuron v0.204.1's wallet derivation uses the CKB Lumos account-key and address derivation APIs, and the Waymark fixture documents its Script at `m/44'/309'/0'/0/0`. The derivation scheme is compatible in principle. But the R3 artifact contains no Neuron wallet identity, and the public audit contains no mnemonic or account xpub from which a Neuron-owned wallet can be created. I did not read or use any wallet secret or assign an arbitrary wallet ID. No replacement Neuron-owned active TESTNET fixture was available.

Useful native integration checks did run: Neuron's exact grouped Light RPC request returned the artifact's eight transactions, and the released client confirmed what Neuron's fresh-progress initialization does to the imported cursor. Neuron's TypeScript `IndexerTxHashCache`, queue and `TransactionPersistor` did **not** run. No application recovery, exact wallet-state comparison, or recovery-performance result is claimed.

## Environment and safety

- Neuron source checkout: `neuron-wo05-src`, clean at `a926e3383d3a3e305b3bde7d233474515ef01a2e`.
- Installed app: `Neuron.exe` ProductVersion `0.204.1.0`; `resources/app.asar` is present. The app was not launched because no valid fixture-to-wallet identity was available and its ordinary profile contains existing user data.
- The Neuron source checkout has no `node_modules` or built `dist`. Its working tree is sparse; the pinned package manifests remain readable from Git objects. No dependencies were installed and no development build was run.
- Existing Rust target was reused only for reference; no Rust compile was needed. C: had 5,493,096,448 bytes free at start and 5,482,541,056 bytes at the end, above the 4 GB reserve. The R4 disposable native-store copy was about 1.86 MB.
- R3's store was copied into `%TEMP%\\wo07-r4-runtime`; the R3 store and R3 report were not changed. R4 used a separate network directory, localhost RPC `127.0.0.1:19058`, and localhost P2P port `19122`. The installed v0.5.4 executable was stopped after the probes.
- No Neuron database or wallet file contents were opened or changed. During initial inventory, I did enumerate directory names and aggregate file sizes under the existing `%APPDATA%\\Neuron` profile; no file contents, SQLite pages or keys were read. I stopped using that profile after the metadata-only inventory.
- The controlled `runs/lite-full-attribution/audit.json` was parsed locally to enumerate field names; no values from its fixture object were output. Its top-level fixture fields say that the BIP39 checksum and both public TESTNET Script identities were checked, but it contains no mnemonic or xpub field.

## Ownership assessment

The public Waymark evidence records the artifact lock Script as code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`, args `0xbc5882c4309431ee23ad7bbad4b5c3325539eebd`, from account 0 at `m/44'/309'/0'/0/0` ([Waymark evidence](evidence.md)).

At the pinned Neuron source revision, mnemonic import derives an account extended key using `AccountExtendedPublicKey.ckbAccountPath`; address generation then uses Lumos `publicKeyInfo(addressType, addressIndex)`. `AddressMeta.generateDefaultLockScript()` builds the default secp lock from the resulting Blake160. Neuron pins `@ckb-lumos/lumos` 0.23.0. These code paths use the same CKB account/address derivation family as the fixture. This establishes source-level compatibility, not that a particular seed/xpub derives the artifact Script.

The artifact itself has only packed Script identity, role, TESTNET genesis, chain anchor, indexes and transaction closure. It has no seed, xpub, Neuron wallet UUID or address metadata. A Neuron wallet UUID must come from Neuron's normal wallet creation/import. The test did not invent one. Exact runtime ownership and the correct Neuron `walletId` association therefore remain unproven.

## Fresh application progress behavior

Source tracing plus an isolated released-client RPC probe establish this behavior:

1. `LightSynchronizer.initSyncProgress()` reads Neuron's existing sync-progress args and Light Client scripts. With an empty fresh application DB, the imported Script has no matching app args, so it is not retained in `existSyncScripts`.
2. Neuron derives the wallet's normal default/ACP Scripts. The imported default Script is consequently included in `addScripts` at the wallet's selected start floor.
3. Neuron sends `set_scripts(addScripts, "partial")`. In released v0.5.4, `Partial` writes the supplied Script block number to `FILTER_SCRIPTS`, replacing that Script's previous cursor. It does not delete the historical Script-index or transaction rows.
4. `SyncProgressService.initSyncProgress(addScripts)` creates the missing app row with `lightStartBlockNumber`, `localSavedBlockNumber`, and `syncedBlockNumber` all at the selected floor.
5. Later `upsertTxHashes()` queries the exact Script over `[app.syncedBlockNumber, LightClientScript.blockNumber)` with `group_by_transaction: true`. It persists transaction hashes to Neuron's indexer cache before updating app Script progress.

The R4 RPC probe used the imported real R3 store copy. Before the simulated fresh-wallet registration, the Script cursor was `0x15db450`. A `set_scripts` partial request for the fixture floor `0x1555691` changed `get_scripts` to report exactly that lower cursor. The eight grouped historical transaction results remained queryable afterward. Thus native history was not deleted, but a normal empty-app initialization rewinds the filter cursor and causes historical filtering to be repeated. The imported data alone does not retain its filtering-time advantage for a fresh Neuron app DB.

If a valid app progress row for this exact Script already exists, startup can retain the Light Client Script and skip `set_scripts` for it. But `upsertTxHashes()` requires that app row to associate results with a real Neuron wallet ID. A safe integration needs Neuron itself to create the wallet/address identity and a matching progress row before the synchronization initializer runs; a guessed row is not acceptable.

## Grouped RPC and H boundary

Neuron's pinned `ckb-rpc` formatter sends `group_by_transaction: true`. The R4 query used that exact request shape, Script, ascending order, and range `[22,369,937, H+1)`. With limit 3 it returned three nonempty pages and a terminal empty page: **8 grouped transactions**, exactly matching the eight hashes in the D2 closure. The objects included block numbers and transaction indexes. The underlying 23 Script-index entries therefore represent eight transactions, not 23 transactions.

The real artifact has no matching transaction at H. A separately labeled synthetic fixture in a disposable store exercised the grouped v0.5.4 RPC at H−1, H and H+1:

| Range | Synthetic grouped results |
| --- | --- |
| `[H−1,H)` | Exactly the transaction at H−1 |
| `[H,H+1)` | Exactly the transaction at H |
| `[H+1,H+2)` | Exactly the transaction at H+1 |
| `[H,H)` | Empty |
| `[H−1,H+2)`, limit 1 | All three in height order, with pagination |

This confirms the RPC's half-open range behavior. Neuron supplies the native Script cursor as the exclusive upper endpoint. If that cursor equals artifact H, a request ending at H will not return an H transaction in that poll; a subsequent poll beginning at H can return it once the upper cursor advances beyond H. The exact completion behavior at a final target of H was not exercised in Neuron. Any app proof must test that case and must not mark usable recovery complete until H's results have entered the queue. One defensible bridge is to represent coverage through inclusive H with a native continuation cursor of H+1, then query through `[floor,H+1)`; this must be validated with Neuron progress and Light Client continuation before adoption.

## Application pipeline and correctness status

| Requirement | R4 result |
| --- | --- |
| Neuron-derived exact Script / generated wallet ID | Not run; no local disposable mnemonic/xpub was available |
| Neuron `SyncProgress` row and wallet association | Not run |
| Neuron startup initializer | Source-traced only |
| Actual v0.5.4 `set_scripts` partial behavior | Executed on disposable copy; cursor rewound, rows remained queryable |
| Neuron-shaped grouped RPC | Executed; 8/8 expected hashes, 3 result pages plus empty terminal page |
| `IndexerTxHashCache` writes | Not run |
| Queue transaction/header/previous-output fetch | Not run |
| `TransactionPersistor` execution | Not run |
| Exact app history/input-output/Cell/balance comparison | Not run |
| DAO state | Unproven; no Neuron app reconstruction |
| App restart with pending cache | Not run |
| Continued Neuron sync after H | Not run |
| App negative tests (wrong wallet, omitted cache row, interruption) | Not run |

Neuron's source ordering remains important: `upsertTxHashes()` writes cache rows before `updateSyncedBlockOfScripts()`. That is a discovery checkpoint, not proof that the normal transaction queue and persistor have finished. WO07-R4 did not start the application modules, so cache-drain and restart safety remain open.

## Resource and evidence details

No build or install was run. The exact installed Neuron binary and source were identified, but an isolated Electron user-data path was not validated; the existing profile was not used. No source files were modified. The only workspace deliverable is this report. Disposable R4 database/config/log files are under `%TEMP%\\wo07-r4-runtime`; they are not Neuron wallet data.

The grouped request and cursor test used the official v0.5.4 Windows binary from `%TEMP%\\wo07-r2-isolated\\ckb-light-client.exe`. R4's grouped query returned 8 hashes matching the D2 closure; the cursor test changed only the disposable R4 copy. The synthetic H-boundary test used `%TEMP%\\wo07-r3-synthetic-v2` and is not real TESTNET history.

## Next engineering action

Do not implement a production integration yet. Stage a **dedicated disposable TESTNET mnemonic or account xpub** for the account-0 Script in the R3 artifact, or prepare a new genuine Neuron-owned TESTNET Script with equivalent indexed activity. Keep the secret local; an xpub is sufficient only for watch-only ownership if Neuron's normal import path accepts it.

Then use the installed v0.204.1 app with a verified isolated user-data directory. Let Neuron create the wallet UUID and address metadata. With all workers stopped, import the R3 artifact into that app's own v0.5.4 store, set its imported Script cursor to H+1 only after destination authority and artifact validation, and ensure a real matching app progress row exists before startup so `initSyncProgress()` does not rewind it. Exercise Neuron's grouped `upsertTxHashes`, cache, queue and persistor at a common chain hash; verify complete history, input/output links, spent/live Cells and balances before and after cold restart. If Neuron cannot run with a safely isolated profile or cannot derive/register the exact Script, stop and use a newly generated Neuron-owned active TESTNET fixture rather than assigning the old Script to a synthetic wallet ID.

## Pinned source references

- Neuron source: `nervosnetwork/neuron` at `a926e3383d3a3e305b3bde7d233474515ef01a2e`; release runtime `v0.204.1`.
- Wallet mnemonic and account-key derivation: [wallets.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/controllers/wallets.ts#L93); address derivation: [addresses.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/services/addresses.ts#L227), [address meta](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/database/address/meta.ts#L99).
- Fresh sync registration: [light-synchronizer.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts#L192); [sync-progress.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/services/sync-progress.ts#L9).
- Query/cache/progress ordering: [light-synchronizer.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts#L127); grouped RPC formatter: [ckb-rpc.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/utils/ckb-rpc.ts#L72).
- Released client `set_scripts` partial cursor overwrite: [native storage v0.5.4](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/storage/db/native.rs#L141); half-open RPC filter: [get_transactions](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-bin/src/rpc.rs#L315).
- R3 source artifact and independent chain anchor: [WO07-R3](WO07_R3_NATIVE_ROCKSDB_ADAPTER.md); original derivation metadata: [Waymark evidence](evidence.md).
