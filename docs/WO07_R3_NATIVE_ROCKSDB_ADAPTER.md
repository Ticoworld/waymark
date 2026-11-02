# WO07-R3: Native RocksDB Adapter and Released RPC Replay

Date: 31 October 2026

## Verdict

**NATIVE RPC REPLAY PROVEN.** An isolated D2 adapter compiled against the released Light Client's native RocksDB dependency, imported the existing exact-Script TESTNET artifact into a byte-verified copy of the independently validated WO07-R2 store, and reopened successfully in the official Windows v0.5.4 binary. The normal `get_transactions` RPC returned all 23 indexed Script matches and the exact eight transaction hashes in the artifact closure. Reimport was idempotent. The data remained queryable after cold process restarts.

This is a one-Script native storage/RPC integration result. Neuron's TypeScript transaction queue and `TransactionPersistor`, complete wallet state, transaction completeness, and comparative recovery performance were not exercised. It is not a Neuron recovery or product-value PASS.

## Target and source identities

- D2 source: isolated clone `%TEMP%\\wo07-r3-d2`, commit `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`.
- Neuron target: v0.204.1, with the official CKB Light Client v0.5.4 Windows x64 release binary already verified in R2. Its pinned Light Client source is `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`; the RocksDB dependency is `ckb-rocksdb 0.21.1`.
- Existing D2 artifact: `%TEMP%\\wo07-exact-script.d2`, SHA-256 `8cd79c806033b46123f205751b83a2f66705dd6f31ce7488df5dd9828207308c`, 7,494 bytes. Its encoded source profile is `pocket-node@6eda0b7a4601050b011591d41cc702f0dc7a7c38/ckb-light-client@0.5.4/kv-v1`.
- Imported Script: exact packed lock Script from the controlled fixture, args `0xbc5882c4309431ee23ad7bbad4b5c3325539eebd`.
- Handoff: H=`22,737,263`, hash `0x5b6578a1acfc6f061d8df5584511ff982b12e8f034ef80bb4bbe7792735c4f31`.
- TESTNET genesis: `0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606`.

The adapter's explicit destination profile label is `neuron@v0.204.1/ckb-light-client@0.5.4/rocksdb-v1`. This is a local semantic profile name for the exact target, not a profile string supplied by upstream. The importer accepts only the one pinned Pocket v0.5.4-derived source profile; ordinary D2 adapters retain exact-profile equality by default.

## Resource and authority controls

Only C: is available as a local drive. The build and Cargo target were placed in WSL `/tmp/wo07-target`, which resides on the C:-backed WSL virtual disk; it was not a separate-capacity drive. Existing caches were reused. The only missing Rust package needed for the bounded build was `clang-sys 1.9.1`; the build then compiled the cached RocksDB 8.5.4 source used by `ckb-rocksdb 0.21.1`. No full CKB chain or large client source build was downloaded.

The original R2 destination had no running Light Client process before copying. Its 10 RocksDB files (1,790,125 bytes) were individually SHA-256 and length compared to a separate `%TEMP%\\wo07-r3-isolated\\data\\store` copy; all matched. The original R2 store was not opened for writing or changed. The disposable R3 configuration used a new network directory, localhost RPC `127.0.0.1:19055`, localhost P2P port `19119`, and the prior four-outbound-peer cap. The official client opened the adapter-written copy, not the D2/Pocket source store.

R2 had independently synchronized the destination, observed H absent from its cache, and fetched H plus its parent through the released v0.5.4 proof path against its proved tip. R3 reused only a byte-verified copy of that destination store. Before import, the adapter read the destination's own genesis and height-to-hash mapping at H and also confirmed the stored header hash/height. It accepted H only when these agreed with the artifact. It did not trust the artifact hash as authority. R2's evidence is in [WO07-R2](WO07_R2_RELEASED_CLIENT_EXECUTION.md).

## Adapter implementation

The adapter is confined to the isolated D2 clone; no D2, Neuron, Pocket, or upstream production checkout was modified. It maps D2's canonical semantic rows to v0.5.4 RocksDB keys and values, opens an already-existing store with `create_if_missing(false)`, obtains an exclusive side lock, and relies on RocksDB's native DB lock to reject a concurrent client. It checks the restored-wallet Script and role, exact source profile, genesis, destination-owned H, closure, row shapes and existing-row conflicts before writing.

One RocksDB `WriteBatch` atomically writes the Script-derived indexes, transaction closure, per-Script filter cursor at H, and recomputed global minimum cursor. It performs read-back checks. Existing identical rows are idempotent; conflicting rows fail closed. A stale/newer Script cursor is rejected. It does not copy Neuron application data or any key material.

Actual import result:

| Result | Value |
| --- | ---: |
| Cell/UTXO Script-index rows | 3 |
| Transaction Script-index rows | 23 |
| Referenced transaction rows | 8 |
| First import | `idempotent=false` |
| Immediate repeated import | `idempotent=true` |
| Post-import validation | passed; complete identical state present |
| Destination tip read during import | 22,917,969 |

The source artifact's own BLAKE2 digest reported by D2 was `c718762fdfcf6934ed071299a2a994e89782225caebef371d4f5cb31790d8886`; it is distinct from the whole-file SHA-256 above.

## Released RPC replay

The official v0.5.4 Windows executable opened the Linux-written RocksDB copy without a schema error. `get_scripts` exposed the imported exact Script as a lock Script with block number H. `get_transactions` was queried with that exact Script and range `[0,H+1)`. The first run paged with limit 5: five non-empty pages returned 23 entries, followed by the terminal empty page. Results were ascending by native index key. Their eight distinct transaction hashes exactly matched the eight D2 transaction-closure hashes: no missing or extra hash.

The genuine fixture has no matching transactions near H. Its last returned entry is at block `22,655,842`, 81,421 blocks before H (not 181,000; the measured difference is 81,421). Consequently the real artifact cannot prove inclusion at H−1/H/H+1. The real RPC windows `[H−1,H)`, `[H,H+1)`, and `[H+1,H+2)` each correctly returned empty; `[H,H)` returned empty as well.

To exercise half-open inclusion separately, a labeled **synthetic-only** second copy received three distinct valid packed transaction bodies and lock-index rows at H−1, H and H+1. The official v0.5.4 RPC returned exactly one expected hash from each respective one-block range. `[H,H)` returned none. A limit-1 query over `[H−1,H+2)` paginated the three rows in height order in three non-empty pages plus a terminal empty page. These synthetic rows are not TESTNET recovery evidence and were not added to the R3 real-artifact store.

No import-specific historical re-filter was required to answer the low-height RPC query: the imported Script cursor was H and its historical index rows were present before the binary opened. The client then advanced the Script cursor from H into later blocks (observed after restart as `0x15d8490`, height 22,906,000), i.e. continuation after the handoff. This shows the native query reused the preloaded historical index. It does not measure saved CPU, network traffic or elapsed recovery time, and it is not a matched baseline.

## Restart, tests, and negative cases

After import, the official process was force-terminated because v0.5.4 exposes no stop RPC in this setup, then relaunched against the same R3 copy. After restart, `get_header(H)` returned the expected height/hash, the imported Script was still registered, and the historical query again returned 23 index entries/eight distinct transactions. A further cold launch reproduced the exact eight-hash closure set. This is abrupt process restart/recovery, not graceful shutdown.

The full isolated crate test command passed **28 tests, 0 failed, 5 ignored**. Four new RocksDB adapter tests cover atomic write/reopen/reimport, cursor minimum with other Scripts, profile/Script/role/genesis/H rejection without mutation, row conflicts and precommit interruption without partial mutation. Existing artifact tests cover corrupt digest, malformed/oversized artifact and incomplete closure. These negative tests use temporary synthetic RocksDB fixtures, not the live TESTNET store. The real artifact exercised only the valid import path. A forced kill during the actual RocksDB batch was not performed.

Relevant command, from PowerShell at the repository root. The variables derive WSL paths from the current checkout and `%TEMP%`; the isolated D2 checkout remains under `%TEMP%\wo07-r3-d2`:

```powershell
$tempWsl = (wsl.exe wslpath -u $env:TEMP).Trim()
wsl.exe -e bash -lc "cd '$tempWsl/wo07-r3-d2' && CARGO_TARGET_DIR=/tmp/wo07-target CARGO_BUILD_JOBS=2 CARGO_PROFILE_DEV_DEBUG=0 CARGO_PROFILE_TEST_DEBUG=0 CXXFLAGS=-g0 cargo test -p d2-script-handoff --no-default-features --features v054-rocksdb --offline -- --test-threads=1"
```

Actual import runner:

```powershell
$tempWsl = (wsl.exe wslpath -u $env:TEMP).Trim()
wsl.exe -e bash -lc "cd '$tempWsl/wo07-r3-d2' && WO07_R3_ARTIFACT='$tempWsl/wo07-exact-script.d2' WO07_R3_STORE='$tempWsl/wo07-r3-isolated/data/store' CARGO_TARGET_DIR=/tmp/wo07-target CARGO_BUILD_JOBS=2 CARGO_PROFILE_DEV_DEBUG=0 CARGO_PROFILE_TEST_DEBUG=0 CXXFLAGS=-g0 cargo run -p d2-script-handoff --example r3_import --no-default-features --features v054-rocksdb --offline"
```

The synthetic fixture writer command used `--example r3_synthetic_boundary` with `WO07_R3_SYNTHETIC_STORE` set to `$tempWsl/wo07-r3-synthetic-v2/data/store`; the released binary then ran from the separate localhost config on port 19057.

## Performance and trust limits

Filtering before H was skipped for this one imported Script in the native store, but no Neuron application work was replayed and no baseline was timed. Cost of artifact export is from the prior evidence; R3 measured native validation/import, RPC replay, and binary startup only qualitatively. Application transaction/header/previous-output fetch, Neuron DB persistence, balances/Cells/DAO reconstruction, post-H catch-up time and total recovery savings remain unmeasured. Do not call this competitive.

D2 remains trusted-self state. Destination validation of H proves the accepted chain point under the v0.5.4 client; it does not prove the source included every historical matching transaction. The unkeyed artifact digest detects accidental corruption, not source identity or omission. The RPC comparison proves that the imported closure was returned, not that the closure was complete relative to the whole chain. Only one lock Script was tested; other Scripts, account discovery, type Scripts, DAO recovery, reorg effects on the transferred range, and application-level omissions remain unproven.

## Files and resource usage

Modified files in isolated `%TEMP%\\wo07-r3-d2`:

- `Cargo.lock`
- `crates/d2-script-handoff/Cargo.toml`
- `crates/d2-script-handoff/src/lib.rs`
- `crates/d2-script-handoff/src/operations.rs`
- `crates/d2-script-handoff/src/upstream.rs`
- `crates/d2-script-handoff/src/v054_rocksdb.rs` (new adapter)
- `crates/d2-script-handoff/examples/r3_import.rs` (real-artifact runner)
- `crates/d2-script-handoff/examples/r3_synthetic_boundary.rs` (separate boundary fixture)

The adapter/build target occupied about 4.1 GB in `/tmp/wo07-target`; Cargo registry source occupied about 1.8 GB. The imported R3 store measured 1,849,014 bytes at final capture. C: finished with 5,068,357,632 bytes free, above the 4 GB reserve. During one accidental helper rebuild that omitted the debug-size environment flags, free space briefly fell to about 4.6 GB; those exact Cargo processes were stopped. No unrelated project data was removed. No Neuron application data was accessed. No Neuron application replay was run.

## Next engineering task

Proceed only to an isolated **WO07-R4 Neuron application replay spike**. Use Neuron v0.204.1 and its bundled v0.5.4 client, keep app progress at/below H, query the imported historical Script through the ordinary client, durably enqueue every result, drain Neuron's existing queue/persistor, and only then advance app progress. At a common canonical TESTNET hash, compare complete history, input/output links, spent/live Cells and balances, then cold-restart. Include DAO only if the disposable fixture contains DAO activity. Keep other Scripts on normal Neuron discovery. This should be a correctness-first one-Script test; do not build product integration or claim speed until exact state passes. A later matched baseline must include export/import/verification costs before any performance claim.

## Pinned evidence

- CKB Light Client v0.5.4 release/source: [release](https://github.com/nervosnetwork/ckb-light-client/releases/tag/v0.5.4), [native RocksDB storage](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/storage/db/native.rs), [storage key schema](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/storage/mod.rs), [ordinary `get_transactions` RPC](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-bin/src/rpc.rs#L315).
- D2 v1 artifact/profile and existing Pocket adapter: [format and trust boundary](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/docs/D2_V1.md), [Pocket adapter](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/crates/d2-script-handoff/src/pocket.rs#L28).
- Neuron replay contract previously traced in [WO07](WO07_NEURON_D2_REPLAY_RESULT.md): query/cache/progress ordering in pinned `light-synchronizer.ts`, followed by the normal queue and `TransactionPersistor`.
