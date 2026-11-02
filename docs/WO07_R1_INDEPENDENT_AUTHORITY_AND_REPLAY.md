# WO07-R1: Independent Authority and Exact-Script Replay

Research date: 30 October 2026. Neuron release baseline: `v0.204.1` (`d3a7467d218e4b6f777326682a83fec802669c00`), bundling CKB Light Client `v0.5.4`. The inspected Light Client source is tag commit `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`. D2 source is pinned to `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`.

## Result

**STILL BLOCKED.** WO07's assumption that historical-header proof support from PR #297 is required was too strong. Released v0.5.4 already has a bounded `fetch_header` path that can obtain a historical header proof relative to the destination's current tip, provided that tip is independently accepted by the destination and a peer has a proved state containing that exact tip. This is a credible Route C and does not require trusting the artifact's H hash or relying on PR #297.

That route was not executed. The available independent B destination is an October 14 Pocket SQLite capture, not a Neuron v0.5.4 RocksDB store, and its tip is 107 blocks below the artifact handoff H. No v0.5.4 executable is installed locally. The pinned source's offline test-build probe stopped before compilation because `bytes v1.9.0` is not cached. I did not download dependencies, sync a client, access the connected phone, or import data into an unqualified store. Therefore no D2-to-RocksDB adapter, Neuron RPC query, application replay, restart, or performance comparison was attempted.

The cheapest technically valid next route is **C against a running Neuron v0.204.1 destination**: let its released Light Client establish its own current chain state; request the artifact H by hash through that client's normal `fetch_header`; accept H only after the request is serviced against the exact destination tip hash and the returned header's identity/height are checked. Then use that v0.5.4 destination for the explicit Pocket-v0.5.4-to-Neuron-v0.5.4 storage mapping and RPC proof. This requires a disposable wallet/source and a usable released Neuron runtime; neither is available in the inspected local fixtures without further setup.

## Authority routes

| Route | Finding | Result |
| --- | --- | --- |
| A. Existing independent fixture | B's frozen independent tip is height `22,737,156`, hash `0xad9853732ca3485e87f9bb6c11530d430f7de2a51df35c7590a4c239c4ee6b19`. Artifact H is `22,737,263`, hash `0x5b6578a1acfc6f061d8df5584511ff982b12e8f034ef80bb4bbe7792735c4f31`. B is 107 blocks below H. B's `native.sqlite` is Pocket storage; it cannot be opened as Neuron's native RocksDB. The old capture cannot simply assert H or supply its hash. | Not executable as a Neuron destination without a v0.5.4 RocksDB runtime and a supported independent chain-state fixture. No catch-up was run. |
| B. Fresh contemporary handoff | A new source and a new destination synchronized by released v0.5.4 could choose a recent common H, but there is no fresh disposable Neuron wallet/source runtime in the workspace. Rebuilding a full destination fixture is more work than using `fetch_header` with an established destination. | Deferred. |
| C. Released historical-header retrieval | `fetch_header(hash)` returns a locally stored header if present; otherwise it queues a fetch. The scheduler anchors the proof request to the destination's current tip hash and chooses peers whose proved state contains that exact tip. The response must match the requested last-state hash; requested headers are checked against the request, PoW/extra hashes are checked, and the MMR proof is verified against the response last header before the fetched header is stored. Thus the artifact hash is only a lookup identifier. A header returned from this proof flow is linked to a chain state containing the independently established destination tip. | **Best route in principle; source-traced, not run.** RPC `Fetched` alone is not sufficient evidence unless the test establishes that it followed the proof path (for example, H was absent locally before request) and verifies exact height/hash after fetch. |
| D. Historical proof extension | PR #297 is not a prerequisite for the first proof: v0.5.4 already has the MMR-backed fetch path above. | Not needed for this spike. |

The fetched header is only an authority check for the handoff block's chain membership. It does not prove that the D2 artifact contains every Script match. D2's trusted-self source assumption and omission limitation remain unchanged.

## Fixture identities

| Role | Preserved fixture | Client/storage identity | Chain identity |
| --- | --- | --- | --- |
| Artifact source | Arm C, `measurement/C/equivalent/native.sqlite`; SHA-256 `60005bde373b96dec1c1a383b9bf98191e50079d9a2ac829b8baae40afcaf682` | Pocket-pinned CKB Light Client v0.5.4-derived SQLite profile `pocket-node@6eda0b7a4601050b011591d41cc702f0dc7a7c38/ckb-light-client@0.5.4/kv-v1` | Source tip 22,737,272; artifact H 22,737,263 and hash above |
| Independent destination candidate | Arm B, `measurement/B/equivalent/native.sqlite`; SHA-256 `72383152bff0c164f09de07917a94f868e34617a11524d84556235cb039d138c` | Fresh Lite-equivalent Pocket v0.5.4-derived SQLite store; separate from C's captured store | Tip 22,737,156, hash `0xad9853732ca3485e87f9bb6c11530d430f7de2a51df35c7590a4c239c4ee6b19` |
| Required integration target | No local destination store or runtime available | Neuron v0.204.1 Windows native CKB Light Client v0.5.4, RocksDB (`ckb-rocksdb 0.21.1`) | Must establish its own chain state at runtime |

The source and B candidate share the research wallet fixture but are separate fresh recovery arms; B's chain store is not copied from C. Neither Pocket SQLite capture is a released Neuron RocksDB destination.

## RPC range semantics

The v0.5.4 `get_transactions` implementation checks `block_number < r0 || block_number >= r1`, so its block range is **half-open**: `[from, to)`. The checked source test fixture queries `[100, 200)` and expects rows for the 100 blocks `100..199`; the implementation and test establish that 200 is excluded. The source tests were inspected, but not executed because the offline build could not resolve the uncached dependency.

Boundary consequence for a D2 handoff at H:

| Query | H-1 row | H row | H+1 row |
| --- | --- | --- | --- |
| `[H-1, H)` | included | excluded | excluded |
| `[H, H+1)` | excluded | included | excluded |
| `[H+1, H+2)` | excluded | excluded | included |
| `[H, H)` | empty | empty | empty |

The correct replay ordering is therefore to keep Neuron's app `syncedBlockNumber` at H after draining all earlier cached rows. The next ordinary interval `[H, H+1)` returns H. Only after those results have entered Neuron's durable transaction cache, and normal queue processing has completed, may app progress advance beyond H. Setting app progress to H+1 immediately after import would skip an H result. This matches Neuron's source-level cache-before-progress ordering, but it has not been tested with imported rows. Pagination uses the last matching key as cursor and must be exercised with actual results spanning H-1/H/H+1 before integration is accepted.

An empty interval is logically empty under the same predicate. Restart and pagination behavior were not run against a live imported store. No real transaction rows in the preserved D2 fixture fall on all three adjacent boundaries, so a boundary test needs a newly captured controlled fixture or a test-only RPC fixture clearly labeled as synthetic; synthetic rows must not be represented as end-to-end recovery evidence.

## Adapter and replay status

No adapter was implemented. The D2 Pocket artifact profile is `pocket-node@6eda0b7a4601050b011591d41cc702f0dc7a7c38/ckb-light-client@0.5.4/kv-v1`; Neuron's native v0.5.4 profile is RocksDB using `ckb-rocksdb 0.21.1`. The v0.5.4 key/value row layout is compatible in principle, but its concrete `Storage` API predates the newer D2 `StorageBackend` abstraction. D2 v1 enforces exact adapter-profile equality. A future isolated adapter must add a named, allowlisted semantic mapping for this exact pair; it must not relabel arbitrary profiles or globally weaken profile equality.

| Required evidence | WO07-R1 status |
| --- | --- |
| Independent destination authority for H through released-client proof path | NOT RUN |
| Import/reopen of D2 rows into Neuron v0.5.4 RocksDB | NOT RUN |
| `get_transactions` exact hashes, including H-1/H/H+1 and pagination | NOT RUN |
| Proof that historical filtering was avoided | NOT RUN |
| Neuron cache/queue/persistor replay | NOT RUN |
| Exact history, Cells, balances, DAO and app-progress comparison | NOT RUN |
| Cold restart and post-H continuation | NOT RUN |
| End-to-end performance | UNPROVEN |

The previous D2/Pocket test remains the only executable import evidence: one Script artifact with 3 Cell-index rows, 23 transaction-index rows and 8 closure transactions, 7,494 bytes. It is not Neuron/RocksDB or RPC compatibility evidence.

## Environment and execution record

- Read-only fixture inspection found B's `native.sqlite` at 1,896,448 bytes with SHA-256 `72383152bff0c164f09de07917a94f868e34617a11524d84556235cb039d138c`; its frozen public summary reports the tip above. The existing D2 source artifact remains the WO07 artifact at H above; source SHA-256 remains `60005bde373b96dec1c1a383b9bf98191e50079d9a2ac829b8baae40afcaf682`.
- C: had about 15.9 GB free at the resource check. The existing WSL Cargo target was 1.9 GB and Cargo registry 2.2 GB. Rust/Cargo were already present.
- No `ckb-light-client` executable was found on the local command path or in the searched WO07 temp area. ADB reported a connected SM-S9180, but it was not queried or modified because this work order forbids accessing personal wallet data and the connected device was not established as a disposable Neuron test destination.
- Reproducible build probe, from the pinned v0.5.4 source checkout:

```sh
CARGO_TARGET_DIR=/tmp/wo07-target CARGO_BUILD_JOBS=2 CARGO_PROFILE_TEST_DEBUG=0 \
cargo test -p light-client-bin --offline --no-run
```

The first attempt found the earlier sparse checkout lacked crate files; after expanding only the temporary checkout's source paths, the second attempt stopped before compilation with `failed to download bytes v1.9.0` because offline mode could not find that crate. No network fetch or build was started after that. The working tree and all prior research evidence remain unchanged; only this report was added to the Waymark workspace.

## Pinned source evidence

All CKB Light Client references below are pinned to `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`.

| Claim | Evidence | Establishes |
| --- | --- | --- |
| `fetch_header` is cache-first, then queues a peer fetch | [rpc.rs, `fetch_header`](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-bin/src/rpc.rs#L911) | A remote hash is a lookup key, not authority by itself. |
| Requests are anchored to local tip and sent to peers with a proved matching tip | [light-client protocol fetch scheduler](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/protocols/light_client/mod.rs#L725), [proved-peer selection](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/protocols/light_client/peers.rs#L2026) | The fetch proof is tied to destination chain state, subject to normal v0.5.4 light-client peer validation. |
| Fetched response checks requested state and MMR/PoW before storage | [SendBlocksProof handler](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/protocols/light_client/components/send_blocks_proof.rs#L49), [native fetched-header storage](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-lib/src/storage/db/native.rs#L773) | The requested historical header is verified against the response's proved last state before local storage. |
| Transaction block-range upper bound is exclusive | [rpc.rs, `get_transactions`](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-bin/src/rpc.rs#L315), [range predicate](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-bin/src/rpc.rs#L446), [service range test](https://github.com/nervosnetwork/ckb-light-client/blob/778590aa3ad7f71ee80b2d4c54af02c42e2dfa25/light-client-bin/src/tests/service.rs#L499) | `[from,to)` behavior and existing range fixture; the test was not run in R1. |
| D2 profile matching is fail-closed | [D2 operations](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/crates/d2-script-handoff/src/operations.rs#L175), [D2 profile guide](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/docs/D2_V1.md) | A new mapping must be explicit and restricted. |
| Neuron queues hashes before advancing per-Script app progress | [Neuron `light-synchronizer.ts`](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts#L91) | Correct ordering exists for normal synchronization; imported cursor behavior is not tested. |

## Exact next action

Resume only with a disposable Neuron v0.204.1 TESTNET destination whose v0.5.4 Light Client can establish and retain its own current chain state, plus the existing disposable source artifact or a fresh artifact. Use Route C: request H by its source-provided hash, but accept it only after v0.5.4 has proved it against the destination's exact local tip and the test confirms the returned header's height/hash. Then implement the narrowly allowlisted Pocket-v0.5.4-to-Neuron-v0.5.4 RocksDB adapter in a separate experimental checkout and test import/reopen/RPC before touching Neuron app replay. Add actual H-boundary rows to the controlled fixture or a narrowly scoped test fixture, verify `[H-1,H)` and `[H,H+1)` with pagination and restart, and hold Neuron app progress at H until all queue rows are processed.

The single prerequisite capable of changing this blocked result is access to a **disposable, running Neuron v0.204.1 TESTNET destination and source fixture** (or authorization to create one and perform its normal Light Client sync). No further protocol extension or PR #297 work is justified before that prerequisite exists.
