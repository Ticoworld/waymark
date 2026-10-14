# Waymark Lite and Full: recovery timings and discovery checks

Measured on 14 October 2026, using Pocket 1.8.5 on the same Android phone and disposable TESTNET wallet. This report answers the data and discovery questions in [Pocket #560](https://github.com/RaheemJnr/pocket-node/issues/560).

**Repeated checks of empty account slots caused much of the delay.** Active accounts and account discovery scanned together at first. Both active accounts had scanned beyond our target block after about **14m28s**. Discovery finished about **18m50s later**. Within that wait, four account slots that turned out empty needed another historical scan lasting about **16 minutes**.

The full wallet state, including Pocket's history and DAO information, was only proven correct in the final saved capture. We have not measured how fast Lite would be if it reused completed discovery checks, or how much extra benefit Full would then provide.

## What we compared

The **native store** is the CKB light client's local database. It holds indexed transactions, live Cells (unspent outputs), headers, checkpoints and scan progress. Pocket also has its own app database, built with Room, and caches for history, balances and DAO information.

**Discovery** means checking derived account or address slots for activity. A candidate is one slot being checked. `PENDING` means its result is unresolved, `EMPTY` means no activity was found over the checked range, and `RESTORED` means it is already an owned account. A **Script** identifies the lock being scanned. Registering a Script tells the light client what to scan and where to start.

| Run | Starting state | Time to the final checked capture |
| --- | --- | ---: |
| **B — Lite-like** | Fresh native store and Pocket state. Normal key recovery, accounts 0/1 and their known historical start heights. No saved discovery results or completion flags. | **35m23.6s** (35m24s) |
| **C — Full saved state** | Normal key recovery, then the original native snapshot plus selected discovery, progress and sync settings. | **10m52.6s** (10m53s) |
| **D — native-store reuse, fresh discovery** | The same native snapshot, but discovery results and safety/completion flags started fresh. Only the small amount of app progress bookkeeping needed to resume that store was set. | **43m03.7s** (43m04s) |

These were **B, C and D**. There was no new A run. Each started with Pocket cleared, recovered the same keys normally and created fresh destination security. Source signing secrets and Android Keystore material were never imported. All three passed the exact wallet-state checks and passed again after Pocket was fully stopped and restarted. No outgoing transaction was made in these runs.

B used the old build's CUSTOM start-height setting and normal account creation to supply Lite-like information. It imported no saved state. It does not measure the current Lite implementation's UI, height rounding or safety margin. Account 1 was already inside the old build's normal discovery window.

C restored 51 discovery rows: 50 `EMPTY` and one `RESTORED`, along with selected progress/settings, including completed-initial-sync flags. **It did not copy Pocket's transaction, balance, header or DAO caches.** Those were rebuilt normally. D reused the exact same native bytes with fresh discovery. D is useful for comparison, but is not a perfectly isolated measure of native-store benefit.

## B: where the 35m24s went

These three intervals do not overlap. The detailed values explain small differences when rounded to whole seconds.

| Interval | Observed time | What was happening |
| --- | ---: | --- |
| Launch → both active accounts scanned beyond target | **14m27.8s** | Setup, active-account syncing and the first discovery scan happened together. Their separate costs are unknown. |
| Active accounts beyond target → discovery finished | **18m50.5s** | Pocket waited for discovery, including the remaining registrations, a normal restart and a second historical scan. |
| Discovery finished → final checked capture | **2m05.3s** | Normal app/history/DAO refresh, observation and capture. These costs were not timed separately. |

Within the 18m50.5s wait, 2m44.9s passed before the second batch's logged registration. The next 16m05.7s ended at the first observation showing all empty checks complete. From the last pending observation, that second batch finished roughly **15m39s–16m06s** after registration, with additional uncertainty from observation delays and device/host clocks.

This is elapsed time associated with discovery. It is not a measurement of pure CPU time, nor proof that a Lite change would save all of it. The final app refresh was deliberately performed after discovery was ready.

### Active-account data and discovery overlapped

Account 1's native live Cells/history first matched the chain reference at **11m45s**. Account 0's matched at **12m13s**. Neither early match proved that scanning had reached the target block: a sparse wallet can show the expected data before the rest of the range has been checked.

At **14m28s**, both active accounts had scanned to block **22,737,008**, beyond the target **22,736,904**. Both app balances matched too. Account 1's sampled history checks passed, but account 0's app history was still incomplete and the DAO cache was absent in the progress observations. Complete app histories and the DAO position were first proven together in the final capture at **35m23.6s**. The acceptance check for that capture passed about 17 seconds later; reported times stop at capture.

### What the empty-slot checks did

There were **51 candidates**: 41 receiving/change address paths under account 0, plus account indices 1–10. Account 1 was normally recovered and marked `RESTORED`. The other **nine account slots and 41 address paths ended `EMPTY`**.

The first scan included both active accounts and 46 discovery Scripts. It produced 46 `EMPTY` results, leaving four candidates `PENDING`. A normal restart activated those four. The registration rules select the lowest five pending account indices plus all address paths. Those rules and the recorded counts identify the last four as indices 7–10; this is inferred from policy, not a per-path completion log.

The second scan started from **22,368,938**, a height difference of **367,966** to the target. The active accounts resumed from **22,737,011**. Across 35 successive observations during that scan, both active-account scan positions stayed at 22,737,011 while the shared filter scan worked through the older range for the four candidates. Their native live Cells/history and app balances continued to match. The active scan positions moved forward again when discovery caught up; the app refresh still remained.

The initial scan's registration set changed during account setup. Candidate start heights moved from a recent window to 22,369,937, then to 22,368,938 after older history became available. Both main discovery passes used that final floor. The logs do not time any duplicated work caused by those changes or any failed-probe retries separately. Height differences describe the range being scanned; they are not counts of downloaded full blocks.

### Timestamped B observations

All times are **UTC on 14 October 2026**. Elapsed times start at first launch. Regular observations were about 27 seconds apart and read several fields in sequence. These are first-observed times, not exact internal completion timestamps.

| UTC | From launch | Observation |
| --- | ---: | --- |
| 07:01:01.010 | 0 | First launch |
| 07:01:32.533 | 0m31.5s | Initial registration, including discovery, from 22,536,912 |
| 07:02:13.694 | 1m12.7s | Active-account and discovery registration from 22,369,937 |
| 07:03:43.330 onward | 2m42.3s onward | Candidate start height widened to 22,368,938 |
| 07:04:53.006 | 3m52.0s | 50 PENDING, one RESTORED; two active + 46 discovery Scripts registered |
| 07:12:46.379 | 11m45.4s | Account 1 native live Cells/history and app history first match |
| 07:13:13.898 | 12m12.9s | Account 0 native live Cells/history first match |
| 07:15:28.812 | 14m27.8s | Both active accounts beyond target; both app balances match; 50 still PENDING |
| 07:15:55.794 | 14m54.8s | 46 EMPTY, four PENDING, one RESTORED |
| 07:17:54.890 | 16m53.9s | Normal restart begins; no reset or import |
| 07:18:13.677 | 17m12.7s | Four candidates register from 22,368,938; active accounts resume from 22,737,011 |
| 07:18:33.701 | 17m32.7s | Shared filter scan back at 22,368,938; active accounts remain beyond target |
| 07:33:52.479 | 32m51.5s | Four still PENDING; lowest registered scan position 22,734,000 |
| 07:34:19.332 | 33m18.3s | 50 EMPTY, one RESTORED; all scan positions 22,737,129 |
| 07:36:24.589 | 35m23.6s | Final capture proves full checked wallet state, including history and DAO |

The samples around target coverage and empty-result completion put the gap at approximately **18m24s–19m17s**, before allowing for observation delays. About 18m50s is a useful description of the observed wait, not an exact split of engine work.

## What C and D tell us

| From launch | B | C | D |
| --- | ---: | ---: | ---: |
| Relevant active-account registration | 1m12.7s | 4m08.2s | 8m55.8s |
| Both active accounts beyond target, first observed | 14m27.8s | 8m45.6s | 22m18.4s |
| All 50 EMPTY, first observed | 33m18.3s | Already imported; first observation at 4m14.2s | 40m39.6s |
| Final checked capture | 35m23.6s | 10m52.6s | 43m03.7s |
| Registration → final capture | 34m10.9s | 6m44.4s | 34m07.9s |

Registration was logged just before the Java-to-native call (JNI). It was B's first active historical registration, versus C/D's registration at the imported snapshot height. It was not node startup. B's remaining account setup overlapped scanning; C/D completed that setup before import.

C registered only the two active Scripts and avoided the repeated discovery scans. D kept the native snapshot but again checked 46 candidates, then four more. Its first batch showed 46 EMPTY at 08:16:54.666, all 50 showed EMPTY at 08:34:47.034, and its final capture was at 08:37:11.196.

B and D both took about 34 minutes from their stated registration point to final capture. D's authentication/account-creation intervals together took about **4m42s longer** than B/C. Its slower total does not mean native reuse makes recovery slower.

Full finished **24m31.0s earlier than B** in these runs. That saving includes native state, completed discovery and other saved settings. It cannot all be called native-store benefit or empty-discovery benefit. The evidence supports repeated empty discovery as a major delay, but does not show how much native import would add after a Lite improvement.

## What this means for Lite and Full

Saving completed discovery checks in Lite looks worth exploring. It could avoid work without importing a native database. **We have not measured that proposed improvement.** Current Lite's information and Full's combined saved state are different, and these results do not show that one has replaced the other. They also do not establish that native-store import has no benefit or that Full is necessary.

The earlier roughly 60-minute versus 30-minute phone comparison cannot supply the missing split. Both old paths already used the same historical start heights and known accounts. Full also restored completed discovery/progress information. Those old totals included different amounts of signing, restart and audit work. We cannot assign reliable Lite/native percentages to that saving.

### EMPTY needs a coverage boundary

In the tested code, EMPTY requires a registered Script, a transaction probe finding no activity, a scan position within **1,000 blocks** of a known tip, and at least **50,000 blocks** between its recorded start and scan position. An unknown probe result stays PENDING. See the pinned [reconciler](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/SubAccountReconciler.kt) and [registration rules](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/SyncCoordinator.kt).

EMPTY therefore means no activity was found over the checked range. **It does not prove the slot has never had activity.** Older activity can fall before the start height, later activity can arrive, and the near-tip rule allows an unchecked recent gap.

The original snapshot's candidate rows record the derivation path, account index, public Script arguments and minimum registered start. They do **not** record the network, checked-to height/hash or discovery-rule version. Of its 50 EMPTY rows, 45 recorded start 20,451,410 and five recorded 22,368,938. Those values alone cannot establish the network or full range covered by each old result.

Safe reuse would need to tie each result to the right wallet derivation/Script, network, rules, checked range and chain checkpoint, with integrity/authentication checks. Authentication protects the record; it does not prove the source scanned correctly. Older uncovered history, new activity and chain reorganizations still need consideration. The existing rows are not enough to justify skipping all future discovery.

## Setup, limits and open question

| Setting | Value |
| --- | --- |
| Pocket | 1.8.5 / code 27, unchanged commit `b28979de744798ffb75367b031d4871ec3af1a12` |
| Phone | Samsung SM-S9180, Android 16, ARM64, 4 KB memory pages |
| Network and wallet | CKB TESTNET; same disposable fixture, accounts 0/1, separate locks, multiple Scripts, active DAO deposit |
| Account derivation | `m/44'/309'/N'/0/0`, N = 0/1 |
| Historical account starts | Account 0: 22,369,937; account 1: 22,647,000 |
| Snapshot checkpoint, called H2 | 22,652,549; `0x3f96acadbf4ef0d847db36468ca13feb37630fd5a156a5540713897c0dd4e3ee` |
| Common comparison target | 22,736,904; `0xca25de35fb3fdcdbd28e545a935915e2fcb9e029782029f37acd23cf7eac1c6e` |
| Native catch-up range | Target minus H2: 84,355 heights |

Each final capture and restart matched eight / three covered transactions, three live Cells per account, exact ownership/balances and the active DAO position. A known defect in this Pocket version's DAO reward estimate was checked separately and was not fixed. DAO-position acceptance is not a claim that the reward estimate was correct.

These are single sequential runs with sparse wallet history. Peers, tip heights, phone temperature (about 37–43 °C), manual authentication, UI navigation and observation delays varied. The new snapshot needed about 84,000 blocks of catch-up, versus about 3,100 in the old phone comparison. They are not interchangeable timings or benchmark-quality results. The snapshot was trusted research data, not a hardened production importer.

The missing measurement is **fresh native state with only properly scoped completed discovery information restored**, while controlling other settings and checking app state continuously. That would help measure improved Lite's savings and the remaining native-store benefit. It has not been run. This publication adds no experiments or implementation.

## Data and how to check it

The CSVs contain sanitized measurements, not raw logs or database copies. Numeric measurements are unchanged from the prepared evidence packet. Human-readable labels were simplified. The original sealed report and raw evidence remain unchanged in local custody.

| File | Contents |
| --- | --- |
| [arm-summary.csv](arm-summary.csv) | B/C/D launch, registration, target coverage, discovery completion, final capture and restart |
| [b-timeline.csv](b-timeline.csv) | B events and first-observed milestones, with references to original records |
| [b-registrations.csv](b-registrations.csv) | B Script registrations, start heights and counts |
| [progress-observations.csv](progress-observations.csv) | All 144 retained B/C/D observations: candidate counts, scan positions and separate native/app/DAO checks |
| [discovery-coverage.csv](discovery-coverage.csv) | Candidate groups, results and recorded start heights in B/C/D and the original snapshot |
| [source-index.csv](source-index.csv) | Original local source/evidence paths, sizes and SHA-256 hashes; these raw files are not included |
| [verification.json](verification.json) | Evidence-integrity and publication security checks |
| [evidence-manifest.json](evidence-manifest.json) | File sizes and SHA-256 hashes for this publication, including the repository README link |

CSV timestamps are UTC. `source` references use original repository-relative paths, with physical JSONL line numbers where available; they are provenance references, not public download links. Each source file's hash is in `source-index.csv`.

Some CSV column names retain the research tool's wording:

- `owned_cursor_min/max` are the lower/higher scan positions of the two active accounts. `owned_min_height` is their lower position.
- `global_filtered_height` is the shared light-client filter scan position. It can return to older history when new candidates are registered. `minimum_registered_height` is the lowest current Script scan position, not its historical start.
- `registered_floor` is the lowest recorded registration start. `exclusive_height_span` is target minus that start. It does not certify the actual checked end; imported verdicts may predate the target.
- `nativeLiveOutpoints` checks which live outputs are present; `nativeHistory` checks transaction IDs against the chain reference. `roomBalance` and `roomHistory` check Pocket's app cache. `accountCorrect` combines those sample checks, but excludes DAO and target-coverage checks. A `False` value can reflect an app cache awaiting refresh.
- `matched_work_rows` counts pending matched-block work. `dao_position_match` checks the known deposit, not the reward estimate.
- C's `all_empty_first_observed` time records imported results seen in the first observation, not a new discovery scan. Registration rows use `owned` for active accounts and `discovery` for candidates; adjacent rows can belong to the same registration call.

The audit rechecked **240 original sealed files**, B/C/D manifests with **33/33/37 members**, the saved package's hashes, the chain-reference binding and all six matching acceptance results. Their common wallet-state SHA-256 is `f78ce47bf5bf353093ec23d621105d4462afc422e4a95d7e4b0768c3ab41d836`. The original seal's SHA-256 is `0b8c327fe5f4089e228dae821748efc8bf3e21f370e8161e8317f403304495f4`.

From the repository root, each manifest entry can be checked with `sha256sum <path>` or PowerShell `Get-FileHash -Algorithm SHA256 <path>`. The manifest does not hash itself. Published text uses LF line endings; compare against GitHub's raw file or Git's stored blob if a Windows checkout changes them. Hashes establish which bytes were retained. They do not independently reproduce the experiment or prove that the source scanned every historical block.
