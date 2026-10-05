# WO-3B1 Candidate B result

2026-10-05. **NOT RUN.** SOURCE failed the mandatory automatic-recovery preflight. No H-state package, trusted manifest digest, immutable package copy, post-H event or F was produced.

No Candidate B profile was created or booted. No key recovery, package transfer, stage, activation, catch-up or restart occurred. No source security state or database was transplanted.

| Acceptance/measurement | Result |
|---|---|
| Candidate correctness | Not tested |
| Final live outpoints / balance / history | Not measured |
| Spent-U removal / new owned output | Not tested; no stale event exists |
| Native/application consistency | Not tested |
| Restart persistence | Not tested |
| Total recovery / package / catch-up times | N/A |
| Real-package negative checks | Not run; no real package exists |

The WO-2 package policy and helper still have their original two-account guard. The B1 reduction was identified during preparation, but no modified helper was built/deployed and no package operation occurred. No provisional changes to those existing package/helper files are retained after the stop gate. Before an approved retry reaches export, adapt the account-count/mapping guards for one primary account, preserve the exact identity/key/version/network gates, rebuild the helper into a separately recorded B1 artifact, and validate the one-account path. Do not create account 1 to satisfy an old test-harness requirement.

Existing synthetic policy checks are a tooling baseline, not negative tests of a recovered B1 candidate. The five requested real-package refusals—corrupt, missing component, wrong network, unsupported schema/version and hash mismatch—remain unexecuted. They must be tested against disposable copies after a future main B result, before activation whenever possible.

All 33 original policy tests were rerun and passed after the source stop. This includes synthetic corruption/network/version/secret rejection; it does not establish behavior of a real B1 package or a real restored wallet.

No result supports B1-FAIL-RESTORE, B1-FAIL-CATCHUP or B1-FAIL-APP: none of those mechanisms was reached.
