# WO07-R10: Cross-Device Handoff Proof

Date: 2 November 2026

## Decision

**NATIVE TRANSFER ONLY.** A quiescent copy of the v0.5.4 native RocksDB store preserved the genuine R8 Script registration, its advanced native cursor, the confirmed faucet transaction index, and transaction body/header lookup across a separately started client process and a cold restart. The destination used a newly created network directory and a different Light Client network key.

This was a **full native-store copy**, not a D2 selective export/import. The destination inherited chain state and historical authority from the copied store. Neuron's app database was not copied or replayed, and the test did not exercise Neuron initialization or its wallet checkpoint behavior. No independent chain authority, complete recovery, duplicate-replay safety, H/H+1 handoff safety, or performance advantage is claimed.

## Source and fixture

R7, R8 and R9 evidence remains unchanged. R9's stopped v0.5.4 source was `%TEMP%\\wo07-r9-owned-source`; it contains the genuinely Neuron-derived lock Script for wallet `1c2d9dbd-4894-4ac6-93bf-b5352acb3eb0` and the confirmed faucet transaction:

- Script hash: `0x28535e1e70eb2ae8c56a829e1f9d3777fdf6b310c9c1dff17e4ae01917e45e62`.
- Lock Script: code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`, args `0xa2ade6127fcbb7f1ccfe4a886f6b1e9c5c92d837`.
- Transaction: `0x42dc0f3efabc9134fc2244f5c01c3b52768ba8d23f29c78d839208afa844e435`.
- Transaction height: `22,944,379` (`0x15e1a7b`); block hash `0x4e5c9e8562027923c11a8608b10c399dccb59f145e047eb0f58a8a8b5b56f52c`.
- Neuron-owned output 0: 10,000 CKB, live in the independent TESTNET RPC check recorded in R9.
- Source client: official CKB Light Client v0.5.4, binary SHA-256 `fe38b58d85239149bd9aab81f9f90dff3ee8d7d01d09435be6621e6525f0cab8`; source commit `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`.

The R8 wallet is still receive-only. Its lost mnemonic/password were not recovered or used. No new faucet request, transaction, or synthetic history was created.

## Native store-copy experiment

The R9 Light Client was stopped before copying. `clone-quiescent-store.js` created `%TEMP%\\wo07-r10-native-copy2` from the source's `data/store` only. It copied 19 files totaling 2,190,898 bytes and compared SHA-256 for every file; all hashes matched. It created a fresh `data/network` directory instead of copying the source peer identity. A post-start check confirmed both network keys existed and were different; key contents were not printed.

The first isolated config attempt used `max_outbound_peers=0`, which v0.5.4 rejects with `max outbound peers shouldn't be zero`. That failed disposable directory was left intact. The working copy used no bootnodes and `max_outbound_peers=1`; its fresh peer store had no peers, so the client did not synchronize from the network during this check. It served localhost RPC `127.0.0.1:19097` and P2P `127.0.0.1:19160`.

On startup and again after cold restart, the normal RPCs reported:

| Check | Result |
| --- | --- |
| Client tip | Height `0x15e1b4b`, hash `0x4b0336e5baacb382a618b44cf1b2512edca47af85798f7c03753a2224f3a36be` |
| Exact R8 Script registration | Present as a `lock` Script |
| Preserved native Script cursor | `0x15e1b4a` (22,944,586), beyond transaction H |
| Query range | `[0x15e1a7a, 0x15e1b35)` |
| Grouped result | Exactly the faucet transaction at `0x15e1a7b`, index `0x1` |
| Ordinary `get_transaction` | `committed`; exact expected tx hash and expected block hash |
| Owned output | Exact Script args and capacity `0xe8d4a51000` |
| Result after restart | Same cursor and exact transaction/output result |

The native index was already present in the source and copied with the store. This demonstrates that a full-store copy can carry prior filtering results and cursor to another process installation. Historical filtering was not needed to answer the test query in the peer-disabled copy. No filtering CPU, network bytes, elapsed-time saving, or equivalent fresh-destination baseline was measured.

This does not establish independent chain authority: the destination's tip, block mappings, native index, and transaction data came from the source RocksDB copy. A new process and network identity do not make copied chain data independently validated. The test did not ask the destination to revalidate the copied transaction block through peers.

## D2 and RPC export assessment

The isolated D2 source remains pinned to `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`. Its `NeuronV054RocksDbAdapter` has explicit allowlisted Pocket-v0.5.4 profile acceptance and a destination import implementation, but its `export()` returns `UnsupportedProfile("v0.5.4 adapter is destination-import only")`. The D2 artifact model carries the exact Script/role, genesis, H/hash, cursor, Script-derived rows and transaction closure. It does not itself provide an exporter for the R8 source store.

The standard Light Client RPC is useful but not a demonstrated lossless native export. `get_transactions` exposes Script matches, range positions and transaction hashes; `get_transaction` exposes transaction bodies/status/header context. No RPC emits the D2 artifact or a complete export of the v0.5.4 Script-index rows, cursor/global-minimum metadata and all closure information in the adapter's expected row format. Reconstructing those rows from RPC responses would be a new exporter and must be proven against Neuron's actual RPC/storage semantics; it was not treated as an existing mechanism.

No safe local RocksDB build was started. At the final check, C: had `5,841,555,456` bytes free, approximately 5.44 GiB, only about 1.44 GiB above the required 4 GiB reserve. Prior R3 build evidence recorded about 4.1 GB of Cargo target output. No compatible build target was present in the isolated checkout, so a local adapter/exporter build would exceed the available margin. The smallest external build requirement is an isolated environment with the pinned D2 source, public dependency access or the existing Cargo cache, the v0.5.4 RocksDB adapter feature, and at least 5 GB free build space. No private wallet data or local evidence needs to be transferred; the test fixture would require only public Script/transaction identifiers plus a sanitized, disposable native-store copy if the exporter must be run against the same records.

## Neuron synchronization checkpoint distinction

R9 observed the real Neuron discovery checkpoint advance from `22,944,378` to `22,944,565` after the matching hash was inserted into `IndexerTxHashCache`. `localSavedBlockNumber` remained `22,944,378`, because the headless harness stubbed the main-process address-generation IPC that performs later local-save/address bookkeeping. The two values have different roles and were not manually set equal. R10 did not run `LightSynchronizer.initSyncProgress()` against the copied native store or change either Neuron field. It therefore does not establish whether Neuron startup preserves an imported cursor in a separate app database.

The completed application rows from R9 were not copied into a second Neuron database. No artificial clean-recovery claim was made using an already-complete app DB. No duplicate transaction replay, interrupted cache replay, or H/H+1 continuation test was run.

## Reproduction and resource use

The two new scripts are limited to disposable temp paths and refuse an existing destination:

- `tools/wo07-r10/clone-quiescent-store.js` copies a stopped R9 native store, verifies each copied file hash, creates a fresh network directory and writes a no-bootnodes config.
- `tools/wo07-r10/probe-native-copy.js` checks the exact Script, cursor, grouped transaction query, committed body and owned output through ordinary v0.5.4 RPC.

Reproduction, if the previous temp fixtures remain available:

```powershell
node tools/wo07-r10/clone-quiescent-store.js `
  "$env:TEMP\\wo07-r9-owned-source" "$env:TEMP\\wo07-r10-native-copy2"

& "$env:TEMP\\wo07-r9-v054-bin\\ckb-light-client.exe" run `
  --config-file "$env:TEMP\\wo07-r10-native-copy2\\config.toml"

node tools/wo07-r10/probe-native-copy.js http://127.0.0.1:19097
```

Stop the test client, restart with the same config, and rerun the probe. The source `%TEMP%\\wo07-r9-owned-source` and R7/R8/R9 evidence were not modified. The working native copy grew to 22 store files / 2,024,534 bytes after client startup and restart. C: remained above the 4 GiB reserve; final free space was `5,841,555,456` bytes. The test client was stopped.

## Next action

Implement the bounded v0.5.4 RocksDB **source exporter** in an isolated build environment with sufficient disk. Export only the R8 exact Script/role, matching index rows, transaction closure, cursor, genesis, and H/hash from a quiescent source. Import that artifact into a destination whose chain authority is independently established, then run Neuron initialization before and after the import barrier and prove that the imported cursor is not rewound. Neuron app progress must remain behind until the historical results are durably queued; `localSavedBlockNumber` must advance only through its normal application lifecycle. Compare exact history and live/spent state, cold restart, duplicate replay, and H/H+1 continuation before calling recovery proven. Use a real wallet spend fixture before making claims about spent-cell recovery.

## Pinned references

- Neuron v0.204.1 source `a926e3383d3a3e305b3bde7d233474515ef01a2e`: `light-synchronizer.ts`, `sync-progress.ts`, `queue.ts`, `transaction-persistor.ts`, and sync-progress/cache entities.
- CKB Light Client v0.5.4 source `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`; official binary used in R2/R3/R7/R9/R10.
- D2 source `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`; experimental `crates/d2-script-handoff/src/v054_rocksdb.rs` is import-only.
- Prior evidence: [R7](WO07_R7_VERIFIED_HEADER_AND_REAL_QUEUE.md), [R8](WO07_R8_OWNED_WALLET_SYNC.md), [R9](WO07_R9_REAL_NEURON_RECOVERY.md).
