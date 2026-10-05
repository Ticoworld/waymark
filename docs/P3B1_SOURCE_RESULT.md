# WO-3B1 source result

2026-10-05, Africa/Lagos (UTC+01:00). **B1-INCONCLUSIVE: stopped at the automatic-recovery preflight.** No wallet recovery, package creation or transaction was performed.

PM's B1 instruction supersedes the extended two-account/DAO preparation in P3_EXECUTION_PLAN.md. This attempt used only the existing SOURCE AVD. No account 1, relay actor, DAO state, physical-phone access or D2 operation occurred.

## Pinned environment

| Item | Observed/configured value |
|---|---|
| Pocket source | b28979de744798ffb75367b031d4871ec3af1a12, v1.8.5; source checkout remains clean |
| APK SHA-256 | 903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f |
| APK guard | Passed after Android recovered sufficiently; Pocket was enabled and launched |
| Embedded LC | 0.5.4; tree 3ac3e0ce1f4e46897d188b76c5b841b9097fa506 |
| SOURCE | H02_P0_API36_X64, explicit serial emulator-5580 |
| AVD registry | H02-P0/runs/wo2/avd |
| Platform | API 36/default/x86_64; 2 cores, 2048 MiB RAM; WHPX, SwiftShader, no-window/no-snapshot |
| Intended chain | TESTNET; normal UI recovery/network selection was not reached |
| Intended owned account | m/44'/309'/0'/0/0; args 0xbc5882c4309431ee23ad7bbad4b5c3325539eebd |
| Intended coverage start | 22,369,937, before first known relevant activity at 22,369,938; not applied |

## Exact blocker and bounded handling

1. Cold boot began around 15:47:55 local. ADB was initially offline, then reachable before Android services were ready. The existing version/device guard refused premature operations.
2. Android's crash buffer records a system-process fatal exception at 15:54:02: `IllegalStateException: Lost network stack`. The message explicitly says this is a consequence of an earlier failure, not the root cause. SystemUI, Bluetooth and other system components subsequently failed. Additional system-component failures appear around 15:57.
3. Emulator stdout eventually reported `Boot completed in 491075 ms` (491.075 seconds). Readiness checks at 15:57:13 and 16:01:45 local returned boot=1, the expected AVD, activity service, emulator identity and installed package path. These basic checks did not establish a usable UI.
4. After enabling and launching the pinned APK, the UI driver observed **“Pocket Node isn't responding”**, with Close app / Wait buttons. The ordinary recovery screen was not reached.
5. One Wait action was taken. The subsequent sanitized UI capture, written at 16:05:19 local, instead showed **“Quickstep isn't responding”**. `dumpsys activity lastanr` names the Android launcher and a 5001 ms focus-event input-dispatch timeout at 16:00:24 local.
6. Following PM's explicit stop gate, Pocket was force-stopped and disabled, then the owned emulator was shut down through `adb -s emulator-5580 emu kill`. The owned emulator processes exited. No userdata wipe, app clear/uninstall or phone operation occurred.

This establishes an unusable recovery environment during this attempt. It does **not** establish that Pocket's recovery code, native state portability, or the phrase-entry selector implementation is defective. The phrase-entry helper was never invoked. Root cause of the Android instability remains unresolved; neither RAM exhaustion nor a particular production-code defect was proven. Host telemetry observed approximately 3.6 GiB free RAM out of 31.7 GiB at one point, which is not sufficient to diagnose the failures.

## Source acceptance and package status

| Required fact | Result |
|---|---|
| Automatic normal wallet recovery | FAIL at preflight; phrase not entered or transferred |
| Recovered address/Script | Not established in SOURCE |
| Balance/live outpoints/history | Not established in SOURCE; prior setup oracle is not substituted |
| Script progress / verified tip | Not established for a recovered fixture |
| Sync mode/start | Not configured |
| Native/Room wallet-state agreement | Not evaluated |
| Correct before backup | NO — required agreement was not established |
| H / H hash | Not selected |
| Sanitized package / immutable copy | Not created |
| Package bytes / export time / secret gate | Not applicable |
| Post-H transaction / F | None / not selected |

The retained setup oracle still records three historical testnet transactions and three live Cells totaling 1,999,999,999,000 shannons. Those are prior public observations, not a fresh source correctness result. No new funding or spending was initiated. The source-loss stage was not reached; shutdown here is failed-preflight cleanup, not a completed loss simulation.

## Preserved evidence and custody

Ignored local evidence under `runs/wo3b1/source/`:

- `emulator-boot.log` / `.err`: boot diagnostics and recorded boot duration.
- `readiness.json`: bounded, explicit-emulator readiness checks.
- `pre-recovery-crash.log`: Android crash-buffer capture made before any secret entry.
- `pre-recovery-anr.txt`: launcher ANR details.
- `ui-after-wait.jsonl`: sanitized semantic UI observation showing the Quickstep dialog; no screenshot or raw UI XML is retained.

The initial Pocket ANR is also recorded in the tool execution transcript. All ADB operations targeted emulator-5580. The physical Samsung was not queried or modified in WO-3B1. The fixture secret remains in the ignored, access-restricted private directory. No new secret transport file was created on the emulator.

`scripts/p3b1_readiness.py` and `scripts/p3b1_ui.py` retain the bounded readiness check and emulator-only normal-UI driver for a future approved retry. Pocket production source is unchanged.

Final checks: the unchanged WO-2 policy suite passed all 33 synthetic tests (36.615 seconds; a tooling regression duration, not wallet recovery). The actual-fixture leak audit passed across 75 documents/scripts/new-output files, including UTF-16 log encodings. No fixture mnemonic sequence or derived private-key bytes/hex were found in those public paths. Run artifacts remain ignored. The original package policy/helper source is unchanged; no unqualified one-account binary was substituted.
