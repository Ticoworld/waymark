# Waymark Lite versus Full: recovery contribution audit

Research date: 14 October 2026. **All three fresh arms passed exact acceptance and cold restart. Full retains value after Lite, but this fixture did not show a large native-store-only gain.**

The original phone comparison does not measure a Lite-versus-Full split. Its Normal arm already used the source's historical start heights and explicitly recovered both known accounts. Full additionally restored native state **and settled discovery/progress metadata**. The published roughly 30-minute saving cannot honestly be called either a measured Lite saving or a pure native-store saving.

I located and rechecked the original logs, manifests, package, chain oracles and pinned source. All 29 published closure bindings and all six evidence manifests (20/30/16/55/40/10 members) verified, including historical report/source bytes recovered from closure commit `918efa774622497f673fa0e588d9d0e26c96d3a5`. The immutable package passed the original policy. The retained private fixture passed checksum and both public account-identity checks in memory; no secret was emitted. Detailed receipts are in the ignored local research directory `runs/lite-full-attribution/`.

| What the original recovery contained | Normal / control | Full candidate |
| --- | --- | --- |
| Native light-client store | Fresh; rebuild transactions, live-Cell/history indexes, headers, filter checkpoints and progress | Logical native snapshot at H2, then catch-up |
| Pocket Room database | Fresh destination database and normally recovered accounts/keys | Destination database retained; selected public progress/discovery rows installed, destination UUIDs mapped |
| Pocket transaction/balance/header/DAO caches | Rebuilt | Also rebuilt; these caches were explicitly omitted |
| Accounts | Normal parent 0 and supported creation of account 1 | Same normal recovery before import |
| Discovery | Fresh candidates; empty paths had to be scanned | 51 source candidate rows: 50 `EMPTY`, one normally owned account `RESTORED`; 41 address-path candidates and ten account-index candidates |
| Owned Scripts | Derived and registered normally | Same two full lock Scripts, native cursors restored to H2 |
| Historical floors | Explicit CUSTOM: 22,369,937 for account 0; 22,647,000 for account 1 | Exactly the same floors |
| Checkpoints/anchors | Native reconstruction | Native headers, checkpoints, chain state, recent headers and filtered height included |
| Other imported values | None | Selected TESTNET/ALL_WALLETS/active-account and per-account sync preferences, including completed-initial-sync flags |
| Signing/security | Fresh destination V2 key protection | Fresh destination V2 protection preserved; no source signing/security material imported |

Both accounts use `m/44'/309'/N'/0/0`, N=0/1, with distinct secp256k1-blake160 lock Scripts. Source H2 is **22,652,549**, hash `0x3f96acadbf4ef0d847db36468ca13feb37630fd5a156a5540713897c0dd4e3ee`. Both native owned registrations and minimum filtered height equal H2. The source's Room `lightStartBlockNumber=22,652,496` is a rewritten resume cursor, **not** the historical coverage floor. The package has exactly `manifest.json`, `app.json` (14,528 bytes) and `native.sqlite` (1,888,256 bytes), bound by manifest SHA-256 `56d4a6506641c62797531eb0f093c4930131a9046d26351377c292568d7d879e`. Native contents include nine transaction records, four live-index records, 16 history-index records, eight headers, eight block mappings, 11,326 filter checkpoints and seven metadata records; two owned lock registrations, 100 recent headers, maximum checkpoint index 11,325.

The pinned conditions were Pocket **1.8.5/code 27**, commit `b28979de744798ffb75367b031d4871ec3af1a12`, CKB TESTNET, Samsung SM-S9180 / Android 16 / ARM64 / 4 KB pages. The original common comparison block was **22,655,648**. Exclusive-floor distances were 285,711 blocks for account 0, 8,648 for account 1, versus 3,099 from the restored native anchor. These are height spans, not counts of downloaded blocks or measurements of CPU/network work.

The old event logs expose substantial stage differences, but not isolated native-versus-wallet costs:

| Original milestone, 6 October, UTC | Normal | Full |
| --- | --- | --- |
| Fresh sandbox verified | 17:38:04.464 | 18:39:26.954 |
| First launch | 17:38:13.872 | 18:39:55.762 |
| Historical floors requested, accounts 0 / 1 | 17:46:41.967 / 17:50:07.530 | 18:48:58.213 / 18:49:32.843 |
| Full activation | — | 18:50:52.809 |
| Exact common-block acceptance | 18:37:42.021 | 18:54:10.478 |
| Fresh-sandbox to common acceptance | 59m 37.6s | 14m 43.5s |
| Published end-of-arm elapsed | 60m 20.7s | 29m 42.4s |

Thus the published difference is **30m 38.4s**, including later signing/restart/audit work with different overhead in each arm. It is not the difference between isolated sync durations. The earlier **pre-signing fixture state** was already correct in Normal's 18:03:49 capture, with four discovery candidates still pending and global filtered height 22,386,000 despite owned registrations at 22,655,399. Settled discovery was first observed at 18:28:57; normal navigation/restarts prolonged this work. Full's restored discovery verdicts avoid that work too. The original logs do not identify exact sync-start or independent first-correct timestamps for each account/history/DAO; capture times are upper bounds, not internal completion events. Both original paths passed restart.

Lite avoids guessing the historical window and helps recover known account indices. It still scans that window and rebuilds native indexes and Pocket caches. Inspection of the shipped [Lite importer](https://github.com/RaheemJnr/pocket-node/blob/80f693afa60f8563c00855c6f24d9eee9a6b8354/android/app/src/main/java/com/rjnr/pocketnode/data/restorehint/RestoreHintImporter.kt) confirms that it seeds indices as **PENDING**, leaves safety rescans enabled, and does not transfer `EMPTY` verdicts or completed-sync flags. Index 1 was already inside the pinned build's normal discovery window. These files were unchanged on upstream main `c028ba0186148c9250c00a1a3ddd3f8f027b6b34` when checked. Modern Lite coarsens heights and subtracts a margin; the fixture would yield common start 22,359,000, not H2. See the [planner](https://github.com/RaheemJnr/pocket-node/blob/80f693afa60f8563c00855c6f24d9eee9a6b8354/android/shared/src/commonMain/kotlin/com/rjnr/pocketnode/data/restorehint/RestoreHintPlanner.kt).

The fresh arms used the unchanged original APK, phone and fixture, with a sealed common target **22,736,904**, hash `0xca25de35fb3fdcdbd28e545a935915e2fcb9e029782029f37acd23cf7eac1c6e`. Each independently cleared Pocket, proved absent prior state/Keystore aliases, recovered normally, created fresh destination security, and passed exact acceptance plus cold restart. They began on TESTNET directly, avoiding the original transient Mainnet initialization. B emulated Lite's information through CUSTOM choices and normal account creation at the original exact floors, importing no source state/flags/verdicts. It is not a backport or benchmark of modern Lite's rounding/UX. C used unchanged Full H2. One bounded D diagnostic used identical native bytes with fresh pending discovery and safety flags, no source app projection/caches, and minimal Room cursors derived from the native anchor.

A separate fresh A would repeat B's known-floor/account reconstruction inputs, so it was not run. This means **A−B and a fresh A−C were not measured**; historical Normal timing is not mixed with new-arm timing.

| Fresh arm | Launch → relevant registration | Registration → exact capture | Total → exact capture | Restart |
| --- | ---: | ---: | ---: | --- |
| B: Lite-equivalent, fresh native store | 1m 12.7s | 34m 10.9s | **35m 23.6s** | PASS |
| C: Full package | 4m 08.2s | 6m 44.4s | **10m 52.6s** | PASS |
| D: native reuse, fresh discovery | 8m 55.8s | 34m 07.9s | **43m 03.7s** | PASS |

Recovery starts at first launch. Registration is the logged instant immediately before JNI: B's first owned historical-floor registration, C/D's post-import H2 registration. Node startup occurs earlier. B's remaining account setup overlaps scanning; these are observations, not isolated engine timings. Exact captures were 07:36:24.589, 07:51:13.015 and 08:37:11.196 UTC respectively. D's authentication/account-creation stages alone took about **4m 42s longer** than B/C, so its raw total is not evidence that native reuse makes recovery slower.

Owned reconstruction spans were 366,967 / 89,904 blocks for B, versus 84,355 from H2 for C/D. D also traversed the 366,967-block discovery span twice. B's final discovery floor was 22,368,938, a 367,966-block span. These are exclusive-floor height spans, not full-block download counts. Both B and D needed one normal restart to activate the final four unregistered discovery probes. C retained settled metadata and registered only the two owned Scripts.

Native live sets/history first matched the oracle at approximately **12m13s / 11m45s** for B's accounts 0/1, **5m09s / 4m41s** for C, and **19m35s / 19m35s** for D, from launch. Owned cursors passed the target at approximately 14m28s, 8m46s and 22m18s. These earlier matches do not establish complete target coverage. Complete Pocket history/balances for both accounts and the DAO position were first proven together at the exact captures above; earlier internal completion was not continuously observed. DAO caches were rebuilt through normal DAO navigation. All final captures had eight / three covered transactions, three live Cells per account, exact ownership and the active DAO position. All three arms and their restarts shared semantic SHA-256 `f78ce47bf5bf353093ec23d621105d4462afc422e4a95d7e4b0768c3ab41d836`.

**Attribution:** fresh **B−C = 24m 31.0s observed elapsed saving** for the complete Full package beyond Lite-equivalent. This is not a pure native-store number or a decomposition of October 6's saving. B and D both took roughly 34 minutes between their stated registration boundary and exact capture, with the same two discovery passes. C avoided those passes. This points to discovery completion as a major contributor to the fast Full path; it does not prove zero native benefit or isolate every preference flag.

For the old saving, **Lite-attributable minutes are not established**: the start floors/known accounts were already supplied. A−B, pure native minutes and attribution shares remain unresolved—not zero-percent findings. No percentages are justified. I would classify **Full #560 as still useful but lower priority, provisionally, as a native-store import project**. The combined saved-state path retained a substantial advantage, but this fixture did not demonstrate a large store-only gain. Current Lite has not superseded the combined path because it does not carry its settled discovery metadata.

Limits: one sparse fixture, one sequential run per new condition, changing peers/tips, phone temperatures roughly 37–43 °C, manual/UI/poll/capture delays, overlapping stages and ~27-second samples. New H2 catch-up was ~84,000 blocks rather than ~3,100; the new runs are not interchangeable with the old timings. The snapshot is trusted-self research data, not a hardened production importer. Candidate rows lack a network column; the old verdicts do not prove cross-network discovery completeness. Canonical DAO position passed; the pinned 61-versus-102-CKB reward-estimate defect was separately checked, not fixed. Larger histories and other devices may change the cost balance.

Local receipts are under `runs/lite-full-attribution/`: `audit.json`, `measurement-summary.json`, `manual-stage-observations.json`, each arm's events/progress/frozen captures/evidence manifest, `deliverable-verification.json`, and `final-evidence-manifest.json`. The final verified wallet is retained with Pocket enabled and stopped. No new outgoing transaction, production-source change, PR or external message was made.

**GitHub-ready response to Raheem**

> I checked the original phone evidence: both paths already used the same historical start heights and accounts 0/1. Full restored native state plus completed discovery metadata; it did not copy Pocket's transaction or DAO caches. On the same pinned build/phone/fixture, a fresh Lite-like run reached the checked state in 35m24s, versus 10m53s for Full. Native-only reuse still needed the discovery replays and about 34 minutes from resume to equivalence. These were single noisy runs, so I cannot split the old 30 minutes into reliable percentages. Full still avoids work after Lite, but this evidence does not show a large native-store-only gain. I'd keep #560 useful but lower priority on this evidence.
