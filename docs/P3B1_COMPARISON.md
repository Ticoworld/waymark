# WO-3B1 comparison

2026-10-05. **No defensible A/B comparison exists.** The attempt stopped before automatic source recovery because the emulator produced system crashes and Pocket/launcher ANR dialogs.

| Metric | SOURCE | Control A | Candidate B |
|---|---|---|---|
| Wallet recovered | No | Not run | Not run |
| Correct fixture state established | No | Not run | Not run |
| H / F | Neither selected | N/A | N/A |
| Final Script/balance/live outpoints/history | Not established | Not measured | Not measured |
| Package transfer/restore | No package | N/A | Not run |
| Stale-U removal | No event | Not tested | Not tested |
| Restart correctness | Not tested | Not tested | Not tested |
| End-to-end recovery time | N/A | N/A | N/A |
| Package/catch-up time | N/A | N/A | N/A |

**A/B semantically equivalent: not established.** In a binary verdict this is NO, meaning unproven, not observed divergence.

The only meaningful elapsed observation is the emulator's reported 491.075-second cold boot. This is environment provisioning/diagnostic time, not wallet recovery time, and cannot be used to estimate either arm's speed. No speedup ratio can be calculated.

**Performance fixture: LIMITED.** The retained real fixture has three known transactions approximately 25 days old. This attempt established no meaningful reconstruction burden, so no product-level Pocket speed claim is available.

No secret was entered into the emulator; no transaction, new account, DAO position, relay actor, D2 artifact or physical-phone operation occurred. The failure is at the environment/UI qualification boundary. A successful retry of the basic one-Script mechanism is still needed before extended acceptance is justified.
