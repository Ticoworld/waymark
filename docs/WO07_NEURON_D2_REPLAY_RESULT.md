# WO07: Neuron D2 Replay Engineering Spike

Date: 30 October 2026

## Final verdict

**ADAPTER BLOCKED.** The storage-row mapping from D2's Pocket v0.5.4 profile to Neuron's upstream v0.5.4 RocksDB store is bounded and appears technically feasible. The available recovery fixture cannot pass the released client's destination-owned historical handoff-hash check: its H is no longer retained by an independent destination, and the v0.5.4 client has no historical-header proof lookup. D2's existing profile check also rejects a Pocket-profile artifact when the destination adapter identifies itself as a different Neuron/RocksDB profile.

This is not a failed wallet-state comparison. The Neuron import, RPC replay, Neuron queue, cold restart, continuation, adversarial matrix and timing comparison were **not run**. The experiment stopped before native import at the chain-authority gate. Do not call this functional or infer a performance benefit.

## A. Storage compatibility

Neuron v0.204.1 selects CKB Light Client v0.5.4. On Windows its runner resolves `ckb-light-client.exe`, writes a TOML config whose store path is a directory, and launches the native client. The official v0.5.4 source selects `ckb-rocksdb = 0.21.1` for native, non-WASM builds. Therefore Neuron's Windows native store is RocksDB, not Pocket's SQLite `kv` database.

The v0.5.4 source is pinned to tag commit `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`. D2's upstream adapter is pinned to `12e29522ab7e078ada704d4ac04cbc0498009b7b`, whose client crate compiled as v0.5.5 in the isolated exporter build. That later commit introduced the `StorageBackend` and `LightClientStorage` abstractions used by D2. The v0.5.4 `Storage` API is concrete and its native module directly wraps RocksDB; those traits are absent. Release notes for v0.5.5-rc1 explicitly identify the unified storage refactor and SQLite support.

The relevant data schema is compatible at the row level. Both v0.5.4 native code and the Pocket v0.5.4-derived source use these key families: `0x00` transaction body, `0x20` Cell-by-lock-Script, `0x40` Cell-by-type-Script, `0x60` transaction-by-lock-Script, `0x80` transaction-by-type-Script, `0xa0` block hash, `0xc0` block number, `0xd0` filter checkpoint and `0xe0` metadata. Script key material is the packed Script's raw `code_hash || hash_type || args`; the role byte is in the registration metadata key. Heights and indexes in Script-derived index keys are big-endian. A transaction value is an 8-byte block number, 4-byte transaction index, then packed transaction bytes. D2's Pocket adapter uses the same prefixes and transaction closure shape.

### Profile differences

| Property | D2 upstream profile | Neuron v0.204.1 Windows | Pocket source fixture |
| --- | --- | --- | --- |
| Pinned client | `12e2952...` / crate v0.5.5 | tag `778590a...` / v0.5.4 | Pocket-pinned v0.5.4-derived client |
| Native backend | RocksDB | RocksDB (`ckb-rocksdb` 0.21.1) | SQLite table `kv(key BLOB, value BLOB)` |
| Storage API | `StorageBackend` + `LightClientStorage` | Concrete native `Storage` methods | Concrete Pocket SQLite adapter |
| D2 artifact profile | `ckb-light-client@12e295.../storage-v1` | No v0.5.4 Neuron profile in D2 | `pocket-node@6eda0b7.../ckb-light-client@0.5.4/kv-v1` |
| Direct D2 acceptance | Supported for matching profile | No adapter/profile | Supported for Pocket profile |

The row schema allows a small explicit Neuron-v0.5.4 RocksDB adapter using the existing D2 artifact fields and RocksDB atomic batches. D2's `PocketSqliteAdapter` offers reusable prefix scans, closure validation, genesis/H checks, minimum-cursor recomputation and transactional import patterns. It is not itself a Neuron adapter. No adapter was written in this spike: profile mapping and destination authority were not yet both satisfiable with the available fixtures, and writing an importer before that would create code without an executable acceptance path.

## B. Adapter result

**No Neuron adapter was implemented.** The isolated run built the pinned D2 checkout and exercised its existing Pocket SQLite adapter against the prior real Pocket TESTNET capture. It exported one account-0 lock Script. The source remains unchanged; the test wrote only a disposable destination copy and artifact under the system temp directory.

The D2 artifact representation can carry the v0.5.4 Script index rows and referenced transaction closure without a format change. However, D2 v1 binds one `adapter_profile` into the artifact and `D2::validate_model()` requires exact equality with the destination adapter's profile. A future adapter must add an explicit, narrowly scoped compatibility mapping or define a new shared semantic profile. It must not relabel artifacts, accept arbitrary profiles, or remove the existing equality check globally. A Neuron-origin export should use a Neuron/v0.5.4 profile; a Pocket-origin artifact should only be accepted by a Neuron importer through an explicit, tested Pocket-v0.5.4-to-Neuron-v0.5.4 mapping.

## C. Historical RPC result

**Not experimentally verified.** The official v0.5.4 `get_transactions` RPC implementation iterates the `TxLockScript` or `TxTypeScript` key prefix, looks up the referenced `TxHash` transaction row, and applies the requested block range `[from, to)` in its query loop. Thus the source implementation is compatible with the D2 row model in principle. It has not been shown that a Neuron-bundled v0.5.4 process, after an imported artifact, returns the expected hashes through its ordinary RPC without historical filtering.

Neuron's `LightSynchronizer.upsertTxHashes()` requests transactions from its app `SyncProgress.syncedBlockNumber` through the Light Client script cursor, inserts results into `IndexerTxHashCache`, and only then writes the app Script progress. This is the correct direction for replay. The later queue still fetches transaction/header/previous-output data and persists Neuron's own transaction/input/output records. Neither that path nor its restart behavior was exercised with imported rows.

## D. Application replay result

**Not run.** No Neuron `IndexerTxHashCache` rows were inserted, no Neuron queue was started, and no `TransactionPersistor.saveFetchTx()` calls were observed. There are no WO07 results for input/output relations, spent/live Cells, balance, DAO state, app progress, cache drain, or account ownership. The required invariant remains: Neuron's app checkpoint cannot advance through H until all imported historical query results are durable in its normal queue and processed.

## E. Correctness and adversarial results

The D2 production Pocket adapter test passed its existing structural export/inspect/validate/import/reopen test against the selected source Script. This is a Pocket-profile result and not a Neuron/RocksDB result. The artifact contained non-empty rows and a closed set of referenced transactions.

| Check | WO07 result |
| --- | --- |
| D2 Pocket source export and artifact validation | PASS, existing adapter/test path |
| Neuron v0.5.4 RocksDB import | NOT RUN |
| Expected historical RPC hashes | NOT RUN |
| Wrong genesis, Script, role, tamper, unsupported profile | NOT RUN for Neuron adapter |
| Stale destination H hash | BLOCKED before import; destination fixture had no H mapping |
| Incomplete closure | NOT RUN for Neuron adapter |
| Deliberately omitted matching transaction | NOT RUN; D2 trust limitation remains |
| Interrupted import/replay and restart | NOT RUN |
| Reorg | NOT RUN |

D2's documented trust limit remains: a valid digest, matching genesis and matching H do not prove that the source omitted no historical Script match. A source-authenticated omission remains undetectable by D2 v1 alone. Any later acceptance must keep the trusted-self source assumption explicit and use an independent test oracle to detect deliberate omissions.

## F. Destination authority, restart and continuation

The D2 artifact exported from the source had **H = 22,737,263**, hash `0x5b6578a1acfc6f061d8df5584511ff982b12e8f034ef80bb4bbe7792735c4f31`.

The source store had H in its `LAST_N_HEADERS` ring because H was only 9 blocks behind its then tip. The available separate captures did not provide a qualifying independent destination anchor:

- Arm B's independently captured tip was 22,737,156, below H.
- Arm D's later tip was 22,737,590, 327 blocks above H, but D is the native-reuse diagnostic arm and therefore is not independent chain authority. Its recent-header ring contains 100 entries and its `BlockNumber(H)` key was absent from the captured SQLite `kv` data.

The v0.5.4 storage records `LAST_N_HEADERS` as a bounded list of recent `(height, hash)` values. `BlockNumber` mappings are not a general historical height-to-hash archive. The available independent destination capture is below H; the later capture is not independent and lacks H locally. Reusing the source H/hash would violate destination-owned authority. A remote full-node `get_header_by_number` response without a proof-backed validation path would not satisfy that requirement.

The open CKB Light Client PR #297 proposes a proof-backed historical header verification API using the client's proof/PoW/MMR validation path. A released v0.5.4 Neuron binary has no such API. That work would strengthen H validation only; it would not prove Script-result completeness. No Neuron destination import, restart or post-H continuation was attempted after the authority gate failed.

## G. Performance result

**UNPROVEN.** No Neuron baseline or candidate runtime was run. No Light Client filtering work, imported-result RPC time, app replay, export/import, validation, catch-up or end-to-end time was measured. Pocket measurements and Waymark Pocket timings are not Neuron results and are not reused here.

If the capability is resumed, count source export and destination import/validation, Light Client startup and chain readiness, historical Script filtering, RPC replay, transaction/header/previous-output fetches, Neuron app persistence, catch-up and exact-state validation separately. Do not count Neuron application replay as saved work; it is required in both arms.

## H. Trust limitations

- D2 v1 trusts the source to report a complete exact-Script view and cursor.
- Its BLAKE2b digest detects accidental corruption but does not authenticate the sender.
- Destination H validation proves chain-point agreement only, not absence of omitted Script matches.
- The artifact contains public but privacy-sensitive Script and transaction information; it contains no wallet signing secret.
- A D2 native import does not restore Neuron's app database, discovery candidates, wallet labels, multisig state or DAO/UI cache.
- Correct Neuron recovery still requires its normal queue to reconstruct app records before app progress advances.

## I. Reproducible evidence and next action

### Executed command

The exporter test ran in WSL using the pinned D2 checkout at `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`, offline Cargo dependencies, and the existing controlled C-arm native store. D2 opened the source SQLite connection and performed reads only; the test copied it to `/tmp/wo07-dest.sqlite`, removed the selected Script rows from that disposable copy, then used D2's existing Pocket adapter to export and import. The retained source SHA-256 matches its prior evidence manifest. The command was equivalent to the following PowerShell invocation from the Waymark workspace root; it derives workspace and temp paths for WSL, and expects the pinned isolated D2 checkout under `%TEMP%\wo07-d2-exp`:

```powershell
$repoWsl = (wsl.exe wslpath -u (Get-Location).Path).Trim()
$tempWsl = (wsl.exe wslpath -u $env:TEMP).Trim()
wsl.exe -e bash -lc "cd '$tempWsl/wo07-d2-exp' && CARGO_TARGET_DIR=/tmp/wo07-target D2_POCKET_SOURCE='$repoWsl/runs/lite-full-attribution/measurement/C/equivalent/native.sqlite' D2_POCKET_DEST=/tmp/wo07-dest.sqlite D2_POCKET_SCRIPT=490000001000000030000000310000009BD7E06F3ECF4BE0F2FCD2188B23F1B9FCC88E5D4B65A8637B17723BBDA3CCE80114000000BC5882C4309431EE23AD7BBAD4B5C3325539EEBD D2_POCKET_ARTIFACT='$tempWsl/wo07-exact-script.d2' cargo test --manifest-path crates/d2-script-handoff/Cargo.toml --no-default-features --features sqlite,pocket-sqlite --offline production_pocket_export_validate_import --lib -- --ignored --nocapture --test-threads=1"
```

Observed result: pass; source tip 22,737,272; artifact profile `pocket-node@6eda0b7a4601050b011591d41cc702f0dc7a7c38/ckb-light-client@0.5.4/kv-v1`; H=22,737,263; 3 Cell-index rows, 23 transaction-index rows, 8 closure transaction rows; 7,494 bytes. The artifact SHA-256 is `8cd79c806033b46123f205751b83a2f66705dd6f31ce7488df5dd9828207308c`. The source `native.sqlite` SHA-256 matches the retained measurement manifest: `60005bde373b96dec1c1a383b9bf98191e50079d9a2ac829b8baae40afcaf682`.

This is executable D2/Pocket export/import evidence only. No D2 code, Neuron code, Pocket source, D2 evidence, or prior Waymark evidence was modified. Rust build output and the generated artifact remain under temp; the only new workspace file for WO07 is this report.

### Exact next action

Do not implement the Neuron replay bridge yet. First establish a released-client-compatible way for the destination Light Client to validate an old H hash independently. The smallest candidate is a narrowly scoped v0.5.4 backport or supported API for proof-backed historical header lookup (the role proposed by CKB Light Client PR #297), followed by a test against a destination that has not inherited source chain state. Keep the D2 source-profile compatibility mapping explicit and fail closed.

Once that gate exists, implement only the isolated v0.5.4 RocksDB adapter and run the one-Script RPC/replay test. Continue to the Neuron queue and exact history/Cell/balance/DAO/restart comparison only if RPC returns the artifact's expected transactions without re-filtering. Measure against the supported-start-height baseline before authorizing any production design.

## Pinned references

- Neuron v0.204.1 release: `d3a7467d218e4b6f777326682a83fec802669c00`; bundled CKB Light Client v0.5.4, from release notes.
- Neuron development sync path: [light-synchronizer.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts#L91), [sync progress entity](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/database/chain/entities/sync-progress.ts#L10), [queue.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/queue.ts#L124), [transaction-persistor.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/services/tx/transaction-persistor.ts#L198).
- CKB Light Client v0.5.4 exact source: [`storage/mod.rs`](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/storage/mod.rs#L295), [`storage/db/native.rs`](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/storage/db/native.rs#L53), [`get_transactions` RPC](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-bin/src/rpc.rs#L315), native RocksDB dependency in [`light-client-lib/Cargo.toml`](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/Cargo.toml).
- D2 pinned profile and v1 trust contract: [D2 v1 guide](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/docs/D2_V1.md), [profile enforcement](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/crates/d2-script-handoff/src/operations.rs#L175), [Pocket profile adapter](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/crates/d2-script-handoff/src/pocket.rs#L28).
- v0.5.5-rc1 storage abstraction change: [official CKB Light Client releases](https://github.com/nervosnetwork/ckb-light-client/releases).
- Proposed historical header proof support: [CKB Light Client PR #297](https://github.com/nervosnetwork/ckb-light-client/pull/297). It was open at research time and is not part of the released v0.5.4 Neuron client.
