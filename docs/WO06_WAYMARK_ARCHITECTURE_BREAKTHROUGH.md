# WO06: Waymark Architecture Breakthrough Investigation

Research date: 30 October 2026. Neuron source is pinned to `develop` `a926e3383d3a3e305b3bde7d233474515ef01a2e` and RC `484a46dadde2a0adfd7975d0159be898b199cf80`; those inspected recovery/sync files are unchanged between the pins. The current CKB Script Port checkout examined is `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`. This was source and existing evidence review only: no build, new test run, chain sync, wallet access, source change, PR or external contact occurred.

## Executive summary

WO05 correctly rejected transferring Neuron's wallet progress into an empty application database. This investigation changes one premise: a checkpoint-only package is not the only candidate. CKB Script Port (D2) already defines and implements a narrow handoff of one exact Script's light-client index rows and referenced transaction closure. A destination validates network genesis and the handoff block hash against its own light-client chain authority, imports atomically, then continues normal filtering after the handoff height. It does not transfer Neuron's app database or signing material.

There is real reference-consumer evidence for that primitive in Pocket: a testnet source with one wallet lock Script exported a 1,767-byte artifact; a fresh Pocket light-client store accepted it; Pocket requested filtering from H+1, rebuilt its own app view from the imported client state, processed a later transaction, and remained coherent across a force-stop/reopen. The D2 invocation was host-side and the output was staged into Pocket. This is not a Neuron result, full-wallet migration, or proof of historical completeness.

The key integration insight is to keep Neuron's two progress domains separate. Neuron must not set `SyncProgress.syncedBlockNumber=H` while its application database is empty. Instead, the imported client index is the historical source for Neuron's ordinary `get_transactions` replay over the imported range. Neuron's existing queue then fetches transactions, headers and previous outputs and rebuilds its application records; only after that replay is drained may Neuron advance its app progress to H and continue from H+1. Whether Neuron's pinned bundled Light Client can serve the full imported range through its RPC after import, and whether this path avoids material work, remain unproven.

**Decision: B. PROMISING NEW DIRECTION.** Authorize one bounded Neuron TESTNET integration proof, not production work. The distinguishing candidate is selective exact-Script Light Client state handoff followed by Neuron-native wallet database reconstruction. Its potential saving is avoiding the destination's repeated Light Client historical filtering/proof/block processing, not avoiding wallet transaction persistence. D2 explicitly trusts the source's derived index and cursor; it does not prove that a malicious, buggy or incomplete source omitted no matches. The experiment must make the trusted-self source model explicit and must fail closed on every incomplete application replay.

## Investigation scope and sources

WO04/WO05 remain the source of Neuron release, recovery, and prior limits. This pass focused on the different D2 design, the actual Neuron import path, and trust/completeness attacks. The `ckb-script-port` source was read from the existing public repository in a shallow, filtered checkout outside this workspace at the pin above. Its checked-in G3 evidence is dated 10-11 September 2026 and identifies its own source/device boundaries. It is not newly rerun evidence.

Neuron release baseline remains v0.204.1 (`d3a7467d218e4b6f777326682a83fec802669c00`), with CKB v0.204.0 and CKB Light Client v0.5.4 in release notes. The main candidate must pin a single released build and its bundled Light Client profile. Develop's package selectors are not proof of release binaries. The inspected Neuron sync files match through the noted v0.209.0 RC, but the experiment should use the exact artifact under test, not combine client versions.

## Three independent passes

### Pass 1: Neuron data path

`LightSynchronizer.upsertTxHashes()` asks Light RPC `get_transactions` for each registered Script over `[SyncProgress.syncedBlockNumber, LightScriptFilter.blockNumber]`, paginating results. It inserts returned transaction hash, transaction index, block number, Script hash, address and wallet ID into Neuron's `IndexerTxHashCache`; only then does it update Neuron's Script progress to the Light Client cursor. This ordering means Neuron's app checkpoint represents the range for which transaction discoveries have been queued, not necessarily the range whose wallet rows are fully persisted.

The block queue waits until Script progress has passed the cached transaction's block and the Light Client can fetch that transaction. It obtains transaction bodies and headers, resolves previous transactions/outputs, invokes `TransactionPersistor.saveFetchTx()`, generates addresses as needed and marks cache rows processed. Neuron persists its own transaction/input/output and cell-state relations. DAO interpretation uses those app records and associated output data/deposit links. The Light Client's native derived index and Neuron's app database are distinct stores with distinct cursors.

On restart, Neuron can resume local per-Script progress and process unprocessed app cache entries. That does not recreate records absent from a fresh app database. A correct importer therefore needs a staged replay/drain barrier before it advances the destination's Neuron progress. D2's native cursor cannot stand in for Neuron's `syncedBlockNumber`.

### Pass 2: D2 contract and real reference evidence

D2 v1 exports one exact packed Script and role, genesis, handoff height/hash, native Script-derived rows, transaction-index rows, and the referenced transaction closure. It validates format/profile, Script identity, closure structure, destination genesis and destination-recognized block hash at H; it imports the selected rows atomically while retaining destination chain/header/peer authority. It requires exclusive, quiescent storage lifecycle and reopen before normal workers resume.

Its digest is unkeyed BLAKE2b-256 for integrity, not source authentication. The D2 docs state that the destination cannot detect a source that omitted historical Script matches or overstates its cursor while keeping the artifact internally consistent. H's block hash proves the destination agrees on that chain point; it does not prove that the source's Script index is complete through H.

The G3-1R1 Pocket evidence is a useful reference flow, not Neuron proof. It used one UI-created TESTNET lock Script, a real Pocket `kv` store, production D2 export/inspect/validate/import, a fresh destination, H+1 normal filtering, application reconstruction, a post-H transaction, and force-stop/reopen. The D2 call was host-side and the imported native state was staged into a disposable Pocket sandbox. It did not prove multiple Scripts, discovery candidates, general version migration, mainnet-scale behavior, arbitrary-depth reorg safety, or Neuron integration.

### Pass 3: strongest attacks and response

| Attack / failure | Unsafe outcome | Required handling in the proposed proof |
| --- | --- | --- |
| Progress imported without records | Missing historical transactions, inputs/outputs, live Cells, balances and DAO linkage | Never import an app completion checkpoint. Replay all imported client results through Neuron's ordinary queue and wait until each row is processed. |
| Source omits a matching transaction or lies about its cursor | Silent missing history despite correct H | State trusted-self source assumption; compare source export against independently generated test oracle and run a deliberate omission negative test. The destination cannot cryptographically prove absence with current API. |
| Artifact modified and digest recomputed | Valid structure with attacker-selected derived rows | Trusted transport/authentication is separate from wallet signing. A production handoff needs authenticated origin or explicit user trust; self-hash alone is not authentication. Test corruption rejection. |
| Wrong network or Script | Cross-network or foreign wallet index contamination | Bind exact packed Script, role, genesis, format/profile; derive expected Script locally from restored wallet; reject all mismatches. |
| H on a different fork/reorg | Stale rows/cursor become inconsistent | Validate H against destination's own accepted chain. Test a bounded reorg if fixtures allow; on changed H invalidate/re-export or rescan affected suffix. No arbitrary-depth guarantee. |
| Newly discovered account/address Script absent | Activity on unexported Script is not recovered | Keep Neuron's normal address/account discovery and scan each required exact Script. One-Script D2 is not a complete wallet archive. |
| Transaction cache replay races app progress update | Restart sees a high cursor but missing wallet records | Add a Neuron integration barrier/transactional ordering; only commit app progress after replay cache is drained and semantic checks pass. Exercise crash points. |
| Imported current Cell view treated as spend proof | Stale or source-incomplete data presented as canonical spendable funds | Reconcile against destination's current chain/indexer and Neuron's normal live-cell query; D2 is not a wallet UTXO proof. |
| Schema/version drift or lifecycle race | Corrupt store, mixed profile, partial import | Pin exact Light Client storage profile; exclusive lifecycle lock; atomic import; fail closed on unsupported profile; reopen before workers. |
| Privacy leakage | Script and history reveal wallet activity | Encrypt/authenticate transport as appropriate; D2 contains public but privacy-sensitive wallet data; no mnemonic, private keys, keystore or device key material. |

## Architecture: exact boundary

The smallest candidate is **a per-Script Light Client handoff composed with native Neuron replay**, not an app database snapshot.

1. On the source, derive and enumerate the exact Neuron lock Scripts needed for the chosen controlled wallet. Quiesce the Light Client and export a separate D2 artifact per Script/role. Record the source client/profile and H/hash. Do not include wallet signing or OS keystore data.
2. On a fresh destination, restore the same disposable mnemonic normally with fresh destination password/security. Neuron derives the expected Scripts. Start and synchronize the destination Light Client sufficiently to independently establish matching genesis and H/hash.
3. Stop sync workers and use the pinned storage adapter's exclusive lifecycle. Inspect and validate each artifact; reject any mismatch. Import atomically, close/reopen the client, then restart Light Client processing from H+1.
4. Keep Neuron app `SyncProgress` at a replay-safe lower boundary. For each imported Script, ask the destination Light Client RPC for matching historical transactions through H, insert them into Neuron's ordinary transaction cache, and run Neuron's ordinary transaction/header/previous-output persistence queue. Do not set its app synced cursor to H until the historical replay has completed and all resulting cache entries are processed.
5. Continue normal Neuron synchronization after H. Compare the rebuilt application state with the independent oracle at a fixed common canonical block. Cold restart, repeat comparison, and exercise recovery from interruption during replay.

The main source-level uncertainty is whether the exact Light Client profile bundled with the selected Neuron release exposes all imported historical `get_transactions` results after D2 import, including the small handoff fixture, with no re-filter. The D2 Pocket result supports the storage behavior for Pocket's pinned profile; it does not establish Neuron's bundled profile. A harness that directly inserts `SyncProgress=H` is invalid because it bypasses app reconstruction.

## What work could be saved

| Work | Baseline fresh Neuron restore | Exact-Script handoff candidate |
| --- | --- | --- |
| Light Client chain/peer startup and synchronization | Required to destination tip/readiness | Still required; D2 does not transfer chain or peer authority. Destination must know H/hash. |
| Light Client Script historical filtering and matched-block processing | Required across the chosen historical range | Potentially avoided through H for the exact imported Script if its indexed results are usable after import. This is the candidate saving. |
| Neuron Script result query | Range query creates Neuron cache rows | Still required to rebuild empty Neuron application DB from imported local index. It may be local and cheap, but must be measured. |
| Transaction/header/previous-output fetch and app reconstruction | Required | Still required through Neuron's own persistor for correct history, Cells, balances and DAO. |
| Address/account discovery and unexported Scripts | Required | Still required. One artifact only covers one exact Script. |
| Full-node chain sync and chain-wide indexer initial sync | Required in full-node mode | Not avoided. D2's current integration candidate is Light Client mode only. |
| Export/import/validation | None | Added cost; count source export, artifact transport, destination import, Neuron replay, verification and catch-up. |

This is not merely moving the same wallet DB rebuild: Neuron still rebuilds it. Potential net benefit is replacing destination's historical Light Client filter/proof/block work with a validated local Script index transfer. But if Neuron's ordinary Light Client restore is already dominated by local replay, if the imported index cannot be replayed without re-filtering, or if destination verification forces full historical filtering, the net gain may be negligible. No Neuron timing or work-volume figure is claimed.

## CKB protocol comparison

CKB's light client uses the block-filter protocol described by RFC 0045 alongside RFC 0044. Filter hashes/checkpoints and matched block retrieval support efficient client-side Script history discovery. This is chain/network synchronization machinery; a D2 artifact carries one source-derived Script view, not consensus state. A matching header H does not authenticate completeness of the source's Script result set.

Bitcoin AssumeUTXO is a useful comparison but a different trust design. Bitcoin Core recognizes a snapshot UTXO commitment compiled into released network parameters; it can use that snapshot while a background chainstate validates history and checks the reconstructed state against the trusted commitment. D2 v1 has no consensus/release-pinned commitment to a wallet Script index, and no equivalent background completeness proof. It is therefore a trusted-self acceleration, not an AssumeUTXO-style trustless fast bootstrap.

The open CKB Light Client PR #297 proposes an API to revalidate a historical header using existing proof/PoW/MMR machinery against accepted chain authority. If merged and shipped, it could strengthen verification of H, but it cannot prove that a Script index includes every matching transaction. It does not by itself remove the trusted-source assumption. Its open status is not adoption or release support.

## Decision and recommended boundary

**B. PROMISING NEW DIRECTION.** The prior “progress-only is unsafe” result remains true, but D2 supplies a different, technically credible candidate: transfer indexed Script-derived data and transaction closure, preserve destination chain authority, then reconstruct Neuron application state through Neuron's own code. Pocket reference evidence raises this from abstract possibility to a working one-Script cross-client pattern.

The evidence justifies exactly one controlled Neuron integration proof because a specific expensive operation might be skipped: historical Light Client Script filtering through H. It does not justify production feature work, complete wallet migration, copying Neuron databases, trusting an imported Neuron app progress value, or claiming trustless history completeness.

### Remaining unknowns that can change the decision

- Whether Neuron's exact released Light Client profile can expose the imported historical transaction result set over RPC without refiltering.
- Whether that avoided filter work is substantial relative to Neuron's mandatory app replay and validation, including total export/import time.
- How many exact Scripts a representative Neuron restore needs, including accounts/address discovery and multisig cases.
- Whether Neuron's sync worker can be given a replay barrier without invasive queue/database changes.

The first is a cheap harness capability check; the second is the controlled timing result. If the first fails or the candidate does not beat a normal restore in total work/time while matching exact state, stop this direction. No wider literature review is needed to resolve those facts.

## Source evidence table

Links are pinned to the source revisions listed. The D2 repository documents are implementation/evidence artifacts, not Neuron claims.

| Claim | Pinned source / location | Evidence establishes |
| --- | --- | --- |
| Neuron queries historical range and inserts cache before updating Script progress | [Neuron `light-synchronizer.ts`, develop](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts#L91) | `get_transactions` range, cache upsert and subsequent synced-height update. |
| Neuron transaction cache is staged and processed separately | [Neuron `indexer-cache-service.ts`, develop](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/indexer-cache-service.ts#L245) | Cache records and unprocessed queue are distinct from Script progress. |
| Neuron queue fetches bodies and previous outputs then persists | [Neuron `queue.ts`, develop](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/queue.ts#L124), [transaction persistor](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/services/tx/transaction-persistor.ts#L198) | Neuron application rows are rebuilt by its existing persistence path. |
| D2 v1 exact Script artifact and trust limits | [CKB Script Port README at `9e8d6f6`](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/docs/D2_V1.md) | Artifact fields, destination authority checks, atomic import, and explicit non-claim of completeness proof. |
| D2 destination binds genesis/H/hash to local authority | [D2 operations at `9e8d6f6`](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/crates/d2-script-handoff/src/operations.rs#L135) | Imported cursor cannot exceed destination tip and H must match local chain hash. |
| Pocket reference consumer rebuilt and continued after D2 import | [G3-1R1 evidence at `9e8d6f6`](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/docs/G3_1R1_POCKET_EXECUTION_EVIDENCE.md#L1) | One real Pocket Script, host-side import/staging boundary, H+1 continuation, app rebuild and restart. |
| CKB uses block filters for light clients | [RFC 0045](https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0045-client-block-filter/0045-client-block-filter.md) | Protocol background; does not give D2 a compact per-wallet completeness proof. |
| AssumeUTXO has a trusted network snapshot commitment and background validation | [Bitcoin Core AssumeUTXO design](https://github.com/bitcoin/bitcoin/blob/master/doc/design/assumeutxo.md) | Comparison model; not equivalent to a self-hashed wallet artifact. |
| Historical header verification API is proposed but open | [CKB Light Client PR #297](https://github.com/nervosnetwork/ckb-light-client/pull/297) | Potential strengthening of H validation only; does not authenticate complete Script query results and is not a shipped dependency. |

## Unproven claims and evidentiary limits

- No Neuron runtime result, importer, exact database comparison, or recovery timing was produced.
- Pocket evidence is one Script on TESTNET; it is not multi-account Neuron evidence.
- D2's digest protects accidental corruption but does not authenticate source identity or prove result completeness.
- H validation protects chain-point agreement only. It does not establish that the source did not miss transactions, scripts, discovery candidates, or older history.
- Current Neuron source shows the required queue and progress separation, but not an existing D2 integration hook.
- DAO, address discovery, multisig, large histories, crash points and post-import reorgs need direct candidate coverage before any product claim.
