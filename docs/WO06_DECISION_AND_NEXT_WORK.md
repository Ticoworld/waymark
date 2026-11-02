# WO06 Decision and Next Work

Date: 30 October 2026

## Decision

**B. PROMISING NEW DIRECTION.** Proceed to one controlled Neuron Light Client proof using exact-Script CKB Script Port/D2 handoff plus Neuron's ordinary transaction replay. Do not start production integration or claim complete/trustless recovery.

The proposal is not to transfer a Neuron sync height into an empty wallet database. It is to transfer one exact Script's indexed Light Client results and transaction closure, then use Neuron's own synchronization queue to rebuild its application database before advancing Neuron's app-level checkpoint.

## Why the answer changed from WO05

WO05 rejected checkpoint-only transfer because it skips historical transaction records required for balances, live Cells, history and DAO reconstruction. D2 is a different candidate: the artifact includes Script-derived indexes and referenced transactions, and the destination binds its handoff height/hash to its own chain state. Existing Pocket evidence exercised import, H+1 continuation, application rebuild and restart for one real testnet Script.

That is enough to justify an integration proof, but not enough to establish Neuron compatibility, history completeness or net user benefit. D2 trusts its source to report the exact Script view/cursor honestly. A self-hash is not authentication, and a matching block hash does not prove there were no omitted Script matches.

## Minimum implementation boundary for the proof

- Use one released Neuron version and its exact bundled CKB Light Client storage profile.
- Use one disposable TESTNET mnemonic wallet with at least two owned lock Scripts if Neuron's address/account model requires them; add a DAO deposit/withdraw cycle if the test fixture supports it.
- Export one D2 artifact per required exact Script/role from a quiescent source. Keep discovery and any unexported Scripts on Neuron's normal scan path.
- Restore the mnemonic on an independent fresh destination with fresh destination password/device security.
- Validate exact Script identity, role, genesis, H and H hash against destination authority; import through exclusive/atomic native storage lifecycle; close/reopen Light Client.
- Keep Neuron's app sync progress below H. Query the imported historical Script view via Neuron Light RPC, replay every result through Neuron's transaction cache and existing queue/persistor, and drain all cache rows before committing app progress through H.
- Continue ordinary sync after H+1. Do not copy Neuron SQLite, Room-equivalent app state, signing keys, keystore files or OS key material.

If there is no supported way to replay imported historical results through Neuron's existing persistence path without changing the imported native cursor or scanning again, stop. Never solve that by setting Neuron `syncedBlockNumber=H` on an empty application database.

## Smallest decisive experiment

Compare two independently initialized destinations using the same Neuron release, same disposable TESTNET wallet/Scripts, same fixed target height/hash and comparable destination security:

1. **Baseline:** normal Neuron mnemonic restore with its supported historical start-height control. Let its Light Client scan and let Neuron reconstruct the app DB normally.
2. **Candidate:** same restore on a clean destination, import the exact-Script D2 artifact(s), replay the imported results through Neuron's normal queue, catch up from H+1, and rebuild any unexported scripts normally.

Measure source export, artifact size, destination LC startup/readiness, historical Script filtering, app `get_transactions` replay, transaction/header/previous-output fetch, DB persistence, catch-up, verification, and time to exact usable state separately. Report end-to-end elapsed including export/import/verification. Repeat or randomize arm order to control changing TESTNET peers/tip and warm caches.

At one identical destination-recognized canonical block hash, compare:

- derived owned Scripts and addresses;
- complete transaction hash/history sets and input/output relations;
- live Cells and balances;
- DAO deposit/withdraw position and claimable state if present;
- Neuron cache processed state and per-Script/app progress consistency.

Cold-restart each destination and repeat all checks. Include negative tests for wrong network/genesis, wrong Script/role, tampered artifact, omitted historical transaction, stale H/hash, interrupted replay, and a bounded reorg where feasible. The omission test should demonstrate the trust limit: D2 validation alone cannot detect an internally consistent source omission; the test harness's independent oracle must detect it.

## Pass/fail gate

**Pass to further engineering only if** the candidate reaches exact state after restart, does not skip Neuron app reconstruction, processes H+1 normally, detects injected corruption/identity/chain mismatches, and reduces total time or measurable expensive Light Client work after counting export, import and validation. Candidate replay must not be counted as a saving when the baseline incurred the same Neuron app reconstruction.

**Stop this direction if** imported history cannot be queried from the pinned Light Client, Neuron needs to re-filter the same historical range to establish correctness, there is no meaningful reduction beyond existing start-height controls, or any exact history/Cell/DAO comparison fails. Do not broaden the test into full-node recovery: D2 does not replace full-node sync or chain-wide indexer sync.

## Trust and product limits

This proof uses a trusted-self source model: the user intentionally transfers public but privacy-sensitive Script activity from their own previously used installation. It must not be advertised as protection against a compromised source or a proof of complete history. Source authentication (for example an authenticated transfer or user-controlled encryption/MAC) is separate from wallet signing keys and would be needed for a product transport. The current unkeyed digest is only a corruption check.

The candidate is Light Client only. Neuron still owns key derivation/security, wallet discovery, app transaction database, DAO/UI caches and normal chain authority. Full-node chain synchronization and its chain-wide indexer remain separate work and are not accelerated by this exact-Script transfer.

## Source pins and evidence

- Neuron `develop`: `a926e3383d3a3e305b3bde7d233474515ef01a2e`; RC: `484a46dadde2a0adfd7975d0159be898b199cf80`; release baseline v0.204.1: `d3a7467d218e4b6f777326682a83fec802669c00`.
- CKB Script Port/D2 examined: `9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835`.
- Neuron range query then cache/progress order: [light-synchronizer.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/light-synchronizer.ts#L91).
- Neuron ordinary transaction persistence: [queue.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/block-sync-renderer/sync/queue.ts#L124), [transaction-persistor.ts](https://github.com/nervosnetwork/neuron/blob/a926e3383d3a3e305b3bde7d233474515ef01a2e/packages/neuron-wallet/src/services/tx/transaction-persistor.ts#L198).
- D2 artifact, authority and trust limits: [D2 v1 guide](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/docs/D2_V1.md).
- Pocket reference evidence and boundaries: [G3-1R1 evidence](https://github.com/Ticoworld/ckb-script-port/blob/9e8d6f6b35f292bfb54cf9500260f3a0c6aa7835/docs/G3_1R1_POCKET_EXECUTION_EVIDENCE.md).
- Protocol comparison: [CKB RFC 0045](https://github.com/nervosnetwork/rfcs/blob/master/rfcs/0045-client-block-filter/0045-client-block-filter.md), [Bitcoin Core AssumeUTXO design](https://github.com/bitcoin/bitcoin/blob/master/doc/design/assumeutxo.md).
- Historical header verification proposal: [CKB Light Client PR #297](https://github.com/nervosnetwork/ckb-light-client/pull/297), open at research time and not a completeness proof.

## Exact next work order

**WO07: Neuron D2 Replay Feasibility Spike.** Build no product feature. In an isolated disposable TESTNET harness, first establish that the pinned Neuron Light Client can import one D2 exact-Script artifact, expose its historical `get_transactions` results to Neuron's existing cache/queue, and complete replay without setting app progress ahead of persisted records. Compare this candidate against Neuron's normal supported restore at a common block and run exact state plus restart checks. If this first capability check fails or no expensive Light Client filtering is saved, stop Neuron Waymark. Only a clean pass with a measurable end-to-end advantage should authorize a separate production design review.
