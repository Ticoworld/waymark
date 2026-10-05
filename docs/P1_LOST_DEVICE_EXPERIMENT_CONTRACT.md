# P1 — Lost-device experiment contract

Date: 2026-10-05. Proposal for PM review. **Not implemented and not executed.**

Question: **Does a boring, same-version, wallet-owned backup of approved non-secret state already solve the recovery job?**

Exactly two arms: A (normal correct recovery) and B (same-version state restore). Corruption/network/version rejection checks belong to B's acceptance checks, not extra performance arms. D2, cloud backup, production wallets, PRs and grant work are excluded.

Read P1_CURRENT_POCKET_RECOVERY_MAP.md first. That document defines the source-backed storage/security boundary. Source pin for both arms: Pocket v1.8.5, b28979de744798ffb75367b031d4871ec3af1a12. Embedded LC 0.5.4, exact vendored tree 3ac3e0ce1f4e46897d188b76c5b841b9097fa506; Room 17 / identityHash 091b40f9618fee3fc8032ff01255a9a4.

## Prerequisites and scope freeze

- Use a newly designated disposable emulator environment. Do not install over or inspect the visible physical phone's wallet. Existing AVDs are not automatically disposable; create/designate new instances only after PM approval.
- Build one debuggable APK from the exact unmodified release source for both arms, with x86_64 enabled where needed. Record APK/SO hashes, ABI, Android API, signing/build type and source status. A debug-from-release-source result is not a measurement of the signed public release APK.
- Same emulator resources, network, peers/configuration policy and foreground/background settings for both arms. Select the test network before recovery/state placement. Use ordinary local light-client verification in both.
- New disposable TESTNET mnemonic family, empty passphrase, accounts 0 and 1. Never use production funds or existing evidence keys/stores.
- Phrase is retained independently through normal key-recovery practice before loss; it is not part of the H02 package or public evidence. The experiment does not test recovering a phrase from a lost phone.
- A future test-only helper must prove authorized access to an unmodified debug app sandbox, selected SQL export, ID mapping, staged import and read-only observations. No such helper exists in WO-1.
- Package state is trusted-self state. This is not an untrusted snapshot or proof-of-historical-completeness experiment.
- Establish a usable build/access path before funding the disposable fixture. Current environment gaps are in P1_ENVIRONMENT_READINESS.md.

## Fixture, coverage and authority

Use one parent WalletEntity at m/44'/309'/0'/0/0 and its normal account-1 sub-account at m/44'/309'/1'/0/0. Each must have at least one populated exact lock Script. Set ALL_WALLETS so both fit below the three-owned-wallet cap. Do not add chain-axis funded addresses in this first fixture; the app's normal discovery candidates remain present and their work must be recorded.

For a clean source/destination comparison, initialize the source mnemonic through normal import as well, so public discovery bookkeeping is not silently absent on source but created on destination. Create/restore account 1 normally and preserve its real state transitions. Do not mark unused candidates EMPTY, delete them or move cursors forward to make B fast.

Declare a per-Script start B_s at/before the earliest relevant funding/DAO deposit, including predecessor transactions needed to value later inputs. Choose the narrowest correct supported start for the known fixture, using CUSTOM block height (positive) or FULL_HISTORY when needed. The UI's "specific date" is actually a height input. RECENT is acceptable only if it truly covers all fixture history. Do not choose from-tip as a recovery control.

The source must have independently reconstructed fixture state through a confirmed boundary H before package creation. Record:
- Network name and genesis hash, H and H's canonical hash.
- Full packed Script/code_hash/hash_type/args plus role for both owned Scripts, their paths, source account relationships and actual native registrations.
- B_s, native scanned height, Room progress, actual candidate states and registeredFromBlock values.
- Exact expected live-cell outpoints, capacities and all fixture transactions in declared coverage.
- One confirmed DAO deposit D, preferably on account 1, with required original deposit transaction/header facts.
- Ordinary live cell U at H, separate from D, which will be spent after H.
- No unresolved DAO withdraw/unlock, pending broadcast, failed retry intent, or in-memory reservation at capture. Confirm these conditions rather than deleting records to obtain them.

Fix capture state H using a stopped, coherent source snapshot; if the native store advances during capture, do not mislabel it H. Reacquire a boundary or record actual per-Script boundaries. Reject a fixture snapshot whose claimed H is beyond some required Script's materialized state.

After packaging, make source installation unavailable for all destination recovery and validation. This means no source filesystem mounts, source emulator access, source RPC or source queries. Keep it offline/sealed for preservation rather than deleting evidence. Store only the already approved non-secret package and public fixture/oracle record in the destination workflow. Record the loss-simulation time.

Generate post-H activity with a separately controlled disposable fixture actor, never by consulting the unavailable source installation:
1. Spend ordinary cell U; record its consuming transaction and new output/change outpoints.
2. Add a new incoming cell to the other Script.
3. Commit DAO phase-1 withdrawal of D, yielding its withdrawing DAO cell. This exercises a stale DAO transition without waiting for an entire 180-epoch unlock cycle.
4. Stop further fixture activity and choose a confirmed completion target F > H after these transactions.

Fixture actor credentials, if needed to authorize the post-H spends, are maintained separately through normal disposable-key handling; no recovery secret enters a package, script or result artifact. No claim is made that source-device loss prevents someone with a separately retained seed from signing.

A pinned full node/reference fixture ledger is the test oracle, not a data source used to accelerate either recovery arm. Record its network, tip/hash, transaction bodies/statuses and exact outpoints. Both arms must use the same final fixture events and confirmed target F. If F is reorganized, invalidate/re-baseline the comparison; do not count a mismatch as speed.

Public chain tips may advance between runs. Require both Scripts through F and record each actual verified tip. Compare normalized fixture state at F and verify DAO compensation/maturity against each observed tip's authenticated header/epoch. Do not require a constant numerical DAO reward across different tips.

## CONTROL A — Normal correct recovery

1. Fresh disposable installation with no source native store, Room rows, prior wallet prefs, emulator snapshot or recovered verifier cache.
2. Start wall-clock measurement before first launch/key recovery on the prepared fresh installation. Record installation/provisioning time separately and report it too.
3. Select TESTNET normally. Restore phrase through supported UI, authorize destination Keystore/PIN setup and choose B_s coverage explicitly. Record the initial RECENT registration and chosen-mode resync.
4. Recover account 1 using the normal supported sub-account flow. A known account index can be recreated through Add sub-account, or through the normal found-account banner; preregister which route will be used in both arms. Use the same known public account plan for both. After manual recreation, ensure the historical sync choice is set; NEW_WALLET for a recovered funded sub-account is not correct.
5. Allow ordinary local reconstruction. No native-store injection, H02 state package, historical-cache seeding or D2 operation.
6. Let balance/activity/DAO views reconcile. Exercise account switching and collect exhaustive read-only observations.
7. At apparent readiness, evaluate EVERY acceptance predicate below. Stop the recovery timer only when all initial predicates hold through F.
8. Perform the required process restart and recheck; report restart validation time and total time through persistent acceptance as the main end-to-end result.

Do not prewarm A's light-client chain state. Do not reuse source emulator snapshots that contain keys, UUIDs, Keystore objects or native history. OS-only prepared emulator templates must be identical for both arms.

## CANDIDATE B — Same-version wallet-owned state restore

Preparation before loss (reported separately from destination restore timing):
1. Source sync reaches H with the approved fixture.
2. Establish the stopped consistency boundary from the recovery map.
3. Create and validate the off-device package BEFORE source loss. No native+Room blanket tar/copy.
4. Retain package in access-controlled local host storage and an independently trusted package digest/provenance record. Do not build cloud storage or invent a production encryption protocol.

Destination, timed:
1. Fresh disposable installation identical to A. Start the same clock before first launch/key recovery.
2. Select TESTNET, recover phrase, destination credentials and both account keys through normal supported flows; choose the same coverage policy. Let the initial import flow finish. These normal flows can start native work before staging; record that work/time.
3. Force-stop the whole package and verify no writers. Do not use a UI service toggle or nativeStop as the only barrier.
4. Preflight the package entirely before changing destination wallet state: trusted digest, size/content checks, exact version/profile, network/genesis, structural integrity, required members, consistent Script coverage/progress and identity match.
5. Build the source-to-destination UUID map using the freshly derived full Script/path/parent identity. All destination account keys must already exist under destination UUIDs. Restore allowed public metadata/references using that mapping. Do not import or rewrite key_material or source auth state.
6. Stage the coherent native snapshot plus approved app state as one recoverable set. Preserve destination security state. Guard against stale target WAL. Do not launch with only half the set applied.
7. Restart Pocket normally. Regenerate peer identity, runtime maps and background machinery. Do not explicitly resync or edit cursors to hide a replay. Log actual Script registration decisions and any candidate rewind.
8. Reconstruct omitted app caches from native/normal peer data. Catch up all post-H events through F.
9. Run the same complete acceptance and restart checks as A. All validation, staging, replay and user interactions count in B's end-to-end timing.

### Approved first-package contents

- Consolidated native SQLite store for TESTNET, containing the same-version verified source chain/derived data.
- Explicit public account/parent/derivation/Script map and non-secret labels required by the fixture.
- Remappable sync_progress and genuine sub_account_candidates rows.
- Selected per-account sync preferences, network and strategy. Preserve destination security/migration state.
- Confirmed history records as optional stale hints, with their wallet associations translated; never pending/local signing intent.
- Manifest: experiment/package version, exact app commit and build digest, ABI, LC tree, Room version/identity, network/genesis, H/hash, per-Script B_s/actual cursor, content lengths/digests, declared omissions and capture method.

Do not include raw Room database pages/WAL/SHM, key_material, PNBK files, secret prefs, peer identity, pending signed transactions, logs or auth state. Export selected Room rows in the stopped app sandbox into a new clean logical representation. Deleting secrets from a copied raw Room file is not sufficient.

The first candidate deliberately rebuilds balance_cache, header_cache and dao_cells. Native state should contain the original DAO/transaction/header evidence. If normal app reconstruction cannot recover an omitted cache correctly from complete native coverage, that is a result requiring PM review, not permission to silently import authoritative-looking stale cache.

Contacts/custom notes are outside the first fixture. Pending actions at H are a fixture exclusion, not a claim that general wallet recovery can discard them. The manifest must make this bounded scope explicit.

## Acceptance — fast incomplete recovery is FAIL

| Predicate | Required observation in BOTH arms |
|---|---|
| Wallet/account identity | Correct parent/sub-account path and accountIndex, both exact Scripts and network addresses; active selection works; destination-generated UUIDs consistently referenced; no duplicate source UUID wallet or orphan secret-key row. Normal signing readiness/authentication works for each account without exposing keys; any proof-of-control observation is local/disposable and not an extra chain-speed arm. |
| Two populated Scripts | Both owned Scripts reconstructed and registered; not merely primary account balance. Account switching does not unregister/lose the other under the declared strategy. All actual candidate statuses/coverage retained and recorded. |
| Exact live cells | Exhaustive paginated outpoint set (tx_hash,index) per Script equals oracle at the target state, including type/data where relevant. No first-page-only comparison. |
| Capacity/balances | Exact integer shannons per live outpoint and correct total/spendable/DAO accounting. Aggregation and returned change agree with fixture transactions, not rounded CKB display alone. |
| History | Every fixture transaction in declared [B_s,F] coverage, correct wallet association, direction and net amount, required predecessor inputs, status and block identity. App activity and native data agree. No claim about pre-B_s history. |
| DAO | D recognized through H; post-H withdrawal consumes it and creates the correct withdrawing position. Deposit and withdrawal headers/epochs/capacity/reward/status agree with canonical data. No duplicate old deposit, phantom spendable balance or stale out-of-window card passed as live. Full phase-2 unlock is not qualified by this fixture. |
| Stale snapshot | U is live in the H package and absent from live cells after its confirmed post-H spend; consuming tx and replacement outputs present. The new incoming cell is present on the other Script. |
| Progress | Every required owned Script's native cursor and Room progress reaches F; verified tip/hash recorded; no unexplained high Room cursor, unresolved relevant matched work, incomplete query page or false initial_sync_completed shortcut. |
| Registration/replay accounting | Record before/after Script set and cursors, ALL/PARTIAL calls and observed historical replay. Replaying is not automatically incorrect, but its full cost counts. Do not suppress candidate work to manufacture a fast B. |
| Restart persistence | Force-stop/reopen disposable app after initial acceptance; recheck identities, cells, histories, DAO and per-Script progress. No fresh unexpected full reconstruction hidden outside the timing. Record any repeated work/time. |
| Source independence | No source-device consultation after declared loss time. Package and key-recovery material already existed elsewhere beforehand. New device's Keystore/peer identity are its own. |
| Corruption refusal (B) | Truncated/member-missing/bit-flipped package rejected BEFORE live state mutation. Bad schema/identity/cursor association also refused. Destination key/security state and prior recoverable baseline unchanged. |
| Wrong-network refusal (B) | Network label AND native stored genesis checked against selected test network; deliberately mislabeled/wrong-genesis package rejected before native start. Native panic is not acceptable refusal. |
| Unsupported-version refusal (B) | App build/profile/Room or package-version mismatch rejected without partial application. Safe fallback is normal recovery A, explicitly reported as fallback, never scored as a fast successful B. |
| No secret transfer (B) | Allowlist audit of every logical column and archive member, no raw Room pages/sidecars or encrypted key blobs. No source secret member can be admitted merely because its bytes are ciphertext. |
| Package activation consistency (B) | Failed/preflight-invalid restore leaves destination keys and baseline intact. An interrupted staged application must not auto-launch a mixed state; either safely complete or return to normal recovery. |

The observer must see exact native/app state without modifying it or altering registration policy. If only UI screenshots are available, the run cannot satisfy exact-state acceptance; do not soften the contract.

Current Room transaction primary key is txHash alone, and DAO rows are keyed by outpoint, with wallet/network as other fields. To keep this first experiment interpretable, use distinct funding transactions for each account and no transaction deliberately shared between the two fixture account histories. This is a declared scope limit, not proof of general shared-transaction/multi-network cache correctness.

## Measurement and result interpretation

No speed threshold is set.

Use a monotonic clock and record at least:
- Fresh-install/provision time separately.
- First launch, key-recovery start/complete and account setup.
- First native registration and chosen coverage.
- For B: package read/check, extraction, UUID mapping, staging, restart and catch-up.
- First correct native state, first correct app state, all-predicate acceptance.
- Restart and persistent acceptance.
- Package creation/capture cost, size and storage cost separately, before loss.
- Actual downloaded/scanned work where observable, memory/storage footprint and failures.

Main recovery time is fresh-first-launch through persistent acceptance, including normal key entry/authentication and all B restore operations. Also report machine-only intervals, so human entry time does not hide reconstruction differences. No subtraction of inconvenient replay, cache rebuild or validation time. No precomputed expected values injected into Pocket.

Run the first paired trial with the same public fixture facts and comparable clean installations. Record order and peer/network conditions. One paired result is a feasibility result, not a stable production speed estimate. Repeat/reorder only in a later PM-approved measurement plan if variability or the result warrants it.

Interpretation:
- B complete and faster: the simpler same-version wallet-owned approach survives. It supports a wallet feature/test-helper direction, not independent library adoption or a grant conclusion.
- B complete but similar/slower: fixed overhead, candidate replay, chain catch-up or cache reconstruction may erase the gain. Report the breakdown; do not add D2 immediately.
- B incomplete: fail, irrespective of time. Identify whether the cause is package omission/mapping, current app behavior, unavailable native evidence, tooling or a coverage mistake.
- A incomplete: the control is invalid. Diagnose correct current recovery/fixture coverage before comparing.
- B needs production behavioral changes to pass: stop and report that new finding to PM. WO-1's source-derived no-production-change expectation was not a runtime guarantee.
- Safe fallback succeeds: useful fail-closed behavior, but does not count as B successfully restoring state.

## Stop boundary

WO-1 provides this contract only. No fixture has been funded, no keys generated, no helper/export/import implemented and no app installed or synchronized. Next authority is PM review of the map, delta, contract and readiness report.

D2 does not enter WO-2 by default. First determine whether same-version state restoration is correct and useful. No production code, package crypto/cloud service, cross-version format, multi-wallet product or upstream patch is authorized by this contract.
