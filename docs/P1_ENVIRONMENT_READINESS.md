# P1 — Environment readiness

Date: 2026-10-05. Readiness inspection only. No Pocket build, test suite, emulator launch, APK installation, uninstall, wallet operation or sync experiment was run. Physical-phone interaction was limited to adb devices -l enumeration.

## Overall result

**Tooling is partly ready; a reproducible emulator build and sandbox helper are NOT TESTED. WO-2 execution is not yet cleared.**

Windows already has SDK 36, working Gradle 8.14.3/JDK 21, Rust 1.92.0 with both default ARM targets, NDKs, adb, x86_64 AVDs and usable WHPX acceleration. Missing for the chosen emulator path: the x86_64 Android target under Rust 1.92.0, a newly designated disposable AVD, a built/verified v1.8.5 debug APK, and the safe observation/export/staging helper.

Pocket's direct Gradle cargoBuild invokes a Unix shell script; it is not a verified Windows-native build route. Historical G3 recorded an earlier Windows hook failure and a later successful disposable debug execution. Neither result establishes current v1.8.5 reproducibility. Do not substitute the old APK.

## Prerequisites

| Prerequisite | Classification | Observed evidence / limit |
|---|---|---|
| Isolated Pocket source | READY | Clean detached b28979de744798ffb75367b031d4871ec3af1a12, tag v1.8.5; no tracked jniLibs binaries |
| Android SDK | READY | C:/Users/timot/AppData/Local/Android/Sdk, ANDROID_HOME set; platforms android-36, android-36.1, android-37.0 present |
| SDK/build-tools | READY | 35.0.0, 36.0.0, 36.1.0, 37.0.0 present; source compiles SDK 36, target 36, min 26 |
| SDK manager | READY | Exists at SDK/cmdline-tools/cmdline-tools/bin/sdkmanager.bat; not on PATH; no package install/license command executed |
| Java runtime / Gradle launch | READY | Android Studio JBR OpenJDK 21.0.10; JAVA_HOME points to C:/Program Files/Android/Android Studio/jbr. Cached Gradle 8.14.3 --version ran successfully on this JDK. |
| Exact release-CI JDK 17 parity | MISSING | Workflow uses JDK 17; no separate JDK 17 found in inspected standard Windows/WSL locations. Source bytecode target 17 is not a demand that Gradle itself run only on 17. JDK 21 launch works; project compilation compatibility NOT TESTED. |
| Gradle wrapper | READY | android/gradlew, gradlew.bat, wrapper JAR/properties present, distribution 8.14.3; matching cached distribution exists |
| Gradle project/dependency resolution | NOT TESTED | No build/configuration tasks or tests invoked; --version checks launcher only |
| AGP/Kotlin/Room requirements | READY (configuration known) | AGP 8.13.2; Kotlin/KSP 2.3.10; Room 2.8.4. Artifact resolution not tested. |
| Windows Rust pinned toolchain | READY | rustup run 1.92.0 rustc --version returned rustc 1.92.0 (ded5c06cf 2025-12-08) |
| Current rustc/cargo on PATH | VERSION MISMATCH | Resolve to standalone C:/Program Files/Rust stable LLVM 1.96/bin, version 1.96.0. Select rustup shims and the 1.92.0 toolchain explicitly for later builds. Merely setting RUSTUP_TOOLCHAIN while calling standalone rustc is not enough. |
| ARM Rust targets under 1.92.0 | READY | aarch64-linux-android and armv7-linux-androideabi installed |
| Emulator Rust target under 1.92.0 | MISSING | x86_64-linux-android absent. Both discovered AVDs use x86_64. Default APK contains ARM ABIs only unless BUILD_X86_64=1 is set. |
| Windows NDK/compiler files | READY | SDK/ndk/27.0.12077973 (source.properties says r27) and 27.1.12297006 (r27b). clang.exe and Android target compiler wrappers present. |
| Exact release-CI NDK match | VERSION MISMATCH | Workflow requests ndk-version: r27c, but its comment calls that 27.0.12077973. Installed source.properties identifies 27.0 as r27 and 27.1 as r27b; no r27c directory found. No explicit ndkVersion in Android project. Pin/record the chosen actual revision before testing; do not repeat the inconsistent comment as a verified version. |
| Git Bash | READY | C:/Program Files/Git/bin/bash.exe exists |
| JNI build route on Windows | NOT TESTED | cargoBuild commandLine("./build-android-jni.sh") is a direct Unix-script invocation. A manual Git Bash native build plus Gradle -x cargoBuild is a possible route, not yet verified. Native script sets RUSTFLAGS globally while compiling stubs; old G3 saw host-build contamination. No workaround or source patch was made here. |
| adb | READY | Platform-tools adb 1.0.41 / 37.0.0-14910828 on PATH |
| Android emulator binary | READY | SDK/emulator/emulator.exe, version 36.5.11.0; not on PATH |
| Emulator acceleration | READY | emulator -accel-check returned 0; WHPX(10.0.26200) installed and usable |
| Existing AVDs | READY (inventory only) | Chevta_2C_AOSP36: API 36 default x86_64. Pixel_8: API 37 Google APIs Play Store x86_64. Existing data not inspected or altered. |
| Disposable H02 AVD | MISSING | None created/designated. Existing named AVDs are not automatically safe to wipe or use. No emulator started. |
| Physical Android visibility | READY | adb devices -l showed one authorized Samsung SM-S9180. Device serial deliberately omitted from committed report. No phone shell command, force-stop, install or wallet inspection. |
| Production phone suitability | NOT TESTED | Visibility is not approval to use it. First A/B should use new disposable emulators. |
| Debug APK and native x86_64 library | MISSING | None built/downloaded in H02. No reuse of D2 APK or packaged native library assumed. |
| Debug app sandbox/run-as/sqlite access | NOT TESTED | No app installed; release run-as is not assumed. Stock Android sqlite3 availability is not established. Test helper must avoid starting Pocket during offline extraction/injection. |
| WSL complete Android build route | MISSING | Ubuntu exists but has no JDK in /usr/lib/jvm, no java on inspected PATH, no SDK in inspected standard paths, and no Linux Android targets in installed toolchains. No usable full Linux build stack established. |
| Network/peers/faucet/fixture oracle | NOT TESTED | Tag/release/docs HTTPS reads worked; no P2P sync, faucet funding or node access attempted |

The classification READY is scoped to observed presence/version or the named invocation, not a successful app build or test.

## Readiness side effect — recorded, not hidden

Ubuntu was initially stopped and was started for environment inspection. The command:

    rustup target list --installed --toolchain 1.92.0

unexpectedly triggered rustup automatic installation because that Linux toolchain was not already installed. Output showed channel sync and "downloading 6 components". It was interrupted with Ctrl-C. A subsequent filesystem/process inspection found no running rustup process and a partial /home/timot/.rustup/toolchains/1.92.0-x86_64-unknown-linux-gnu directory with no target directories beneath lib/rustlib.

This is a tooling/cache side effect outside the new repository, not a successful setup step. It is NOT classified READY. No cleanup, deletion or further installer command was performed. Existing CKB repositories/evidence were not modified. Further checks used direct filesystem inspection to avoid repeating automatic installation.

Cached Gradle --version also ran against the existing host distribution; no source build tasks ran.

## Source-backed build settings

- android/app/build.gradle.kts:10-79: app ID/version, SDK and ABI selection.
- Same file:186 onward: release/playRelease distinction; no debug applicationIdSuffix declared. A debug install could collide with an existing phone installation, another reason not to use the physical phone.
- Same file:408-436: cargoBuild script hook and preBuild dependency.
- android/gradle/wrapper/gradle-wrapper.properties: Gradle 8.14.3.
- android/gradle/libs.versions.toml: versions above.
- external/ckb-light-client/rust-toolchain: 1.92.0.
- external/ckb-light-client/build-android-jni.sh: default ARM targets, optional BUILD_X86_64, stub/RUSTFLAGS handling, library output into android/app/src/main/jniLibs.
- .github/workflows/release.yml:92-168: JDK 17, requested NDK r27c, native targets and unsigned release build.
- Original G3 source report's failed setup was superseded by G3-1R1 execution; neither was rerun.

## Exact next commands recommended

These are for a **later PM-approved build-readiness step**, not commands executed in WO-1 and not an authorization to run the lost-device test.

Safe read-only rechecks from PowerShell:

~~~powershell
git -C 'C:/Users/timot/Desktop/2026/CKB/H02-P0' log -1 --oneline
git -C 'C:/Users/timot/Desktop/2026/CKB/H02-P0/repos/pocket-node' status --porcelain=v1
git -C 'C:/Users/timot/Desktop/2026/CKB/H02-P0/repos/pocket-node' rev-parse HEAD
& 'C:/Users/timot/.cargo/bin/rustup.exe' target list --installed --toolchain 1.92.0-x86_64-pc-windows-msvc
& 'C:/Users/timot/AppData/Local/Android/Sdk/emulator/emulator.exe' -list-avds
adb devices -l
~~~

The Windows toolchain above is confirmed installed; do not issue the same query against an absent Linux toolchain.

After PM authorizes installing the missing emulator target:

~~~powershell
& 'C:/Users/timot/.cargo/bin/rustup.exe' target add --toolchain 1.92.0-x86_64-pc-windows-msvc x86_64-linux-android
~~~

Potential native build route for PM review, run in Git Bash, **unverified**:

~~~bash
cd /c/Users/timot/Desktop/2026/CKB/H02-P0/repos/pocket-node/external/ckb-light-client
export PATH="/c/Users/timot/.cargo/bin:$PATH"
export RUSTUP_TOOLCHAIN=1.92.0-x86_64-pc-windows-msvc
export ANDROID_HOME=/c/Users/timot/AppData/Local/Android/Sdk
export ANDROID_NDK_HOME=/c/Users/timot/AppData/Local/Android/Sdk/ndk/27.0.12077973
export BUILD_X86_64=1
./build-android-jni.sh
~~~

This chooses the installed r27 revision explicitly; it does not claim CI r27c parity. Verify shell/compiler execution and host-build flags before relying on the result. If it fails, preserve the failure and resolve build tooling within the isolated workspace under PM scope. Do not patch Pocket production logic or silently use a newer Rust.

Only after native build succeeds with all required ABIs, the matching PowerShell packaging command is:

~~~powershell
Set-Location 'C:/Users/timot/Desktop/2026/CKB/H02-P0/repos/pocket-node/android'
$env:BUILD_X86_64 = '1'
.\gradlew.bat assembleDebug -x cargoBuild
~~~

Skipping cargoBuild before producing the exact pinned native libraries can create a nonfunctional APK; it is not a shortcut around the missing native build. No installation/start/force-stop/restore commands are recommended for the visible phone.

Before WO-2 timing, PM must designate a fresh disposable AVD and authorize the minimal test helper. Do not start either A/B arm until build provenance, helper access and the acceptance observation path are verified.

## WO-1 document and preservation checks

The new Pocket checkout remains clean at the verified v1.8.5 tag/commit with the expected origin and no Git alternates. Across the 37 existing Git roots in WO-0, HEAD/unborn state, current branch, remotes and status-entry counts match the recorded inventory. This is a metadata comparison, not a byte-level audit of every ignored artifact. All six experiment-source SHA-256 fingerprints recorded in WO-0 also match. No historical evidence database was opened.

The copied inventory is byte-identical to the original; SHA-256 is 1dfcf0f7ed6e13b002d3b0ea434f7a929c513c6dfe96f58473720b2977eb02a5. All 54 pinned source links in the four P1 reports resolve to paths in the isolated checkout, and all 47 line anchors are within the cited files. These document checks do not establish runtime recovery correctness.

The local root commit is restricted to .gitignore, the copied inventory and the four P1 reports. Nested source, captures, generated output and private material are excluded. No build/test suite or lost-device A/B was run for this documentation work.
