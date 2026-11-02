# Waymark Neuron Technical Handoff

Date: 2 November 2026

## Purpose

This handoff summarizes the completed Waymark recovery research through WO07-R12 for a future technical review with Neuron maintainers. It is not a request to merge an implementation. No upstream contact or publication has occurred.

## Recovery problem

Neuron mnemonic recovery restores wallet ownership and derives addresses, then uses a user-selected Light Client start height and normal Script scanning to reconstruct application history. A transferred Script checkpoint alone is unsafe: an empty destination application database does not contain the transactions, inputs, outputs, Cell relationships, and DAO references represented by that checkpoint.

The research asks whether a destination can reuse previously completed Light Client Script discovery, then feed its historical results through Neuron's existing transaction cache, queue, and persistor. The intended benefit would be less destination-side filtering and shorter recovery while preserving ordinary Neuron ownership, chain validation, and app reconstruction.

## Pocket Node results and limits

The original Pocket comparison reported about 30 minutes between its Normal and Full arms, but Normal already used the same historical floors and recovered both known accounts. Full restored native state plus settled discovery/progress metadata; transaction, balance, header, and DAO caches were rebuilt in both arms. The original difference cannot be attributed to Lite or to native-state reuse alone.

A later controlled TESTNET comparison had all three arms pass exact-state acceptance and cold restart. The Lite-equivalent fresh-native arm took 35m23.6s to exact capture; the Full package arm took 10m52.6s, an observed 24m31.0s total difference. However, Full also restored completed discovery metadata. A diagnostic native-reuse arm with fresh discovery took 43m03.7s overall and about 34 minutes from registration to exact state, with discovery passes still required. The experiment points to settled discovery as a major source of the Full arm's benefit; it did not isolate native-store-only savings.

These were single, sequential, fixture-specific runs with changing peers/tips and manual capture delays. Height spans are not work counts. Results do not establish representative recovery performance or generalize from Pocket to Neuron. See [Lite/full attribution](lite-full-attribution.md) and the retained [Pocket evidence](evidence.md).

## Neuron findings: R9-R12

Target versions were Neuron v0.204.1 and its bundled CKB Light Client v0.5.4. The examined Neuron source pin is `a926e3383d3a3e305b3bde7d233474515ef01a2e`; the Light Client source pin is `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`.

- **R9, ordinary sync:** A genuine disposable Neuron TESTNET wallet owned one confirmed receive. Neuron's actual `LightSynchronizer` found it, cached it under the real wallet UUID before advancing discovery progress, and its Queue/persistor saved the transaction and live output. This was ordinary scan from H-1, not transferred-state recovery.
- **R10, native copy:** A quiescent full v0.5.4 RocksDB store copy preserved the Script registration, cursor, and transaction query across another process and restart. It inherited chain state from the source and did not prove app recovery or independent authority. The reports record inconsistent store byte totals, so the approximately 2 MB footprint is not a precise benchmark.
- **R11, application recovery:** A disposable clone retained genuine wallet/address identity but had its transaction/cache/progress rows reset. Neuron's actual initializer, grouped RPC, cache, Queue, and persistor rebuilt one known receive from a full native-store copy. The app progress rows were initialized before attaching the store. The known transaction/output/cache survived SQLite reopen; the native client survived cold restart. This was simulated clean app state, not mnemonic restore, selective D2 import, or complete wallet recovery.
- **R12, pending cache:** A disposable state reconstructed from the genuine R11 cache row, with app transaction/output rows absent and the cache unprocessed, was reopened in a new Node process. Neuron's packaged synchronization loop and Queue resumed the row, fetched the real transaction, persisted one output, marked the cache processed, and matched after database reopen. This was a constructed interruption state, not process termination at the original write boundary.

The older D2 line also produced useful integration evidence: an exact-Script artifact imported into a v0.5.4 RocksDB store and was returned by the ordinary RPC; proof-backed `fetch_header` filled the historical header mappings; Neuron's actual Queue/persistor processed eight real TESTNET transactions from the Pocket fixture. That Script had no established Neuron wallet ownership. It is pipeline compatibility evidence, not wallet recovery. The v0.5.4 D2 adapter remains destination-import-only.

## Two-phase initialization and cursor behavior

Neuron's `LightSynchronizer.synchronize()` awaits transaction-cache insertion before updating per-Script `SyncProgress.syncedBlockNumber`. The Queue persists transaction/input/output state, handles address generation, and only then marks cache rows processed. `localSavedBlockNumber` therefore trails discovery progress and must not be set equal to the native cursor as a shortcut.

R11 tested both startup orders. If the transferred native store was attached while the app had no matching progress rows, Neuron sent partial `set_scripts` registrations for 90 Scripts, resetting the owned Script cursor to its wallet start height and repeating historical filtering. When Neuron first created the legitimate progress rows through its normal initializer, then the quiescent native store was attached, the next initializer issued empty Script registration/deletion calls and preserved the transferred cursor. Neuron then queried the imported range and reconstructed the transaction through its existing path.

The demonstrated order is therefore: establish wallet/address identity and real app progress; stop both workers; stage, verify, and attach a compatible native store; restart Neuron; replay results through its cache and queue; wait for persistence and validation before reporting recovery ready. R11/R12 did not implement a durable coordinator, atomic install/rollback, phase journal, or full crash matrix. A stale native cursor below the app checkpoint caused Neuron to lower discovery progress in an excluded diagnostic run, so mismatched snapshots must be rejected or explicitly fall back to ordinary scanning.

## What full-store copying accomplishes

For the tested one-Script case, copying the complete v0.5.4 native store carried prior Script-filter results and the cursor. With Neuron's matching progress rows present, the app queried those results and rebuilt its own history through the normal persistence pipeline. No Neuron application database or signing key was transferred by the recovery step.

This does not validate all copied historical chain state independently, prove that the source omitted no Script matches, or cover reorgs. A file hash detects transfer corruption, not source honesty or completeness. A full store also includes other registered Scripts, chain/header data, global cursors, and privacy-sensitive activity. Cross-version portability, representative size, and multi-wallet behavior remain untested.

## Difference from a cold backup

Neuron's wallet-backup UI exports the encrypted keystore JSON; it is not a complete backup of application and Light Client databases. A complete cold backup would need a quiescent, version-compatible copy of both the Neuron profile/application state and native Light Client data, with consistent shutdown and restore behavior. This complete profile-copy procedure was not tested.

Waymark's tested path instead relies on ordinary wallet recovery to establish ownership, transfers only Light Client native state, and asks Neuron to rebuild application state. It can avoid copying Neuron's app database, but it still transports broad native chain and Script data. The experiments did not show that this is smaller, safer, faster, or easier than a complete cold backup.

## Trust, privacy, and safety limits

- The recovery source is trusted to provide complete Script results. An artifact digest or matching chain anchor does not prove no matching transactions were omitted.
- The R8 wallet was receive-only; its signing credentials are unavailable. No wallet-owned spend or spend recovery was tested.
- The R11 fixture contains one receive near its selected start height. Complete history, general balance reconstruction, DAO recovery, and broad Cell-spend correctness are unproven.
- R12 resumed a pending-cache state, but did not inject process kills during native installation, cache writes, persistor commits, or processed-marker updates. Duplicate persistence after a crash between database commit and cache completion remains untested.
- Cursor preservation depends on initialization order and matching wallet Script/progress records. A production path needs an exclusive worker barrier, durable phase marker, atomic staged install/rollback, consistency checks, pending-cache drain, and ordinary-scan fallback.
- No matched Neuron recovery benchmark exists. Historical filtering reuse was observed for the tested Script range; CPU, network, total elapsed savings, and benefit over cold backup were not measured.

## Product hypothesis and decision

The strongest remaining hypothesis is: **users with long Neuron Light Client histories may value a portable, keyless synchronization snapshot that lets a freshly mnemonic-restored installation rebuild app state without repeating historical Script filtering, especially when a complete profile backup is unavailable or undesirable.** The tests establish technical plausibility for one receive, not user demand or advantage over a full profile backup.

Before another engineering experiment, clarify whether users actually face this recovery case and what Neuron currently recommends. There are no demonstrated product blockers requiring a new architecture yet; the gaps are crash-safety evidence, representative performance evidence, and an unvalidated user problem.

Questions for Yukang:

1. Which failure is the intended target: lost device, corrupted app database, reinstall, migration to another computer, or routine recovery on a second device?
2. What recovery procedure does Neuron currently recommend, and is a consistent full-profile/native-data backup already supported or acceptable?
3. Do users need only mnemonic-based recovery, or do they want history and balances ready sooner on a fresh installation?
4. Would users transfer all Light Client activity in a full-store snapshot, or is Script-scoped privacy materially important?
5. Which release/version compatibility, reorg handling, source trust, and completeness guarantees would Neuron require before accepting a portable synchronization snapshot?
6. What measurable recovery-time or support burden would make this useful enough to maintain?
7. Can Neuron provide a supported lifecycle barrier to create wallet progress before attaching native state, or is that ordering incompatible with current startup architecture?

## Smallest decisive comparison

Only proceed if the user problem is confirmed. Use one recoverable disposable wallet with separated confirmed receives and a wallet-owned spend, a large enough history to make filtering measurable, and one pinned Neuron/Light Client version. Compare three independent destinations at the same canonical block hash:

1. Ordinary mnemonic restore with Neuron's supported historical start height.
2. A complete, quiescent Neuron profile plus native-store cold backup restore.
3. Two-phase native-store transfer followed by Neuron app reconstruction.

Record total preparation and restore time, bytes, historical filter work, application reconstruction, chain catch-up, validation, and restart/failure behavior. Compare exact transaction history, inputs/outputs, live/spent Cells, balances and relevant DAO state. Count export/copy, restore and verification costs. A Waymark benefit is established only if it materially improves on both alternatives without weakening trust or correctness. Keep the existing Pocket/D2 evidence as separate research; do not extrapolate its timing to Neuron.

## Research index

- [WO04 feasibility](WO04_NEURON_RECOVERY_FEASIBILITY.md)
- [WO05 safe-recovery decision](WO05_NEURON_SAFE_RECOVERY_DECISION.md)
- [WO06 architecture decision](WO06_DECISION_AND_NEXT_WORK.md)
- [WO07 initial D2 result](WO07_NEURON_D2_REPLAY_RESULT.md)
- [WO07-R1 through R12 reports](WO07_R1_INDEPENDENT_AUTHORITY_AND_REPLAY.md), [R3](WO07_R3_NATIVE_ROCKSDB_ADAPTER.md), [R7](WO07_R7_VERIFIED_HEADER_AND_REAL_QUEUE.md), [R9](WO07_R9_REAL_NEURON_RECOVERY.md), [R10](WO07_R10_CROSS_DEVICE_HANDOFF.md), [R11](WO07_R11_NEURON_APPLICATION_RECOVERY.md), [R12](WO07_R12_RECOVERY_SAFETY_VALUE.md)
- Reproducible headless experiments: `tools/wo07-r5` through `tools/wo07-r12`.
