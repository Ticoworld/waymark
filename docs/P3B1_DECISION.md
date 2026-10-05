# WO-3B1 decision

2026-10-05. **B1-INCONCLUSIVE. Do not proceed to WO-3B2.**

The existing source AVD cold boot experienced Android network-stack/system-process crashes. The pinned Pocket APK passed identity checks after boot, but normal launch showed “Pocket Node isn't responding.” One bounded Wait attempt was followed by “Quickstep isn't responding,” with a launcher input-dispatch timeout in the diagnostic record. The recovery screen was not qualified and the fixture secret was never entered.

PM explicitly required stopping when automatic recovery cannot be completed reliably. The attempt stopped there: Pocket was force-stopped/disabled and the owned emulator shut down. This stop is not a failed backup experiment and does not establish a Pocket portability defect. It also does not justify a production-code workaround.

## What a retry must resolve

1. Restore a stable Android environment with normal launcher/input/network behavior and no recurring system-process failure. Preserve this attempt's logs and userdata. Diagnose the environment before choosing a fresh source profile or revised emulator resources; use the same resulting configuration in all roles. Do not touch the Samsung.
2. Qualify normal v1.8.5 recovery using the private fixture and existing secret-safe automation. Verify the public primary Script. No key injection or production-code bypass. Stop again if recovery remains unreliable.
3. Implement the PM-authorized one-account adjustment to the existing WO-2 test harness and rebuild/test its separate B1 helper. The original two-account guard is still present; it must not cause silent scope expansion or skipped identity checks.
4. Resume the same B1 sequence: correct source → sanitized immutable package at H → exactly one authorized owned-Cell spend → F → source loss → independent A/B recovery → exact-state/restart acceptance → package refusal checks. Account 1, relay and DAO work stay excluded.

No step above has been run after the stop gate. The reports document the required retry work; they are not authorization to start a new experiment without PM review.

## Evidence and interpretation

See P3B1_SOURCE_RESULT.md for the observed failure and evidence paths. P3B1_CONTROL_RESULT.md and P3B1_CANDIDATE_RESULT.md explicitly record unrun arms. P3B1_COMPARISON.md excludes startup/diagnostic time from wallet timings.

**D2 enters now: NO.** There is no observed state-restoration, authority or catch-up failure for D2 to address. The blocker precedes wallet recovery and package creation.

**B2: NO, pending B1-PASS.** If the basic mechanism later converges correctly, B2 should add the second populated Script/account and identity remapping, DAO deposit/withdrawal reconciliation, richer coverage and restart checks, and stronger performance fixtures. Those extensions were not created in this attempt.

No funding conclusion or product speed result follows. Stop for PM review.
