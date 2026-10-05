# WO-3B1-R1 emulator diagnosis

2026-10-05. Scope: Android and Pocket startup qualification only. No wallet secret was accessed or entered, no recovery was attempted, and no backup, transaction, DAO or additional account was created. Samsung, D2 and Pocket production source were untouched.

## Finding

**GO for a PM-approved B1 retry on API 36 with `-gpu host`.** The single graphics change passes two cold boots, each with three minutes of Android-only observation, three minutes of Pocket observation and successful launcher/Settings/Pocket interactions. No ANR or crash occurs in either host-graphics qualification cycle. See `P3B1_R1_STABLE_PROFILE.md` for the exact profile and commands. The emulator is stopped; B1 is not resumed.

The failed B1 run had **Android instability before Pocket launch**. Retained Android DropBox records establish system-component startup timeouts, a system-server crash and watchdog failure preceding Pocket's ANR. Pocket subsequently blocked in a synchronous Android package-manager call during WorkManager initialization. This is evidence of a system-wide stall, not an observed recovery or JNI/light-client failure.

The immediate failure mechanism was severe guest CPU/scheduling pressure with UI/package-manager stalls. The emulator graphics compositor is prominent in the failure samples. **The trigger of that saturation is unresolved.** Neither a SwiftShader defect, insufficient RAM, nor a Pocket production bug has been established. The unchanged profile subsequently booted normally during R1.

## Evidence preservation

Original `runs/wo3b1/source/` files remain in place. Before diagnosis, their six SHA-256 digests were saved to `runs/wo3b1-r1/preserved/failed-evidence-hashes.json`. No failed-run file was overwritten. The original `config.ini`, generated `hardware-qemu.ini`, AVD registry entry, image properties and initial host resource observations were copied into the same preservation directory. Emulator userdata necessarily changes when booted; it was not archived as a frozen disk image. The preserved files and diagnostics are the forensic boundary, not a claim of immutable userdata.

Additional historical records retrieved through `dumpsys dropbox --print` are preserved as `prior-system-server-watchdog.txt`, `prior-system-server-crash.txt`, `prior-system-server-lowmem.txt`, `prior-system-app-anr.txt`, `prior-data-app-anr.txt` and `prior-tombstones.txt`. Historical DropBox entries survive reboot and must not be mistaken for new R1 failures.

## Original profile and host

| Property | Observed value |
|---|---|
| AVD / explicit serial | `H02_P0_API36_X64` / `emulator-5580` |
| Registry / userdata | `runs/wo2/avd` / `runs/wo2/avd/H02_P0_API36_X64.avd` |
| Emulator | 36.5.11.0, build 15261927 |
| Image | `system-images;android-36;default;x86_64`, revision 2, extension 17 |
| Fingerprint | `Android/sdk_phone64_x86_64/emu64x:16/BE2A.250530.026.D1/13818094:userdebug/test-keys` |
| Hardware / display | Pixel 6, 1080 x 2400, density 420 |
| RAM / vCPU | 2048 MiB / 2 |
| Hypervisor | WHPX 10.0.26200; operational in emulator output |
| Graphics | Effective `swiftshader` from launch flags; gfxstream, software GLES/Vulkan |
| Launch | `-avd H02_P0_API36_X64 -port 5580 -no-window -no-audio -no-snapshot -no-boot-anim -gpu swiftshader` |
| Data disk | Current config 6,442,450,944 bytes; effective hardware `6g`; original WO-2 minimum request was 4G |
| Guest heap | Config `228M`; generated effective hardware reports 512 MiB |
| GPU config distinction | Stored config says disabled/auto; command-line override and generated hardware establish enabled/SwiftShader |
| Host | Windows 11 Pro 10.0.26200; Intel i5-1145G7, 4 cores / 8 logical processors |
| Host RAM at R1 preflight | 32,448 MiB total; approximately 9,241 MiB free; CPU load sample 15% |
| Host disk at R1 preflight | C: 9,070,694,400 bytes free of 498,539,163,648 bytes |

The earlier B1 report observed approximately 3.6 GiB host RAM free at one point. There is no continuous host trace proving that host exhaustion caused the guest failures. R1 starts with more free host memory, which is an uncontrolled environmental difference, not a deliberate RAM fix.

## Failed-run sequence and stacks

Times below are Africa/Lagos, UTC+01:00, on 2026-10-05.

1. Around 15:47:55: cold boot begins. Emulator eventually reports `Boot completed in 491075 ms`.
2. Before Pocket launch: SystemUI, network stack, phone and Settings time out. At 15:54:02 Android records `IllegalStateException: Lost network stack`; the exception explicitly identifies itself as a consequence of an earlier failure.
3. At 15:57:33: system-server watchdog reports `Blocked in handler on ui thread (android.ui) for 77s`. Its CPU sample shows 99% total guest CPU, graphics composer about 90% (88% kernel), CPU pressure avg10=86.11 and I/O pressure avg10=23.57. Memory pressure avg10=0.02 is low in that sample.
4. Low-memory DropBox notices at 15:55:03 and 15:58:32 are retained. Their dumps report roughly 1.1 GiB free RAM, so the labels alone do not establish exhaustion. Bluetooth/system failures and launcher ANRs are additional symptoms.
5. Pocket ANR at 16:01:41 reports failure to complete startup. The captured main thread is blocked along this path:

```text
CkbWalletApp.onCreate:33
  SyncWorkScheduler.ensurePeriodicCatchUpScheduled:50
    SyncWorkScheduler.getWorkManager:37
      WorkManager initialization / background scheduler creation
        PackageManagerHelper.setComponentEnabled
          ApplicationPackageManager.setComponentEnabledSetting
            IPackageManager proxy -> BinderProxy.transactNative
```

The same ANR sample shows about 99% total guest CPU and graphics composer about 91%. No wallet recovery/JNI frame appears on this blocked main-thread stack. Source at the pinned commit confirms the normal startup call in `android/app/src/main/java/com/rjnr/pocketnode/CkbWalletApp.kt:33` and `data/sync/SyncWorkScheduler.kt:37-50`. Even the foreground-service build initializes WorkManager to cancel prior periodic work. That explains the path without proving a WorkManager defect.

6. The B1 UI attempt displays Pocket's ANR, then Quickstep's ANR after one Wait action. The source never reaches a qualified recovery UI. B1 stops without entering the phrase.

This does not establish an emulator/debug-only Pocket defect versus release/physical behavior; no such cross-platform test was run. There is no evidence requiring a production patch or Android downgrade to mask a reproducible Pocket bug.

## R1 tests

All device operations explicitly select `emulator-5580`. `scripts/r1_qualify.py` checks the emulator/AVD, refuses overwriting observation files, captures semantic UI without screenshots, and refuses nonempty editable fields. It contains no fixture-reading, recovery or signing path.

The first repeat cold boot uses **unchanged AVD settings and launch flags**, with no wipe, package clear, image replacement or toolchain upgrade. Android-only qualification precedes an explicit Pocket launch. The installed APK is checked as v1.8.5 / code 27 / debuggable and against SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. Pocket source remains `b28979de744798ffb75367b031d4871ec3af1a12`.

First repeat: emulator boot completion 56.956 seconds; the separate boot watcher observes `sys.boot_completed=1` at 62.99 seconds. Android-only observation lasts 180.1 seconds, with no Pocket PID and unchanged system-server PID 643. Launcher and Settings respond before and after. No ANR since boot is reported; crash buffer is empty. A startup `am_low_memory` event is recorded, but no new ANR/crash or low-memory-kill loop is found. Older tombstones remain distinguishable by timestamp.

Pocket's first launch returns `Status: ok`, `LaunchState: COLD`, TotalTime 3856 ms. Semantic UI contains `Welcome to Pocket Node`, `Create New Wallet`, and `Recover from Seed Phrase`. No recovery action is taken. A later `top` sample shows 193% idle of 200% available guest CPU, with Pocket idle and the graphics compositor around 3.7%; this is a point sample, not a sustained load benchmark.

Pocket then stays alive for 180.12 seconds, PID 2459 unchanged, with no new ANR/crash. Settings and launcher respond and Pocket returns to the welcome screen. The first cycle passes bounded startup qualification.

The second unchanged cold boot completes in 55.436 seconds (watcher 61.49 seconds). Launcher/Settings remain responsive, system-server PID 633 remains constant, and Pocket is absent throughout a 180.13-second observation. However, current-boot event/logcat records contain **one new Android Phone ANR**, at 18:54:33-35, before Pocket launch. Its `SafetySourceReceiver` times out on `android.safetycenter.action.REFRESH_SAFETY_SOURCES`; Android kills the background phone process for `bg anr` and restarts it. This is not a launcher/system-server loop, but prevents describing the repeated baseline as ANR-free.

The new ANR sample again has substantial CPU pressure: avg10=85.91, 97% total guest CPU, system-server 31%, SurfaceFlinger 28%, graphics composer 13%; memory pressure avg10=0.56. The exact original storm does not recur. `dumpsys activity lastanr` misleadingly says no ANR since boot, and a targeted DropBox query finds no persisted report, while logcat and the events buffer explicitly establish the ANR and kill. The trace file is listed under `/data/anr/` with system-only permissions. These diagnostics justify using multiple health sources.

Second-cycle Pocket launch is intentionally withheld. The baseline is retained as evidence rather than being represented as a clean repeat. One next configuration change is tested: launch with `-gpu host` instead of `-gpu swiftshader`. API/image, AVD userdata, RAM, CPU count, APK, headless mode, audio and snapshot policy stay the same. Host graphics uses Intel Iris Xe driver 32.0.101.7088 (emulator OpenGL ES translator; Vulkan 1.4.323). No GPU driver or emulator upgrade is performed. The emulator emits a `VulkanVirtualQueue` support warning; actual boot/UI results determine qualification.

Host-GPU qualification passes twice: boots 51.358 and 48.556 seconds; Pocket cold startup 3112 and 3989 ms; stable Android-only/Pocket windows of approximately 180 seconds each per boot. System-server PIDs stay 645 and 638 within their respective boots; Pocket PIDs stay 2432 and 2413. Launcher and Settings open/close, Pocket returns to its welcome screen, and current-boot events, crash buffers, logcat and DropBox show no new ANR/crash. Distinct Linux boot IDs establish a real restart. These startup times do not measure wallet recovery. Full evidence and commands are in the stable-profile report.

## Configuration decisions and limits

Only the graphics backend is changed after a system ANR recurs before Pocket. RAM/CPU increases, visible-window mode, a newly created API-36 AVD and API 35 remain untested fallbacks, not failed options. Cold boot is repeated without snapshot loading; it is not a factory reset or a newly created AVD. Although host graphics passes, this small sequential sample cannot prove SwiftShader caused the original storm: host load and persistent guest caches are uncontrolled differences.

Direct unprivileged reads of `/proc/pressure/*` are permission-denied on this image. An initial combined pressure-capture command produced an empty file; subsequent captures preserve explicit per-file denials. Failure-period pressure data comes from the historical watchdog/ANR reports. `dumpsys cpuinfo` can contain a cached boot-period sample; the separate `top` capture is used for the current idle observation. Diagnostic availability is not silently treated as a passing health test.

R1 can qualify bounded boot/startup behavior only. It cannot establish wallet recovery, network sync stability, long-running native load, state-restore correctness or performance. B1 remains inconclusive until a separately approved retry performs those operations.

Final preservation check: all six original failed-run evidence hashes match; the AVD `config.ini` is byte-identical to the preserved original. The selected graphics override is recorded in each trial's launch evidence and effective generated hardware. `qualification-summary.json` records the checks. Pocket's pinned source checkout remains clean. Only R1 reports and the non-secret diagnostic helper are added to the local experiment repository.
