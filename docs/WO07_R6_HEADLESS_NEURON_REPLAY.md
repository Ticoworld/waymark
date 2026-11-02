# WO07-R6: Headless Neuron Replay

Date: 2 November 2026

## Verdict

**HEADLESS HARNESS PROVEN, REPLAY BLOCKED.** Neuron v0.204.1's packaged `Queue` and `TransactionPersistor` ran under Node without opening Electron. On a synthetic two-transaction fixture, Neuron fetched transactions and headers, resolved the prior output, wrote real Neuron SQLite rows, marked the spent output dead and the successor output live, drained its queue, and retained exact rows after close/reopen.

The genuine eight-transaction D2 fixture did not reach Neuron's queue. The released v0.5.4 Light Client returned eight grouped Script-index results, but its ordinary `get_transaction` RPC panicked while resolving a historical transaction's header: the imported store has no height-to-hash mapping for that transaction block. This is a concrete D2 header-closure gap. No cache rows were inserted because the old Pocket Script has no Neuron wallet identity and WO07-R6 did not invent one. No genuine wallet recovery or speedup is established.

## Pins and runtime

- Neuron release package: v0.204.1; installed executable SHA-256 `74abd9a83cf3a4bfbfb70d6edca49c12d73dc8f272f219ea56dfde9f5f50cc18`; original packaged `app.asar` SHA-256 `ef42a37d28bebd729b4703266e1733315e3aa0605e66d8df6d92ee83c4a251bb`.
- Neuron source reference: `a926e3383d3a3e305b3bde7d233474515ef01a2e`. The clean source-only checkout was `%TEMP%\neuron-wo05-src`; relevant source was not modified.
- CKB Light Client: official Windows x64 v0.5.4 binary, extracted from the previously verified R2 release archive; source pin `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`.
- D2 adapter source: isolated `%TEMP%\wo07-r3-d2`, commit `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`; not modified.
- Runtime: Windows 10 25H2, Node.js `v22.14.0`, CKB client process on local RPC only. The Light Client config had no bootnodes. No chain synchronization was started.

The original Neuron `app.asar` contains the compiled backend modules and SQLite native dependency. Extracting its 75 MB uncompressed payload avoided installing Neuron dependencies or rebuilding Rust. A narrow Electron stub supplied `app.getPath` and IPC surfaces; a Light-mode service stub selected the disposable TESTNET DB. The Neuron Queue and persistence implementation remained the packaged v0.204.1 code.

## Imported fixture RPC attempt

The R3 RocksDB store was copied into `%TEMP%\wo07-r6-light-store`; R3's store was not used as the write target. A separate official v0.5.4 process served the copy on `127.0.0.1:19065`, with outbound peers disabled. The copy's RPC tip was height `22,943,444` (`0x15e16d4`). H's independent authority is established in WO07-R2/R3; WO07-R6 did not redo that proof.

Using the exact R4 Neuron grouped request shape for the fixture lock Script and range `[22,369,937, 22,918,224)`, `get_transactions` returned eight transaction groups. Their block heights ran from `22,369,938` through `22,655,842`; the previous reports establish that the source has 23 Script-index entries for these eight distinct transactions. The returned hashes were:

```text
0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66
0xb7503283af42a8fd1595306e2d5dd4a789e103980207fdafb5229b2e20b7113c
0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894
0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7
0xb23fbbb1db9ca0da48f76993e9258fdadb0f3bc81d9999924561e72583aa5d5a
0xce0b13ba3f23babc6e4cc011a992b1f7bf610dd92b4f6719afde1c91a5e2ab39
0x2067edf16ab143e7bff9ef91803e36ce6a32347c632c75a37d382443ae379738
0xe4cbdffa9002b0283c2c71cc19ec646b85cb58274b8f45d72496e78ae96b4cbd
```

The next request, ordinary `get_transaction` for the first result, closed the RPC connection. The v0.5.4 worker reported:

```text
light-client-lib\src\storage\db\native.rs:1083
stored block number / hash mapping
```

At that line `get_transaction_with_header()` reads the transaction's stored block number, looks up `Key::BlockNumber(height)`, then uses that hash to retrieve `Key::BlockHash(hash)` and its packed header. The expected height-to-hash row was absent. The client process was stopped after capturing the panic. No Neuron application rows were written from this real fixture.

R3's adapter writes the artifact's Script indexes, transaction indexes and transaction bodies, then the Script cursor and global minimum cursor. It does not write `BlockNumber` or `BlockHash` rows for each indexed transaction's block. The D2 artifact carries the handoff H/hash, but not each historical matching transaction's block hash/header. Thus `get_transactions` can enumerate imported index rows while `get_transaction` cannot construct Neuron's expected committed transaction-with-header response. This is not an Electron or Node limitation.

## Headless Queue and SQLite proof

The reproducible synthetic-only runner used Neuron's packaged `Queue`, `TransactionPersistor.saveFetchTx()`, TypeORM entities/migrations and bundled `sqlite3` native addon. It mocked the LightSynchronizer event source and JSON-RPC boundary only. The test used a disposable DB under `%TEMP%\wo07-r6-queue-db9`; no wallet ID or source key was created.

The Queue made two transaction requests, two header requests, and one previous-transaction request. It called the actual persistor for both committed transactions. The DB contained two transaction rows and two input rows. The first output's status became `dead`; the second output's status was `live`. The test drained `Queue.stopAndWait()`, closed the DB, reopened it, and obtained byte-for-byte-equivalent query results (`restartExact=true`).

This proves the headless Queue/persistor plumbing for a synthetic fixture. It does **not** prove the eight D2 transactions can be fetched, nor that Neuron would associate the unowned fixture Script with a wallet. The test did not insert `IndexerTxHashCache` rows: those rows require a real `walletId`, which the old Pocket artifact does not supply. It also did not execute `LightSynchronizer.upsertTxHashes()` or `SyncProgressService` initialization. No pending-cache restart, continuation, exact real Cell/balance comparison or DAO comparison was run.

An initial mock omitted the transaction `hash` field from its `get_transaction` response and made the persistor update the same row twice. The mock was corrected to match Neuron's transaction-with-status response shape; the final result above includes the two expected distinct transactions. No product code was changed.

## Ownership, correctness and limits

The D2 Script remains a Pocket fixture. No mnemonic/xpub exists in the public evidence, and no Neuron wallet UUID was assigned. No TESTNET funds were sent, and no new on-chain activity was fabricated. There was no app-level transaction cache insertion or wallet recovery result.

The R2/R3 authority proof validates the handoff H under the released client; it does not automatically provide or validate the historical header closure required for each transaction's `get_transaction` response. Nor does the D2 digest prove that the source omitted no matching Script transactions. The trusted-self completeness limit remains.

No application performance comparison was attempted. Synthetic timings are not recovery measurements, and historical filtering savings remain unproven.

## Resource audit

C: ended with `6,159,015,936` bytes free (5.736 GiB), above the 4 GB reserve. R6 added an approximately 75 MB ASAR extraction, a 19.6 MB v0.5.4 executable extraction, a 1.86 MB initial RocksDB copy (2.10 MB after client metadata/logs), and small disposable SQLite profiles. No Neuron dependency installation, Rust build, full-chain download or synchronization occurred. The previous `/tmp/wo07-target` build output was not present at inspection; it was not recreated. Only C: was available.

No cleanup was performed. Existing `%TEMP%\wo07-r5-neuron-app` is about 0.506 GB and belongs to the earlier R5 isolated-app diagnostic; removing it would discard that prior startup evidence. The installed Neuron program is about 0.437 GB and is the official local runtime. The new R6 ASAR extraction and test DBs are disposable research artifacts but are retained for reproduction. No Rust/Cargo cache or WSL virtual disk was removed, compacted, or moved.

## Reproduction

From the Waymark workspace, after the R3/R2 temp fixtures are available:

```powershell
New-Item -ItemType Directory "$env:TEMP\wo07-r6-v054-client"
node tools/wo07-r6/extract-neuron-asar.js `
  "$env:LOCALAPPDATA\Programs\Neuron\resources\app.asar" `
  "$env:TEMP\wo07-r6-neuron-asar"

tar.exe -xzf "$env:TEMP\wo07-r2-isolated\ckb-light-client_v0.5.4-x86_64-windows.tar.gz" `
  -C "$env:TEMP\wo07-r6-v054-client" ckb-light-client.exe

node tools/wo07-r6/prepare-client.js `
  "$env:TEMP\wo07-r3-isolated" "$env:TEMP\wo07-r6-light-store"
node tools/wo07-r6/fix-local-client-config.js "$env:TEMP\wo07-r6-light-store"
& "$env:TEMP\wo07-r6-v054-client\ckb-light-client.exe" run `
  --config-file "$env:TEMP\wo07-r6-light-store\config.toml"

node tools/wo07-r6/probe-neuron-modules.js "$env:TEMP\wo07-r6-neuron-asar"
node tools/wo07-r6/persistor-smoke.js `
  "$env:TEMP\wo07-r6-neuron-asar" "$env:TEMP\wo07-r6-neuron-db4"
node tools/wo07-r6/queue-smoke.js `
  "$env:TEMP\wo07-r6-neuron-asar" "$env:TEMP\wo07-r6-queue-db9"
```

Use fresh, nonexistent destination directories for each reproduction run. Run the Light Client command in its own foreground shell while running the Node probes in another; stop that test client with Ctrl+C afterward.

The actual native query used `get_transactions` with the lock Script, `script_type=lock`, `group_by_transaction=true`, order `asc`, limit `0x64`, and range `[0x1555691,0x15db450)`. The subsequent `get_transaction` request for the first returned hash reproduced the missing mapping panic. The two smoke runners are explicitly synthetic and do not read the D2 artifact.

The native RPC requests can be repeated from a second PowerShell window while the test client is running:

```powershell
$script = @{ code_hash = '0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8'; hash_type = 'type'; args = '0xbc5882c4309431ee23ad7bbad4b5c3325539eebd' }
$search = @{ script = $script; script_type = 'lock'; block_range = @('0x1555691', '0x15db450'); group_by_transaction = $true }
$body = @{ jsonrpc = '2.0'; id = 2; method = 'get_transactions'; params = @($search, 'asc', '0x64', $null) } | ConvertTo-Json -Depth 8 -Compress
$result = Invoke-RestMethod -Uri 'http://127.0.0.1:19065' -Method Post -ContentType 'application/json' -Body $body
$result.result.objects | Select-Object block_number, tx_index, @{ n = 'hash'; e = { $_.transaction.hash } }

$body = @{ jsonrpc = '2.0'; id = 3; method = 'get_transaction'; params = @('0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66') } | ConvertTo-Json -Compress
Invoke-RestMethod -Uri 'http://127.0.0.1:19065' -Method Post -ContentType 'application/json' -Body $body
```

## Modified files and next action

New workspace files only:

- `tools/wo07-r6/extract-neuron-asar.js`
- `tools/wo07-r6/fix-local-client-config.js`
- `tools/wo07-r6/persistor-smoke.js`
- `tools/wo07-r6/prepare-client.js`
- `tools/wo07-r6/probe-neuron-modules.js`
- `tools/wo07-r6/queue-smoke.js`
- `docs/WO07_R6_HEADLESS_NEURON_REPLAY.md`

No prior report, Neuron source, D2 source, Pocket source, installed Neuron program or existing wallet profile was changed.

The next engineering action is a bounded D2 header-closure extension: include the canonical block hash and packed header for every distinct block containing an imported Script match; have the destination independently validate each header through released v0.5.4's proof path; atomically install the required `BlockNumber` and `BlockHash` native rows with the Script indexes/transaction rows. Re-run `get_transaction` for the eight existing fixture hashes before attempting Neuron Queue replay again. Once native transaction/header retrieval passes, the queue can be driven headlessly with no wallet association for pipeline-only evidence. Defer `IndexerTxHashCache` insertion until a legitimate Neuron wallet identity exists; do not mint a synthetic wallet UUID.

## Pinned source evidence

- Neuron queue and persistor source at `a926e3383d3a3e305b3bde7d233474515ef01a2e`: `packages/neuron-wallet/src/block-sync-renderer/sync/queue.ts`, `packages/neuron-wallet/src/services/tx/transaction-persistor.ts`.
- Neuron `get_transaction` result handling uses the installed v0.204.1 compiled files `dist/block-sync-renderer/sync/queue.js` and `dist/services/tx/transaction-persistor.js` extracted from the SHA-pinned release archive.
- CKB Light Client v0.5.4 `get_transaction` calls `get_transaction_with_header` in [`rpc.rs`](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-bin/src/rpc.rs#L829); the native lookup requires historical block mappings in [`native.rs`](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/storage/db/native.rs#L1083).
- R3 adapter import logic is in the isolated D2 revision `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`, `crates/d2-script-handoff/src/v054_rocksdb.rs`; its atomic batch copies artifact index/transaction rows and cursor metadata, not per-transaction historical headers.
