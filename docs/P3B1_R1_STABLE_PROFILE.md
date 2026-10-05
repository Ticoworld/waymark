# WO-3B1-R1 stable emulator profile

2026-10-05. **QUALIFIED: API 36 / x86_64 with host GPU rendering. GO for a PM-approved B1 retry, starting at automatic recovery.** Two cold-boot cycles passed Android-only and Pocket-startup checks. This order ends before phrase entry and does not resume B1.

## Reproducible profile

The qualified profile uses the existing isolated `H02_P0_API36_X64` AVD at `runs/wo2/avd/H02_P0_API36_X64.avd`, with explicit serial `emulator-5580`. API 36, default x86_64 image revision 2 / extension 17; emulator 36.5.11.0 / build 15261927; WHPX; 2048 MiB RAM; two vCPUs; Pixel 6 display at 1080 x 2400 / density 420; effective 6 GiB data partition; **host graphics**; headless, no audio, no snapshots. Runtime `/data` reports 6,082,144 KiB total and 5,442,584 KiB available in the first host-graphics Android capture.

Pocket is the existing WO-2 debug APK:

- Source/tag: `b28979de744798ffb75367b031d4871ec3af1a12`, v1.8.5.
- Package/version: `com.rjnr.pocketnode`, 1.8.5 / versionCode 27, debuggable.
- Artifact: `runs/wo2/gradle/app/outputs/apk/debug/app-debug.apk`.
- SHA-256: `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`.
- Embedded LC from WO-2: 0.5.4, tree `3ac3e0ce1f4e46897d188b76c5b841b9097fa506`; no new LC build or integration in R1.

The only configuration change is the launch flag `-gpu swiftshader` becoming `-gpu host`. The latter selects Intel Iris Xe, driver 32.0.101.7088, through the emulator's OpenGL ES translator. No Pocket source, APK, image or host toolchain change was made. RAM, CPU count, display and headless mode are unchanged. The stored AVD `config.ini` still matches the preserved original; the launch flag overrides its GPU defaults. No RAM increase, visible-window run, new AVD or API-35 fallback was tested.

## Qualification observations

Baseline evidence is under `runs/wo3b1-r1/original-boot1/` and `original-boot2/`. First baseline: 56.956-second boot, 180.10-second Android-only check, Pocket cold launch 3856 ms, 180.12-second stable Pocket observation and successful system/Pocket UI return. Second baseline: 55.436-second boot and responsive system/launcher/Settings, but one background Android Phone ANR at 18:54:33-35 before Pocket. System-server stayed alive; no ANR loop developed. This is not counted as a clean repeated qualification and Pocket was not launched in that second cycle. The diagnosis records the logcat evidence even though `lastanr` reported none.

Host-graphics evidence is under `runs/wo3b1-r1/hostgpu-boot1/` and `hostgpu-boot2/`. These use the same host-graphics flags and existing userdata, with no snapshot loading/saving. This is a cold-restart test of the existing unpopulated installation, not two factory-fresh independent wallet arms. Recorded Linux boot IDs distinguish guest boots.

| Test | First cold boot | Second cold boot |
|---|---|---|
| Emulator-reported boot duration | 51.358 s | 48.556 s |
| Boot watcher reaches `sys.boot_completed=1` | 51.14 s | 51.12 s |
| Android-only bounded observation | 180.13 s, Pocket absent | 180.10 s, Pocket absent |
| Launcher / Settings before and after | PASS | PASS |
| System-server PID during observations | 645, unchanged | 638, unchanged |
| Pocket cold launch, Android `TotalTime` | 3112 ms | 3989 ms |
| Pocket welcome/start UI | PASS | PASS |
| Pocket bounded observation | 180.10 s, PID 2432 unchanged | 180.12 s, PID 2413 unchanged |
| Settings / launcher / Pocket return | PASS | PASS |
| New ANRs / crash loop | None observed | None observed |

The welcome screen explicitly exposes `Recover from Seed Phrase`. No mnemonic field was entered or populated; the recovery action was not pressed. Android app-launch timings are startup diagnostics, not wallet-recovery timings.

Each host-graphics boot has an empty crash buffer and no `am_anr`/`am_crash` events through the final pre-shutdown capture. Current-boot DropBox and logcat show no system/Pocket crash loop or new tombstone. Startup StrictMode notices and a low-memory notification are retained; no low-memory-kill loop is observed. Android's `lastanr` output is corroborated by events/logcat, not used alone. The four formal host-graphics observation windows total approximately 12 minutes, plus boot and UI-interaction time. All recorded times in JSON are UTC; Android log timestamps are UTC+01:00.

The first host-graphics cycle had 6074-6369 MiB host free RAM during Android-only checks and 5610-5965 MiB during Pocket observation. The original SwiftShader first observation had 6309-6674 MiB and 6469-6645 MiB respectively. These are measurements, not a proved minimum memory requirement. See the diagnosis for the failed-run CPU pressure and the unresolved underlying trigger. A passing host-graphics run supports choosing that configuration; this sequential comparison cannot prove a graphics-driver/software-renderer defect, because host load and guest caches are not held constant. Boot-watcher and emulator-reported durations have different timing origins and polling granularity.

Second host-graphics cycle: host free RAM 5852-6114 MiB during Android-only observation and 5629-5860 MiB during Pocket observation. One emulator ran at a time. API 35 was unnecessary for this bounded qualification and remains untested.

## Exact non-secret qualification commands

Run from H02-P0, with the existing emulator fully stopped and port 5580 unused. Choose a new run label/directory for each invocation; the Python helper refuses to overwrite captures. `Start-Process` itself can overwrite redirected logs, so the existence check below is required. This sequence only launches Android; inspect Android results before the separate Pocket commands.

```powershell
Set-Location 'C:/Users/timot/Desktop/2026/CKB/H02-P0'
$ErrorActionPreference = 'Stop'
$env:ANDROID_AVD_HOME = "$PWD/runs/wo2/avd"
$r1Run = 'r1-review-boot1'
$r1Output = "$PWD/runs/wo3b1-r1/$r1Run"
if (Test-Path -LiteralPath $r1Output) { throw 'Choose a new run label' }
if (Get-NetTCPConnection -LocalPort 5580 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Emulator port is already in use'
}
New-Item -ItemType Directory -Path $r1Output | Out-Null
Start-Process -FilePath 'C:/Users/timot/AppData/Local/Android/Sdk/emulator/emulator.exe' `
    -WindowStyle Hidden `
    -ArgumentList @('-avd','H02_P0_API36_X64','-port','5580','-no-window',
                    '-no-audio','-no-snapshot','-no-boot-anim','-gpu','host') `
    -RedirectStandardOutput "$r1Output/emulator.log" `
    -RedirectStandardError "$r1Output/emulator.err"
python scripts/r1_qualify.py bootwatch --run $r1Run
if ($LASTEXITCODE -ne 0) { throw 'Boot qualification failed' }
python scripts/r1_qualify.py interact --run $r1Run --label android-start
if ($LASTEXITCODE -ne 0) { throw 'Android interaction failed' }
python scripts/r1_qualify.py observe --run $r1Run --label android-only --seconds 180
if ($LASTEXITCODE -ne 0) { throw 'Android observation failed' }
python scripts/r1_qualify.py interact --run $r1Run --label android-end
if ($LASTEXITCODE -ne 0) { throw 'Android interaction failed' }
```

Check the captured `lastanr`, crash/events/logcat and current-boot DropBox records, plus UI observations. Require no Pocket process during the Android-only interval, a stable system-server PID and responsive Settings/launcher. `sys.boot_completed=1` alone is inadequate, as failed B1 demonstrated. A Python success exit is also insufficient: some diagnostic commands intentionally preserve permission failures for review.

Only after Android passes, run:

```powershell
python scripts/r1_qualify.py pocket --run $r1Run --label pocket-start
if ($LASTEXITCODE -ne 0) { throw 'Pocket launch failed' }
python scripts/r1_qualify.py observe --run $r1Run --label pocket-idle --seconds 180
if ($LASTEXITCODE -ne 0) { throw 'Pocket observation failed' }
python scripts/r1_qualify.py interact --run $r1Run --label pocket-end
if ($LASTEXITCODE -ne 0) { throw 'System interaction failed' }
python scripts/r1_qualify.py pocket --run $r1Run --label pocket-return
if ($LASTEXITCODE -ne 0) { throw 'Pocket return failed' }
```

Inspect the same health records, require a continuous Pocket PID, and confirm the normal welcome screen after returning. Do not enter a phrase as part of qualification. Shutdown is explicit and emulator-only:

```powershell
$r1Adb = 'C:/Users/timot/AppData/Local/Android/Sdk/platform-tools/adb.exe'
& $r1Adb -s emulator-5580 shell am force-stop com.rjnr.pocketnode
# Wait for pidof to become empty; force-stop completion can be asynchronous.
& $r1Adb -s emulator-5580 shell pidof com.rjnr.pocketnode
& $r1Adb -s emulator-5580 emu kill
```

Confirm the owned emulator process has exited before repeating a cold boot. Do not start a second process on the same AVD. Preserve logs and stop if ANRs recur; do not proceed by dismissing a continuing system ANR loop.

## B1 handoff boundary

This profile can qualify startup without proving sustained history reconstruction or native catch-up under wallet load. The cause of the failed run's transient saturation remains unresolved. For a B1 retry, the host-GPU launch command here supersedes the SwiftShader boot command in the earlier WO-2 readiness report; do not silently revert that flag. The next approved B1 attempt should check host headroom and run the Android/startup gate before invoking the existing secret-safe recovery automation. Use the same qualified configuration for independent SOURCE, Control A and Candidate B roles, preferably sequentially on this host.

R1 does not qualify phrase-entry automation: that is the first step of the PM-approved B1 retry. It also does not remove the previously documented one-Script adjustment required by the WO-2 harness before B1 package work; no such harness change was made in R1.

Do not interpret startup success as B1-PASS, a product-speed result, or authorization for B2. The physical phone is untouched, no private fixture file was read, no wallet was established, and no H02 package/state restoration was attempted. D2 remains excluded. Stop for PM review before resuming B1.

At handoff Pocket is force-stopped and the owned emulator is shut down. The AVD and installed APK remain available. `runs/wo3b1-r1/qualification-summary.json` records the four trials, observation durations, PIDs, boot IDs, event findings and evidence-preservation checks. Only the two R1 reports and the diagnostic helper are tracked; run logs and emulator state remain ignored.
