# WO07-R8: Owned Neuron Wallet Sync

Date: 2 November 2026

## Verdict

**OWNED FIXTURE BLOCKED.** A genuine disposable Neuron v0.204.1 TESTNET wallet was created headlessly through Neuron's packaged mnemonic-import controller and wallet/address services. Neuron assigned the UUID, derived the account-0 Script, wrote its wallet/address records and Light-mode SQLite data under a fresh `%TEMP%` profile, and a separate Node process reopened and verified them.

The R8 replay did not proceed. The official Pudge faucet accepted a 10,000 CKB claim for the disposable address, but still reports it as pending with no transaction hash. There is therefore no confirmed owned transaction to export or replay. No activity was fabricated, no D2 source exporter was added, and no R8 `IndexerTxHashCache`, queue, or persistor result is claimed. R7 remains the fallback pipeline proof.

## Versions and isolation

- Neuron packaged backend: v0.204.1, extracted from the existing R6 ASAR at `%TEMP%\wo07-r6-neuron-asar`; Neuron source reference `a926e3383d3a3e305b3bde7d233474515ef01a2e`.
- CKB Light Client target: v0.5.4; no Light Client process was started for R8.
- Runtime: Windows, Node.js v22.14.0, packaged Neuron dependencies and SQLite addon.
- Isolated profile: `%TEMP%\wo07-r8-neuron-profile-real-testnet`. `app.getPath('userData')` was stubbed to this new directory before loading Neuron modules. The existing Neuron profile was not opened. No Electron window or full-node service was launched.
- Network selection was made through Neuron's real `NetworksService.activate('light_client_testnet')` and verified on reopen against TESTNET genesis `0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606`.
- Only the Electron boundary and Neuron's background block-sync task launcher were stubbed. The packaged wallet controller, wallet service, address derivation/service, TypeORM schema/migrations, SyncProgress service and `LightSynchronizer.initSyncProgress()` were used.

The test runner refuses an existing profile directory. A separate early diagnostic profile initially selected the default mainnet network; its `ckb`-prefixed address was not used for the faucet request. The final test explicitly activated TESTNET and rejects any account-0 address that does not start with `ckt`.

## Genuine wallet identity

The runner generated a fresh BIP39 phrase in process memory and passed it directly to Neuron's actual `WalletsController.importMnemonic()`. The phrase and password were not printed or included in this report. Neuron's wallet service generated the UUID and encrypted keystore; its address queue derived the normal account/address metadata.

| Field | Neuron-created value |
| --- | --- |
| Wallet UUID | `1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0` |
| Network | `light_client_testnet`, TESTNET genesis above |
| Account-0 derivation | `m/44'/309'/0'/0/0` |
| Address | `ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdz4hnpyl7tklcuelj23phkk85utjfdsdclqrnw2` |
| Lock Script | code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`, args `0xa2ade6127fcbb7f1ccfe4a886f6b1e9c5c92d837` |
| Script hash | `0x28535e1e70eb2ae8c56a829e1f9d3777fdf6b310c9c1dff17e4ae01917e45e62` |
| Generated address metadata | 30 rows (20 receiving and 10 change) |

These identifiers came from Neuron's persisted wallet and `hd_public_key_info` rows, not from an assigned UUID or manual wallet record. No mnemonic, private key, password, or extended public key is disclosed.

## Progress initialization and restart

After database initialization and actual wallet/address creation, the harness invoked the packaged `LightSynchronizer.prototype.initSyncProgress()` with Neuron-derived address metadata. Its Light RPC boundary returned no existing Scripts and captured the `set_scripts` calls; Neuron's real `SyncProgressService` wrote the rows to the disposable Light-mode SQLite database.

| Check | Result |
| --- | --- |
| Neuron-created wallet UUID on all owned progress rows | Pass |
| Per-wallet sync-progress rows | 90: default, ACP, and legacy ACP Scripts for 30 addresses |
| Account-0 default Script row | Present; role `lock`; start/local/synced heights all 0 |
| `set_scripts` registration requested by actual initializer | 90 Scripts in `partial` mode; 0 deletion requests |
| Real Light RPC registration or imported native cursor | Not run |
| `LightSynchronizer.upsertTxHashes()` and actual indexer cache | Not run |
| Queue / `TransactionPersistor` | Not repeated; R7 remains the existing proof |

The creation runner exited. A separate Node process reopened the same profile through Neuron's real network, wallet and address services, reopened the TESTNET Light SQLite DB, and verified the same UUID, Script, 30 address records, 90 progress rows and encrypted keystore file. No transaction or cache state existed to compare.

The initializer test does not establish imported-cursor preservation: its RPC fixture had no registered native Scripts. The R4 finding still applies. With no existing matching app progress, Neuron can request `set_scripts(..., 'partial')` from the wallet start floor; do not import an advanced D2 cursor until a real lifecycle test proves it survives startup.

## TESTNET activity attempt

The official [Nervos Pudge Faucet](https://faucet.nervos.org/) API accepted one claim for 10,000 TESTNET CKB at `https://faucet-api.nervos.org/claim_events`. The request used only the generated public `ckt` address. Faucet claim ID `706994` was returned with `status: pending`, `txHash: null`, and `txStatus: pending`. A subsequent address-scoped status read still showed the claim pending; no canonical transaction hash or block was available.

No transfer was signed or broadcast by this test, no transaction hash was fabricated, and no real received/spent Cell is established. Because the R7 Pocket Script is not owned by this wallet, it was not reused. The R3 adapter is destination-import only; a new owned-history artifact would require an exporter for this Neuron wallet's native source store. That work was not started before a confirmed activity fixture existed.

## Replay and correctness status

| Requirement | R8 result |
| --- | --- |
| Genuine Neuron-owned TESTNET Script | Proven; exact Script above |
| Confirmed incoming or spending transaction | Blocked; faucet has no tx hash yet |
| Owned Script native source index / D2 artifact | Not produced |
| Actual imported cursor before/after Neuron startup | Not tested |
| Historical refilter avoided | Not measured or proven |
| `upsertTxHashes()` / walletId-bound cache rows | Not run |
| Queue / persistor for this owned Script | Not run |
| History, inputs/outputs, spent/live Cells, balance | Not applicable without a confirmed transaction |
| Interrupted cache replay and restart | Not run |
| H/H+1 continuation | Not run |
| DAO | Unproven |

No recovery correctness, completeness, or acceleration claim follows from wallet creation or progress-row creation. R7's eight-transaction Pocket fixture remains pipeline-only evidence and is not associated with this wallet.

## Resource use and files

C: had `6,055,809,024` bytes free at the first R8 check and `6,049,656,832` bytes at final inspection. The observed net decrease was about 5.9 MiB (not all attributable to this run); the 4 GiB reserve remained intact. The final disposable profile measured `505,484` bytes across 10 files. No build, dependency install, chain sync, full-chain download, or R7 store modification occurred.

New workspace files:

- `tools/wo07-r8/create-owned-wallet.js`
- `tools/wo07-r8/verify-owned-wallet.js`
- `docs/WO07_R8_OWNED_WALLET_SYNC.md`

Earlier failed diagnostic profiles remain separate under `%TEMP%`; they were not used to submit the claim. R7 reports, scripts, artifact, Pocket source and imported store were not modified.

## Exact next action

Poll faucet claim `706994` for a confirmed `txHash`. If it confirms, use a disposable copy of the existing validated TESTNET Light Client store, register only this exact owned Script at the current destination tip, and observe the confirmed receive through v0.5.4. Then add a bounded v0.5.4 RocksDB source exporter for that Script, create a D2 handoff artifact, and import it into a separate independent destination copy. Run the real Neuron `upsertTxHashes()` against that destination with the existing wallet UUID, verify cache insertion precedes app progress, drain the existing queue, and compare exact transaction/Cell state after restart. If faucet claim does not confirm, obtain a usable TESTNET funding source before attempting that owned-history replay; do not substitute synthetic transactions or the old Pocket Script.

## Reproduction

Wallet creation and actual Neuron progress initialization:

```powershell
node tools/wo07-r8/create-owned-wallet.js `
  "$env:TEMP\wo07-r6-neuron-asar" `
  "$env:TEMP\wo07-r8-neuron-profile-real-testnet"
```

Fresh-process profile/database reopen check:

```powershell
node tools/wo07-r8/verify-owned-wallet.js `
  "$env:TEMP\wo07-r6-neuron-asar" `
  "$env:TEMP\wo07-r8-neuron-profile-real-testnet" `
  1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0
```

Both scripts reject unsafe profile paths; creation additionally refuses to overwrite an existing destination. They never print or accept the generated mnemonic/password as command-line arguments.

## Pinned implementation references

- Neuron source pin `a926e3383d3a3e305b3bde7d233474515ef01a2e`: `packages/neuron-wallet/src/controllers/wallets.ts` (`importMnemonic`), `services/wallets.ts` (UUID allocation and keystore), `services/addresses.ts` (derived address persistence), `services/sync-progress.ts`, and `block-sync-renderer/sync/light-synchronizer.ts` (`initSyncProgress`, `upsertTxHashes`).
- Packaged runtime used for execution: Neuron v0.204.1 extracted from the previously inspected release ASAR; no source build or source modifications.
- Prior native and queue evidence: [WO07-R7](WO07_R7_VERIFIED_HEADER_AND_REAL_QUEUE.md).
