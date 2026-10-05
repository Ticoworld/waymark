# WO-2 emulator readiness

Disposable profile: H02_P0_API36_X64. Location: H02-P0/runs/wo2/avd/H02_P0_API36_X64.avd. The AVD registry is also isolated under runs/wo2/avd through ANDROID_AVD_HOME. No existing AVD was repurposed or wiped.

| Property | Observed value |
|---|---|
| System image | system-images;android-36;default;x86_64, revision 2, extension 17 |
| Runtime API / ABI | 36 / x86_64, checked through the explicit emulator connection |
| Emulator | 36.5.11.0, build 15261927 |
| ADB serial | emulator-5580, from explicit port 5580 |
| AVD name check | emu avd name returned H02_P0_API36_X64 |
| Hardware acceleration | WHPX 10.0.26200 available and reported operational at boot |
| RAM / CPU configuration | 2048 MiB / 2 cores |
| Storage configuration | Requested dataPartition 4G; runtime /data filesystem reports 6,082,144 KiB total and 5,510,280 KiB available at the recorded check. System-image defaults can enlarge the configured minimum; the runtime measurement is authoritative |
| Runtime page size | 4096 bytes |
| Display / graphics | Headless boot, swiftshader, no audio; pixel_6 hardware profile |
| Snapshot policy | -no-snapshot; no wallet/emulator state snapshot used as either recovery arm |
| Boot | Successful; sys.boot_completed=1 |
| WO-2 exercise | Standalone helper against generated synthetic files in /data/local/tmp; then inspected APK installation and empty debug-sandbox probe under run-as. No Pocket/LC launch, wallet recovery, funding or chain sync |
| Physical phone | Untouched; all WO-2 device shell/file operations explicitly target emulator-5580 |

avdmanager printed warnings about missing devices.xml in already installed system-image directories, then successfully created the profile. Runtime boot/identity/API/ABI checks are stronger evidence than creation exit status alone.

The inspected app-debug.apk (SHA-256 903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f) is installed, disabled and unlaunched. The final sandbox probe verified Room, wallet/PIN preferences, key_backups and both native store paths absent. Only helper, byte-transfer and generated SQLite fixtures were placed in files/h02-*; no wallet was populated. Recorded /data measurement after initial installation/probes: 6,082,144 KiB total, 5,451,780 KiB available. No actual restore command was run against the app.

An emulator restart also passed the final actual-UID SQLite/WAL scratch-database probe, with all wallet initialization paths still absent. Its generated database is only under files/h02-probe-*. At WO-2 handoff the owned emulator is stopped; the AVD and disabled, empty debug installation remain available. No emulator snapshot containing a wallet was created or used.

## Reproduce profile creation and boot

Creation refuses an existing AVD instead of overwriting it:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/create-avd.ps1
```

For a later PM-approved session, set the isolated registry and start only this profile. Do not start a second process on a running profile/occupied port.

```powershell
$env:ANDROID_AVD_HOME = 'C:/Users/timot/Desktop/2026/CKB/H02-P0/runs/wo2/avd'
& 'C:/Users/timot/AppData/Local/Android/Sdk/emulator/emulator.exe' -avd H02_P0_API36_X64 -port 5580 -no-window -no-audio -no-snapshot -no-boot-anim -gpu swiftshader
```

No script installs to, starts, stops, changes or uninstalls the physical phone. ADB enumeration from WO-1 is not used as an implicit test target. WO-3 still needs fresh source/control/candidate app installations and normally recovered disposable keys, selected testnet coverage, an independent fixture oracle and the complete acceptance observations; this boot does not supply those results.

## Exact next commands, only after PM approves WO-3

Use this preserved empty installation for the approved source-preparation step. First establish the fixture/oracle and measurement plan from P1; do not fund or launch recovery arms based only on build success. The following commands boot the named AVD and re-enable the empty app. They do not launch it or perform recovery. Wait for sys.boot_completed to return 1 before the enable command.

```powershell
Set-Location 'C:/Users/timot/Desktop/2026/CKB/H02-P0'
$env:ANDROID_AVD_HOME = "$PWD/runs/wo2/avd"
Start-Process -FilePath 'C:/Users/timot/AppData/Local/Android/Sdk/emulator/emulator.exe' -WindowStyle Hidden -ArgumentList @('-avd','H02_P0_API36_X64','-port','5580','-no-window','-no-audio','-no-snapshot','-no-boot-anim','-gpu','swiftshader')
& 'C:/Users/timot/AppData/Local/Android/Sdk/platform-tools/adb.exe' -s emulator-5580 shell getprop sys.boot_completed
python scripts/h02_device.py enable --serial emulator-5580 --apk-sha256 903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f
```

Actual export/stage commands are in P2_TOOLING_DESIGN.md and require future fixture-derived genesis, H/hash, coverage and trusted manifest digest. They are deliberately not filled with invented values. The app enable/recovery workflow remains pending PM approval; only readiness boot/probe operations ran in WO-2.
