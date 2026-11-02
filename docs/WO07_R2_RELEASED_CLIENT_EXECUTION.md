# WO07-R2: Released Client Execution

Date: 31 October 2026. Target: official CKB Light Client v0.5.4 for Windows x64, the version bundled by Neuron v0.204.1. This report continues WO07-R1 and preserves earlier evidence.

## Verdict

**A. INDEPENDENT AUTHORITY PROVEN.** The released v0.5.4 client independently synchronized TESTNET state, fetched the historical handoff header H from peers after confirming it was absent locally, fetched H's parent, and retained both headers across process restart. The runtime request lifecycle and the pinned v0.5.4 source path together establish that the requested header was received through a proof request tied to the destination's proved tip.

This does **not** prove D2 import, historical Script RPC replay, Neuron application replay, or faster recovery. No adapter was implemented. The test stopped after authority and restart because the official precompiled package has no storage-import command/RPC, the local Rust cache does not include v0.5.4 RocksDB bindings, and available C: space fell to about 6.1 GB. Building an additional RocksDB toolchain risked consuming the previously set 4 GB reserve.

## Official Binary

GitHub's official `v0.5.4` release metadata lists `ckb-light-client_v0.5.4-x86_64-windows.tar.gz` at 8,837,344 bytes with digest `sha256:fe38b58d85239149bd9aab81f9f90dff3ee8d7d01d09435be6621e6525f0cab8`. The downloaded archive's local SHA-256 matched exactly. Its contents were only `ckb-light-client.exe`, `config/mainnet.toml`, and `config/testnet.toml`. The executable reported:

```text
CKB Light Client 0.5.4 (778590a 2026-01-02T02:55:12Z)
```

The release tag resolves to source commit `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`. The archive was extracted under `%TEMP%\wo07-r2-isolated`; no project or system binary was replaced.

## Independent Destination

The client used a copy of the official TESTNET config with its own `data/store` and `data/network` directories under `%TEMP%\wo07-r2-isolated`. RPC listened only on `127.0.0.1:19054`, P2P listened only on `127.0.0.1:19118`, and the config allowed at most four outbound peers (16 total peers). No source Light Client state was copied. No Neuron app database, credentials, or phone data were accessed.

Resource controls were: retain at least 4 GB free on C:, stop if this test's store exceeded 1 GB, cap peers at four outbound, and bound the synchronization/proof run to minutes rather than initiating any full-node download. At start, C: had 6,259,994,624 bytes free. After client restart and the proof requests, the isolated data directory was 1,718,238 bytes and C: had 6,095,290,368 bytes free. The measured directory growth was about 1.7 MB. Exact network byte consumption was not available from the client or the process-level telemetry used here; network exposure was bounded operationally by the four-peer cap and short run. The Light Client did not request full blocks or create a full-node chain database.

The client reported genesis hash:

```text
0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606
```

Its local node ID was `QmSn8QCLipUUNBfQzrDevEt4SR7gSta8qLmdDTK9xaXyQF`. It connected to TESTNET peer `QmQoTR39rBkpZVgLApDGDoFnJ2YDBS9hYeiib1Z6aoAdEf`. At the authority request, the destination tip was height `0x15db336` (22,917,942), hash `0x71047db4f52f7e4f9e885b5d6d4aa1b65ce3ae66efcf0930dd7fb300089d5eaf`; the peer's `proved_best_known_header` matched that hash and height. Later tip samples advanced normally.

## Historical Header Authority

Target handoff:

- H: `22,737,263` (`0x15af16f`)
- Expected H hash: `0x5b6578a1acfc6f061d8df5584511ff982b12e8f034ef80bb4bbe7792735c4f31`
- Expected parent hash: `0x24e3a2fbc16a6844519d45518158b71d8efea811ee3f04cd2330f8bac372c501`

Before fetching, `get_header(H)` returned `null`, proving H was absent from the new local header cache. `fetch_header(H)` returned `status: added`; polling the same RPC later returned `status: fetched` and the exact expected header. The header reported height `0x15af16f` and the expected hash. Its parent hash was then independently looked up: `get_header(parent)` was initially null, `fetch_header(parent)` queued it, and a subsequent query returned height `0x15af16e` (22,737,262), hash equal to H's `parent_hash`. This confirms direct parent continuity for H.

The v0.5.4 runtime's fetch path is asynchronous. At the time of the request, the peer's proved-best-known header equaled the destination's independently obtained tip. In the pinned source, the scheduler sends a `GetBlocksProof` request with the destination tip hash; it selects peers whose proved state contains that exact tip. The proof handler requires the response last-state hash to match the request, checks that the returned header hashes are those requested, validates proof-of-work/extra hashes, verifies the MMR proof against the response last header, and only then stores the fetched header. The sequence `absent -> added -> fetched`, plus a peer's matching proved tip, establishes a peer-proof retrieval rather than a response from the old source store. The artifact hash was used only as the lookup identifier.

The destination tip during the original request was later than H by 180,679 blocks. The proof flow validated H's membership relative to the independently proved destination state. This establishes header-chain authority under the released Light Client's trust/consensus model; it does not prove D2 Script-result completeness.

## Restart

The binary exposes no stop RPC. It was launched hidden, and Windows `AttachConsole` returned error 5, so a graceful console signal was unavailable. To perform a cold process restart without touching other processes, the disposable client process (PID 21372) was terminated; its store remained intact. It was relaunched as PID 1064 using the same isolated config. After restart:

- `local_node_info.version` reported `0.5.4`.
- `get_header(H)` returned the exact same H hash and height.
- `get_header(H.parent_hash)` returned the exact parent hash and H-1 height.
- `get_tip_header` returned a later TESTNET tip above H.

This demonstrates persistence and RocksDB recovery after abrupt process exit, not graceful shutdown. The store opened and served the historical headers after restart.

After capturing the post-restart evidence, the isolated process was terminated again (no stop RPC/attachable console was available). It is no longer running. Final isolated data size was 1,790,157 bytes; C: had 6,231,367,680 bytes free.

## Adapter and Replay

**Not attempted.** The existing D2 artifact is Pocket-v0.5.4-derived SQLite profile data. The target Neuron client uses native RocksDB (`ckb-rocksdb 0.21.1`). The v0.5.4 release archive includes no import facility. D2's existing upstream adapter depends on the newer `StorageBackend`/`LightClientStorage` abstraction and its D2 profile; those abstractions are absent from v0.5.4. D2's Pocket adapter can support the source format, but a narrowly allowlisted semantic profile mapping and a v0.5.4 RocksDB adapter still need implementation and tests.

The prior offline source-build probe for `light-client-bin` stopped before compilation because `bytes v1.9.0` was not cached. Cargo artifacts from the earlier D2 test do not include `rocksdb`/`librocksdb-sys` bindings. A RocksDB-aware importer must therefore acquire/build additional Rust dependencies or use a verified compatible database utility. With C: at 6.1 GB free, preserving the 4 GB reserve leaves about 2.1 GB for that work, which is not a defensible budget for an unmeasured RocksDB toolchain build. No dependency was downloaded and no store was modified for import.

Consequently, there are no imported row counts, historical `get_transactions` results, H-1/H/H+1 RPC tests, pagination tests, Neuron transaction-cache rows, queue/persistor replay, wallet-state comparisons, or app restart/continuation results. The exact RPC range contract remains source-verified as `[from,to)`; it was not exercised against imported data here. Neuron replay remains unproven.

## Performance and Trust

No recovery performance comparison was run. Independent header validation does not itself avoid Light Client Script filtering or Neuron app reconstruction. D2 remains a trusted-self source handoff: its digest is not source authentication, and destination proof of H does not prove the source omitted no matching historical Script transaction. Any later import must keep Neuron's app checkpoint at H until all results from the imported range are durably queued and processed through Neuron's ordinary synchronization path.

## Pinned Evidence

| Claim | Source |
| --- | --- |
| Official v0.5.4 release, signed tag commit and binary assets | [CKB Light Client v0.5.4 release](https://github.com/nervosnetwork/ckb-light-client/releases/tag/v0.5.4) |
| `fetch_header` cache-first/async behavior | [v0.5.4 `rpc.rs`](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-bin/src/rpc.rs#L911) |
| Request anchored to the local tip and sent to peers with matching proved state | [v0.5.4 Light Client protocol](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/protocols/light_client/mod.rs#L725), [proved-peer selection](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/protocols/light_client/peers.rs#L2026) |
| Requested header proof is checked before storage | [v0.5.4 `SendBlocksProofProcess`](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/protocols/light_client/components/send_blocks_proof.rs#L49), [native storage](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/storage/db/native.rs#L773) |
| Neuron ordinary cache-before-progress ordering (not exercised in R2) | [Neuron pinned `light-synchronizer.ts`](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts#L91) |
| D2 exact profile enforcement and trusted-source contract | [D2 pinned operations](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/crates/d2-script-handoff/src/operations.rs#L175), [D2 v1 guide](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/docs/D2_V1.md) |

## Exact Next Action

Do not repeat the authority test or pursue PR #297. The next action is a separately budgeted, isolated **v0.5.4 RocksDB adapter spike** on a machine with enough disk for cached RocksDB dependencies and build output while preserving a 4 GB reserve. It must add one allowlisted mapping for the exact Pocket-v0.5.4-derived source profile to the Neuron-v0.5.4 native RocksDB profile, then validate H against the already independently demonstrated released-client proof path, import atomically under exclusive lifecycle, reopen the client, and query exact historical Script results. Only after RPC replay passes should a separate Neuron runtime be used for app cache/queue/persistor and exact wallet-state tests. Performance remains a later gate.
