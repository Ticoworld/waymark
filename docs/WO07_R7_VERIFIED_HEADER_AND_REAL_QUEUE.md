# WO07-R7: Verified Header Recovery and Real Neuron Queue

Date: 2 November 2026

## Verdict

**REAL NEURON PIPELINE PROVEN.** The released CKB Light Client v0.5.4 `fetch_header` path populated the missing historical header mappings for all eight D2 transaction blocks on a disposable copy of the independently validated R3 destination. After each proof-backed header fetch, ordinary `get_transaction` returned the matching committed body and block hash. All eight transactions and headers remained available after a cold client restart.

Neuron v0.204.1's packaged Queue and `TransactionPersistor.saveFetchTx()` then processed the eight genuine TESTNET transactions into a fresh Neuron SQLite database. It fetched two required previous transactions through the ordinary Light RPC, resolved input details, wrote 8 transaction / 12 input / 16 output rows, and the app DB matched exactly after close/reopen. This is pipeline evidence only. The fixture has no Neuron wallet identity, so no `IndexerTxHashCache` rows were created, no wallet ownership was asserted, and this does not prove complete wallet recovery or speedup.

## Pins and fixture identity

- Neuron release: `v0.204.1`; source reference `a926e3383d3a3e305b3bde7d233474515ef01a2e`.
- Light Client: official Windows x64 `v0.5.4`, source `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`; executable reused from the SHA-verified R2 archive.
- D2 adapter: isolated source `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`; unchanged.
- D2 artifact: `%TEMP%\wo07-exact-script.d2`, 7,494 bytes, SHA-256 `8cd79c806033b46123f205751b83a2f66705dd6f31ce7488df5dd9828207308c`.
- Read-only Pocket source DB: `runs/lite-full-attribution/measurement/C/equivalent/native.sqlite`, final SHA-256 `60005bde373b96dec1c1a383b9bf98191e50079d9a2ac829b8baae40afcaf682`, matching the retained R3 evidence hash.
- Imported Script: lock Script, code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`, args `0xbc5882c4309431ee23ad7bbad4b5c3325539eebd`.
- Handoff: `H=22,737,263`, `0x5b6578a1acfc6f061d8df5584511ff982b12e8f034ef80bb4bbe7792735c4f31`.
- TESTNET genesis: `0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606`.

The actual R7 target was `%TEMP%\wo07-r7-imported-store`, with new `data/network` identity, RPC `127.0.0.1:19076`, P2P `127.0.0.1:19140`, and four outbound peers configured. Its 15 source RocksDB files (1,863,675 bytes) were copied individually from the R3 store and each SHA-256 matched before startup. R3 is the copy of the independently proven R2 destination; no Pocket chain state was used as destination authority. The R7 client reported v0.5.4 and node ID `QmaxVe6HjU1A6TzCeJoS4NLuJxWBUUTmF81iqLaDJmaAob`.

The destination already inherited R2's independently accepted TESTNET chain context through that byte-verified R3 copy. R7 additionally started with peers enabled. The candidate source hashes were used only as `fetch_header` lookup identifiers. The v0.5.4 proof path is documented and pinned in [WO07-R2](WO07_R2_RELEASED_CLIENT_EXECUTION.md): the request is anchored to the destination's proved tip and a header is persisted only after proof processing.

## Source header records

The source SQLite `kv` table has a `BlockNumber(height)` row for each of the eight indexed transaction blocks and a corresponding `BlockHash(hash)` row containing 244 bytes. Eight unique blocks cover the eight distinct D2 transactions. The source DB was opened read-only by [inspect-source-headers.js](../tools/wo07-r7/inspect-source-headers.js).

| Height | Source mapping hash | Indexed transaction |
| ---: | --- | --- |
| 22,369,938 | `0xdd0ab2b8a07c641665e0f152af42c1f613352bfe4d8876a586bd18fcda6ddce7` | `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66` |
| 22,369,943 | `0xf50999ff89d6245de66e1438383c0e8581005a7b179e1e66c29a7114daa8a1d2` | `0xb7503283af42a8fd1595306e2d5dd4a789e103980207fdafb5229b2e20b7113c` |
| 22,370,275 | `0x11c9d1b8811f9d9f61364f13e031728193800659bdb70426179228c925bd216c` | `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894` |
| 22,646,305 | `0x45616351d7448a21ba0dad75383119f293f089d8bd5d95320293a7cd49082226` | `0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7` |
| 22,647,401 | `0x4a91e9a444df60e8db01f91cf2323bc3fe42bf770e4ce82bcd3b0095569e990c` | `0xb23fbbb1db9ca0da48f76993e9258fdadb0f3bc81d9999924561e72583aa5d5a` |
| 22,652,580 | `0x413f758d5930756b01db459c3cdfa60e6a486414b4d296c2d52de521135e543a` | `0xce0b13ba3f23babc6e4cc011a992b1f7bf610dd92b4f6719afde1c91a5e2ab39` |
| 22,655,641 | `0x53f75d7236a6ed26cdf736a2ba9bef92581cbcd2022f71c890de99921f01e2bf` | `0x2067edf16ab143e7bff9ef91803e36ce6a32347c632c75a37d382443ae379738` |
| 22,655,842 | `0xac49d2fc4965187bdaa925f94fa373d2f0b6b9d92acced66b3d6b1d5c04b3f13` | `0xe4cbdffa9002b0283c2c71cc19ec646b85cb58274b8f45d72496e78ae96b4cbd` |

This confirms the source mapping/header rows exist. Their packed 244-byte values were not independently decoded and rehashed here: the readily available Lumos v0.23 codec uses a different 208-byte header representation. The source rows therefore remain lookup hints. Authority for each result below comes from the released destination client's proof-validated `fetch_header` response, not from trusting those source bytes.

## Header fetch and native RPC

Before fetching, `get_header(firstHash)` returned `null`. A premature `get_transaction(firstTx)` reproduced the R6 failure: the RPC connection closed and the worker panicked at v0.5.4 `native.rs:1083`, where transaction retrieval needs the block-number-to-hash mapping. The client process remained available for the header request.

For each absent transaction-block header, R7 called `fetch_header(sourceMappedHash)`. The RPC returned `status: added`; polling `get_header(hash)` returned the header with the source-mapped hash and expected height. Then `get_transaction(txHash)` returned status `committed`, the exact transaction hash/body, and a `tx_status.block_hash` equal to the independently returned header hash. This empirically establishes that the normal proof-validated header-fetch path wrote the mappings needed by transaction retrieval. No manual global RocksDB rows or D2 format extension were used.

| Result | Count |
| --- | ---: |
| Distinct historical headers absent before fetch | 8 |
| `fetch_header` added and retrieved | 8/8 |
| Header hash and mapped height matched | 8/8 |
| `get_transaction` returned exact committed body | 8/8 |
| `get_transaction` and `get_header` passed after cold client restart | 8/8 |
| Grouped historical `get_transactions` after restart | 8 groups, same exact hashes |

The verified eight hashes and transaction heights are in the table above. After peer-enabled startup, the Script's native cursor was above H (`0x15e18f7`, then `0x15e1907` after restart), while the historical query still returned the preloaded index rows. The client did not need to re-run filtering over the imported pre-H Script range to answer that query. It did attempt ordinary post-H filtering; logs included peer block-filter checkpoint mismatch/unknown-start warnings. Complete post-H catch-up is therefore not claimed. No CPU, network-byte, or elapsed filtering savings were measured.

## Neuron Queue and persistence

The new [real-queue.js](../tools/wo07-r7/real-queue.js) uses the packaged v0.204.1 `Queue`, `RpcService`, `TransactionPersistor.saveFetchTx()`, TypeORM entities/migrations and SQLite addon. Only Electron boundaries and the LightSynchronizer event source were stubbed. The event source supplied the eight actual imported Script-index results; Neuron's transaction and header requests went to the real local v0.5.4 RPC. The Neuron DB was newly created at `%TEMP%\wo07-r6-queue-db10`.

Neuron requested the eight real transaction bodies and headers. Its ordinary queue also requested two external previous transactions referenced by the first two history transactions. Those dependencies initially reported `added`/`fetching`; the queue's existing retry loop waited until both became committed and their bodies were available. No custom transaction-processing or history-writing code was used. All eight calls reached `saveFetchTx`; Neuron's computed raw transaction hashes matched the requested hashes.

| Disposable Neuron Light DB result | Value |
| --- | ---: |
| Transaction records | 8 |
| Input records with resolved previous-output details | 12 |
| Output records | 16 |
| Outputs for the exact fixture Script | 13 |
| Exact-Script outputs marked dead | 10 |
| Exact-Script outputs marked live | 3 |
| Exact-Script live capacity sum | 1,749,999,994,000 shannons |
| `IndexerTxHashCache` rows | 0 |
| Application DB close/reopen exact equality | PASS |

The three live exact-Script outputs were `(0xce0b13…e2ab39, index 1)`, `(0xe4cbd…96b4cbd, index 0)`, and `(0xe4cbd…96b4cbd, index 1)`. The DB derived statuses by processing the fetched transaction/input graph. This was not compared to an independent wallet balance service; it is an application reconstruction result for the supplied trusted-self transaction set. The artifact's digest and the imported set do not prove that the source omitted no matching transaction.

The queue runner intentionally used an empty address list. It did not make a Neuron wallet, create a wallet UUID, assign ownership, run `LightSynchronizer.upsertTxHashes()`, or insert `IndexerTxHashCache` entries. It proves the real transaction queue/persistor path for the eight real transactions, not full Neuron wallet sync or recovery. No DAO activity or DAO restoration claim is included.

## Restart, continuation, and limitations

- Light Client was stopped and reopened against the same disposable imported store after all eight fetches and after the queue had fetched its previous-transaction dependencies. All eight committed transactions and headers remained available. The final tip was `0x15e1908` / hash `0xb6353d571254391497753583ef4298afe0fbc64f503fddb054647b2c718f2c4e`.
- The grouped historical query after restart still returned all eight D2 transactions; the imported Script cursor remained ahead of H.
- Neuron's disposable SQLite DB closed and reopened with an exact same transaction/input/output snapshot (`restartExact=true`). There was no Neuron wallet ID/cache row, so interrupted cache replay and application progress restart were not tested.
- The original R3 destination store, source Pocket SQLite DB, R2 evidence and prior reports were not modified. A first setup attempt accidentally produced an empty RocksDB copy because a PowerShell wildcard was passed literally; it was excluded from the import/queue experiment. The actual R7 destination copy was rebuilt using per-file copies and SHA-256 comparison.
- No Neuron GUI, full-chain download, Rust rebuild, dependency install, personal wallet data, or TESTNET transaction submission was involved.

## Resource use and reproduction

C: had `6,216,544,256` bytes free before the test and `6,138,269,696` bytes after all clients stopped, remaining above the 4 GB reserve. The measured free-space decrease was about 74.7 MiB and cannot be attributed solely to this test. R7's imported RocksDB directory ended at 2,011,833 bytes across 19 files. The isolated Neuron DB directory measured 505,479 bytes across 10 files. No unrelated data was removed.

Source header inspection (read-only):

```powershell
node --experimental-sqlite tools/wo07-r7/inspect-source-headers.js `
  runs/lite-full-attribution/measurement/C/equivalent/native.sqlite
```

Destination copy was built by copying each file from `%TEMP%\wo07-r3-isolated\data\store` into `%TEMP%\wo07-r7-imported-store\data\store`, then comparing every source/destination file SHA-256 and byte length. Its config reused the R3 TESTNET bootnodes and peer limits, pointed to the new `data/network`, RPC `127.0.0.1:19076`, and P2P `127.0.0.1:19140`.

Start the released client:

```powershell
& "$env:TEMP\wo07-r6-v054-client\ckb-light-client.exe" run `
  --config-file "$env:TEMP\wo07-r7-imported-store\config.toml"
```

For each source pair, query `get_header(hash)`, call `fetch_header(hash)`, poll `get_header(hash)` until fetched, then call `get_transaction(txHash)`. Verify header `hash` and numeric `number`, transaction `hash`, `tx_status.status == committed`, and `tx_status.block_hash == header.hash`. Stop and restart the same process/store, then repeat all eight `get_transaction` calls and the grouped `get_transactions` query using the exact Script and range `[0x1555691,0x15db450)`.

Run the actual Neuron queue/persistor harness against that local RPC:

```powershell
node tools/wo07-r7/real-queue.js `
  "$env:TEMP\wo07-r6-neuron-asar" `
  "$env:TEMP\wo07-r6-queue-db10" `
  http://127.0.0.1:19076
```

Read-only database checks used the Android SDK `sqlite3.exe` with `-readonly`; the Neuron DB SHA-256 at final inspection was `d0e42250cce0b2a85b834f2910734cec87b462bdee9570c72e4eace3daf6e767`.

## Next engineering action

Freeze the R7 harness and evidence. The next justified experiment is not another native-header adapter: v0.5.4 `fetch_header` repaired the mappings without changing D2. To test wallet synchronization rather than only the processing pipeline, first create a legitimate disposable Neuron identity whose exact Script is present in a trusted TESTNET fixture, then seed that identity through Neuron's actual wallet/address services and run the real `LightSynchronizer.upsertTxHashes()` path. Its cache-before-progress ordering, cache drain and interrupted replay must be tested without cursor rewind. Keep a separate matched normal-recovery baseline before making any performance claim.

## Pinned references

- CKB Light Client v0.5.4 `fetch_header`, `get_transaction`, and native block mappings: [RPC](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-bin/src/rpc.rs#L911), [native storage](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/storage/db/native.rs#L1083), [proof processing](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/protocols/light_client/components/send_blocks_proof.rs#L49).
- Neuron v0.204.1 queue and persistor source at `a926e3383d3a3e305b3bde7d233474515ef01a2e`: `packages/neuron-wallet/src/block-sync-renderer/sync/queue.ts` and `packages/neuron-wallet/src/services/tx/transaction-persistor.ts`.
- Authority fixture and released-client proof behavior: [WO07-R2](WO07_R2_RELEASED_CLIENT_EXECUTION.md); native D2 import and RPC behavior: [WO07-R3](WO07_R3_NATIVE_ROCKSDB_ADAPTER.md); prior headless harness: [WO07-R6](WO07_R6_HEADLESS_NEURON_REPLAY.md).
