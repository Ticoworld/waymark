# Recovery proof on Pocket Node

**Baseline and state-assisted recovery reached identical canonical wallet state. Both real-phone recovery paths signed confirmed testnet transactions and passed cold restart with independent destination security.**

Pocket Node 1.8.5/code 27 was tested at one pinned source commit with its embedded light client. Production Pocket source stayed unchanged; the importer/exporter was external debug-sandbox instrumentation. Exact provenance, public transactions and sealed digest bindings are in [evidence](evidence.md). The [mechanism](how-it-works.md) describes the state/secret boundary.

## Method and source-loss boundary

First validate a correct settled source against independently recorded public-chain facts. Capture a coherent saved-state checkpoint, then introduce confirmed activity after it. Stop/seal the source and declare it lost before either destination recovery. Subsequent recovery uses independently retained recovery material, the selected saved package where applicable, recorded public facts and public chain access. No later source database/runtime consultation supplies a shortcut.

Baseline recovery starts with independent fresh application state and normal key/account recovery, then reconstructs state through Pocket. State-assisted recovery independently recovers the same keys/accounts normally, creates fresh device security, maps public identities, installs the stale selected package, then catches up normally. Exact acceptance includes live outpoints/capacities, covered native/Room history, account/parent/Script mapping, no cross-account leakage, coherent progress, settled discovery, DAO canonical position where present, and restart.

The emulator environment was API 36/default x86_64 image revision 2, 2048 MiB RAM, two vCPUs, WHPX and Intel Iris Xe host graphics, headless with no snapshots. Earlier software-rendering/environment failures were inconclusive; two bounded cold-boot qualification cycles established the chosen profile. This does not prove a root graphics-driver cause or eliminate later Android boot caveats. The richer baseline recorded two pre-install boot ANRs/crashes and passed a subsequent bounded settled-system gate.

## Initial one-account proof

One populated account used explicit historical coverage from block 22,369,937. Normal source recovery and restart settled 51 discovery candidates as empty. Restart initially activated five remaining probes and replayed older filters before any state restore; this matters when interpreting elapsed time.

The saved checkpoint was 22,646,283. A later 100 CKB self-transfer spent a Cell that was live in the package. Both destinations reached exact state through 22,646,322: four covered transactions, four live Cells, and 1,999,999,998,000 shannons (19,999.99998 CKB). The state-assisted destination began with the original stale native payload, removed the spent Cell, found both replacement outputs and rebuilt omitted caches. Independent destination UUIDs mapped to the same public account, and restart preserved equivalence.

The three-member package was 1,895,341 bytes. Nine actual-package negative variants refused corruption, missing payload, wrong network/genesis, unsupported Pocket/Room/native versions, manifest trust mismatch and payload hash mismatch before activation. Synthetic host/Android tests separately exercised known secret exclusion and interruption/rollback. There was no DAO or second populated account in this initial proof.

## Two accounts and an active DAO

The richer fixture had parent account 0 and derived account 1 with distinct populated Scripts and histories. Account 1 owned a confirmed 1,000 CKB DAO deposit, still `DEPOSITED`, with exact principal, outpoint, lock/type/data, deposit header and epoch. No withdrawal/unlock was attempted.

Both historical coverage floors were explicit: 22,369,937 and 22,647,000. The first proposed source capture had a sibling tip and was refused; the accepted saved-state checkpoint was canonically anchored at 22,652,549. Its package was 1,904,717 bytes. Two later transactions at 22,652,580 consumed an old account-0 Cell and added 100 CKB to account 1. The comparison boundary was 22,652,587.

Both destinations matched six account-0 and three account-1 covered transactions without cross-account overlap. They matched exact live Cells, balances, DAO owner/position/deposit metadata, coherent per-Script/native/Room progress and settled discovery. The state-assisted destination's prelaunch capture proved the old Cell was still live, later transactions absent and application caches empty; catch-up then produced the correct replacement/incoming state. An incomplete baseline discovery capture and a later noncanonical native-tip capture were correctly refused before final acceptance.

Both emulator destinations verified local challenge signatures for both accounts before and after restart. These were signing-readiness checks with emulator security; they were not broadcast transactions or physical-device authentication proof. The later phone test established those additional properties.

## Real Samsung phone proof

The phone was a Samsung SM-S9180 running Android 16/API 36, ARM64, with 4096-byte pages. The qualified debug APK came from the same Pocket/native source as the emulator package. Its signature matched the previously installed debug build; the official release APK had a different certificate and was not selected. An overwrite/startup qualification retained existing data, then observed native initialization/execution, normal user authentication and cold restart. Qualification alone did not establish signing; the independent recovery paths did.

The x86-to-ARM audit examined the exact unchanged saved package's logical SQLite and fixed-width/packed encodings. Source manifest/ABI/APK provenance stayed unchanged. A separate phone destination policy bound the ARM APK/signer, same source/schema/network and exact public identities. No payload resealing or ABI transformation occurred. The retained public transport is emulator-only; the historical fixed-phone driver remains recoverable in Git history.

| Requirement | Baseline recovery | State-assisted recovery |
| --- | --- | --- |
| Fresh application state and absent prior Keystore aliases | Passed | Passed independently after baseline evidence was sealed |
| Normal parent/account recovery and supported account creation | Passed | Passed before state restore |
| Fresh authenticated V2 destination key rows | Passed | Passed; different creation time from baseline |
| Exact account/Script/parent mapping and no leakage | Passed | Passed |
| Live Cells, balances, covered history and both earlier post-backup activities | Passed | Passed after stale-state catch-up |
| Canonical active DAO position and deposit metadata | Passed | Passed |
| Android signing authentication and confirmed Pocket transaction | Passed | Passed after restore |
| Cold restart, native startup and persisted canonical state | Passed | Passed |

Baseline used no saved package. Both accounts were recovered through supported Pocket flows with genuine manually approved Android key-encryption/account authentication. The account key rows used V2 protection with per-operation authentication and Trusted Environment metadata. Baseline reviewed/signed/broadcast a 61 CKB account-0 self-transfer, then restarted and passed exact canonical acceptance.

State-assisted recovery created its own fresh authenticated key rows and activated the original saved package after normal account recovery. An initial coverage-mode refusal was resolved by saving explicit historical options in Pocket Settings; the validator was not relaxed. Staging preserved destination wallet IDs, encrypted-row bytes and Keystore creation/protection metadata. Catch-up recovered both original post-checkpoint events and baseline's later signing transaction.

## Canonical equivalence and signing

At common comparison block **22,655,648**, baseline after restart and state-assisted after catch-up shared semantic SHA-256 `e3075d29259b8b39c440691296b7d9c29cba8ab664361e1fc51bea9c6ea60c21`. Exact Scripts/derivations normalize independent UUIDs; timestamps and differing later native tips are observations, not wallet-identity differences. Canonical history, live Cells, balances, coverage and DAO fields agreed.

After that comparison, state-assisted recovery signed a second 61 CKB self-transfer through Pocket's normal review and authenticated V2 signing path. The user observed and approved the Android signing prompt; automation missed its transient UI, so evidence explicitly records user observation instead of claiming a captured prompt. Per-operation security metadata and the pinned signing path corroborate the result. Both transactions' recoverable witness signatures independently matched the owned account-0 Script. No host private-key signer or Android authentication bypass was used.

The second transaction's inputs were removed from the common live set and its self outputs added. This exactly explains the later final oracle: account-0 history gains that transaction, spendable capacity falls only by its 1,000-shannon fee, and account-1/DAO history and live state remain identical. Final state-assisted acceptance after signing and cold restart was at **22,655,881**. Comparing different later tips blindly would give a misleading result.

No source security material was imported. Fresh destination creation/protection metadata survived activation, signing and restart. The real-phone result therefore covers actual device authentication/storage/native startup, beyond the emulator signing-readiness result. The final state-assisted installation was retained intact, with its process stopped and package enabled without launch.

## Timing observations, not a benchmark

| Run and timing boundary | Baseline | State-assisted |
| --- | ---: | ---: |
| Initial emulator, first exact comparison acceptance from launch | 800.542 s | 208.774 s |
| Initial emulator, full acceptance including restart | 1,453.074 s | 293.140 s |
| Richer emulator, full acceptance including restart | 2,239.181 s | 730.317 s |
| Phone, reported elapsed including manual authentication/qualification overhead | 60 min 20 sec | 29 min 42 sec |

Initial source export took 3.412 s; its state-assisted package handling took 8.480 s. Richer source export took 4.398 s; restore including gates/activation took 15.961 s (transfer 1.059 s, validation 0.774 s). Source preparation/export is separate from destination timings; initial Android/APK provisioning precedes the launch timer.

These are sequential, small, unreplicated testnet runs. Times include setup/UI automation, discovery replays, manual phone authentication, peer conditions, capture/audit and restart delays. Native reconstruction, catch-up and application polling overlap and were not isolated. The phone baseline had premature captures while discovery probes were unsettled; navigation prolonged those probes. State assistance avoided work in these observations, but no controlled production-user speed number, multiplier or general threshold follows.

## Separate DAO reward-estimate defect

Pocket's pinned DAO reader passes **61 CKB** occupied capacity for the fixture's DAO Cell; canonical occupied capacity is **102 CKB**: 8 capacity bytes + 53 lock bytes + 33 type bytes + 8 data bytes. The discrepancy existed before export and before/after restart, and the reader persisted it to Room. It was not introduced by recovery.

At the fixed historical comparison header 22,647,478, canonical reward is **21,546 shannons**; observed cache is **22,530**, exactly reproduced using 61 CKB. Both small amounts display `+0.00 CKB` after Pocket's two-decimal formatting. Exact arithmetic and independent public-node maximum-withdraw RPC checks support the diagnosis; adjacent tips/cache age do not explain it. Room omits an estimate-as-of header, so the matching height is inferred from integer agreement within bounded observations.

For capacity `C`, occupied capacity `O`, deposit DAO rate `A` and comparison rate `B`:

```text
maximum = floor((C - O) * B / A) + O
compensation = maximum - C
```

The rates are unsigned little-endian bytes 8..15 of the canonical header DAO field. [Evidence](evidence.md) retains the fixed rates, outpoint, header/hash, source locations and independent audit bindings for offline inspection.

The accepted richer/phone contract requires canonical DAO owner/outpoint/principal/stage/live status/deposit metadata/history and no cross-account leakage. It separately verifies refreshed estimates against the known reader algorithm at bounded canonical headers. An unexplained restore-only difference or stale estimate would still fail. This separation did not waive exact position correctness.

Code tracing found the Android transaction path independently uses the existing 102-CKB constant for phase-2 unlock amounts and preserves principal in phase-1 withdrawal. Cached estimates affect reward display/totals and potentially later APC; APC distortion is an implication, not an observed result for this short-lived deposit. A mature withdrawal/unlock was not executed or certified. The proposed correction is to use the existing DAO occupancy constant in both deposited/withdrawing reader branches and add fixed-header/cache/restart regressions. No production patch or external bug report was sent.

## Separate 16 KB packaging observation

Android displayed a recurring native-library 16 KB alignment warning. This tested phone used **4096-byte pages** and passed. The warning is a separate Pocket/native packaging follow-up; no 16 KB-device execution or support was demonstrated, and no production fix was made.

## Claim boundary and status

The tested responsibility sits in Pocket's account model, persistence, embedded light client, normal recovery/authentication and signing. The proof required no separate external recovery layer.

The result is scoped technical research ready for maintainer evaluation, not production release qualification. Limits include one pinned source/debug version, one disposable testnet fixture, two accounts, one active DAO, one Samsung/API-36 phone, no arbitrary cross-version/backend/wallet compatibility, no extensive reorg/finality study, no hostile-source completeness proof, no large-history/device distribution, and no encryption/cloud/import UX. Further work would require a wallet-owned supported feature and a broader validation plan.
