# WO-3B1 Control A result

2026-10-05. **NOT RUN.** SOURCE failed the mandatory automatic-recovery preflight; see P3B1_SOURCE_RESULT.md. Starting a control after that stop gate would not satisfy PM's execution sequence.

No Control A profile was created or booted, no application was installed for this arm, no recovery timer started, and no keys were entered. Existing source/emulator state was not reused as a control.

| Acceptance/measurement | Result |
|---|---|
| Normal recovery / expected Script | Not tested |
| Final live outpoints / balance | Not measured |
| Covered history / post-H transaction | Not tested; no post-H transaction exists |
| Spent-U exclusion | Not tested; U/H were not fixed |
| Script progress coherence | Not measured |
| Restart persistence | Not tested |
| Total recovery time / phase times | N/A; no timer |

This is neither a successful control nor evidence that ordinary Pocket recovery is incorrect. A future retry must first qualify SOURCE and establish H, the authorized stale event, and F. Its Control A must then start from a separate clean userdata directory and time first launch through persistent acceptance, using the justified pre-funding coverage start.
