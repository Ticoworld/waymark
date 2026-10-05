# WO-2 pinned Pocket build report

Date: 2026-10-05. Scope: build and test-only harness preparation. No Pocket launch, wallet keys, funding, chain sync, lost-device A/B, D2 integration, cloud, PR or grant work.

## Source and isolation

Pocket remains detached at v1.8.5 / b28979de744798ffb75367b031d4871ec3af1a12, origin https://github.com/RaheemJnr/pocket-node.git. Production source is unchanged. Embedded ckb-light-client-lib declares 0.5.4; exact vendored tree is 3ac3e0ce1f4e46897d188b76c5b841b9097fa506. No independently authoritative upstream LC commit was discovered or substituted.

All new build scripts, helper source and documents are in H02-P0. Generated output is under runs/wo2, except ignored JNI packaging inputs under repos/pocket-node/android/app/src/main/jniLibs/x86_64 and normal ignored build-tool caches. No historical repository/database was modified or used as a writable fixture. The new root commit contains experiment documents/scripts/configuration only.

## Toolchain

| Component | Exact selection/result |
|---|---|
| Java | Android Studio JBR OpenJDK 21.0.10, build 21.0.10+-14961533-b1163.108; target bytecode 17 |
| Gradle | Pocket wrapper 8.14.3; --no-daemon, --max-workers=4 |
| Android configuration | com.rjnr.pocketnode, versionName 1.8.5, versionCode 27; compile/target SDK 36, minimum 26 |
| AGP / Kotlin / KSP / Room | 8.13.2 / 2.3.10 / 2.3.10 / 2.8.4 |
| Android SDK | Existing C:/Users/timot/AppData/Local/Android/Sdk; no SDK/image upgrade |
| NDK | Explicit native build revision 27.0.12077973, r27; clang 18.0.1 (12027248, r522817) |
| Rustup | 1.29.0 (28d1352db 2026-03-05) |
| Rust | Explicit 1.92.0-x86_64-pc-windows-msvc; rustc 1.92.0 (ded5c06cf 2025-12-08) |
| Cargo | 1.92.0 (344c4567c 2025-10-21); --locked |
| Android Rust target | x86_64-linux-android, newly installed after recorded absence |
| Existing targets retained | aarch64-linux-android, armv7-linux-androideabi, x86_64-pc-windows-msvc under 1.92.0 |
| Host linker/compiler prerequisites | Rust-bundled rust-lld; NDK clang in MSVC driver mode; existing Windows SDK 10.0.18362.0 |
| Local MSVC import libraries/headers | Hash-pinned Microsoft CRT Desktop/Store 14.44.35226 and headers 14.44.35220; extracted tool directory 14.44.35207 under runs only |
| Make / Perl | Existing mingw32-make 4.4.1, Git Perl 5.38.2; missing pure-Perl modules extracted under runs |
| adb | 1.0.41 / 37.0.0-14910828 |
| Emulator | 36.5.11.0 / 15261927 |
| Python / Git | 3.13.14 / 2.52.0.windows.1 |

The PATH default Rust is 1.96.0; scripts deliberately invoke rustup's pinned shims instead. No unrelated Rust/JDK/NDK upgrade or Visual Studio installation occurred. The only rustup install was the missing x86_64 Android standard library for already-installed Rust 1.92.0. Before/after evidence: runs/wo2/rustup-before.log, targets-before.log, target-install.log, targets-after.log and versions-final.log.

JBR 21 compiled Java/Kotlin targeting 17 successfully; this does not claim exact JDK 17 release-CI parity. The existing NDK r27 also differs from the workflow's requested r27c (whose source comment inconsistently labels 27.0). The experiment records the actual revision and uses one identical APK for both future arms.

## Isolated Windows build fixes

Pocket's Gradle cargoBuild directly invokes a Unix shell script. The host-side recipe replaces only that build invocation: build the exact vendored Rust first, then Gradle assembleDebug -x cargoBuild with the verified JNI libraries present. It does not bypass native compilation.

Initial native attempts exposed missing Windows host prerequisites: link.exe/import libraries, cl.exe, Perl modules and a make-compatible shell. The solution uses existing NDK/Rust/Git tools plus hash-pinned runtime/header packages and pure-Perl modules unpacked into runs. scripts/host-cl.cmd is a host-compiler adapter. MSVC and Perl lock JSON files include exact upstream URLs and SHA-256 values. No Pocket files or Cargo.lock were patched.

The Perl modules are Locale-Maketext-Simple 0.21, ExtUtils-MakeMaker 7.78, Pod-Usage 2.05, podlators 6.1.1, Pod-Simple 3.48 and Pod-Escapes 1.07. The final path fix sets MSYS2_ENV_CONV_EXCL=PERL5LIB: Git sh otherwise converts the POSIX module path to C:/..., which Perl splits at the drive colon. Earlier failures remain in runs/wo2/native-build*.log.

Native flags retain release Rust, jni-bridge,portable, Android API 21 and the pinned Android stubs. Stub linking flags are target-specific so they do not contaminate Windows host build scripts. The external Gradle init file redirects outputs, selects only x86_64 and uses a newly generated isolated debug signing key under runs/wo2/signing. These are test build settings, not production behavior changes. The key/password is Android's disposable debug convention; no wallet key or production signing credential is used or committed.

The first assembleDebug reached packageDebug, then failed because the external override changed the keystore path while retaining Pocket's public CI alias smokedebug. The correction explicitly sets the isolated PKCS12 store, androiddebugkey alias and standard debug passwords in scripts/wo2-build.init.gradle. This was an experiment-configuration error; Pocket's checked-in debug configuration was not changed. Evidence: runs/wo2/android-assemble.log.

## Build and artifact results

Kotlin/Android compile: PASS, compileDebugKotlin, 24 tasks, 30m10s. Evidence: runs/wo2/android-compile.log. Compiler warnings were retained; production source was not edited to silence them.

Native Rust build: PASS. The successful final invocation completed its remaining release compilation in 18m33s; this is build time with dependencies retained from earlier attempts, not a clean-build or recovery benchmark. Evidence: runs/wo2/native-build-10.log. Stripped x86_64 light-client library: 17,611,888 bytes, SHA-256 fb8262af9279cd7379a2ab6d3a9c5397106647443012343af4241297859e402f. NDK libc++_shared.so input: 1,617,608 bytes, SHA-256 936e1150309bdae86216f14e493f478d39e588095f1577105856da6d0f24f149.

PowerShell's redirected native stderr is rendered as NativeCommandError/RemoteException blocks in several logs, including successful compiler runs. Those wrappers alone are not build failures. The initial redirected host command reported a nonzero status despite Cargo's Finished result and generated artifacts. A cached recipe recheck, captured through Python subprocess, returned exit code 0 in 26.59s with unchanged SO hashes (runs/wo2/native-recipe-recheck.log). This was not a second clean build or a bit-for-bit reproducibility test.

APK assembly: PASS after the isolated signing-alias correction, assembleDebug, 55 tasks (3 executed, 52 up-to-date), 52s. Evidence: runs/wo2/android-assemble-2.log. Kotlin, Java, DEX, JNI merge/strip, debug signing and APK packaging completed. No production source modification was needed.

| Artifact | Size / SHA-256 |
|---|---|
| runs/wo2/gradle/app/outputs/apk/debug/app-debug.apk | 49,764,015 bytes / 903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f |
| APK lib/x86_64/libckb_light_client_lib.so | 17,611,888 bytes / fb8262af9279cd7379a2ab6d3a9c5397106647443012343af4241297859e402f; identical to built/stripped JNI input |
| APK lib/x86_64/libc++_shared.so | 1,252,080 bytes / 128bb6e63a08bbd21fba7128223fb6e1016afd76dab9cbc09d9aaf4b0400f4e2; AGP strips the NDK input, so this differs from the unstripped input hash above |
| runs/wo2/helper/helper.jar | 12,193 bytes / 3c8c858e006c9ba082cb5e543dcf5198bd6e74a6489d9ce165f85768384d31ae |

aapt verified app ID, 1.8.5/code 27, min SDK 26, target/compile SDK 36, DEBUGGABLE and x86_64-only native code. apksigner verified APK Signature Scheme v2, one disposable H02 Debug signer, certificate SHA-256 52bdccbe47ca004b6bfd7ffd374ba16bd4c41ad62e15ec9df398aeb0ead42ddc. Full artifact/library inventory is in runs/wo2/apk-artifact.json; badging/signature evidence is in apk-badging.log and apk-signature.log.

ELF inspection confirms ELF64/X86-64, 24 exported Java JNI entry points (including nativeStart/nativeStop/nativeSetScripts/nativeGetScripts), and only liblog.so, libdl.so, libm.so and libc.so as dynamic dependencies. Evidence: native-elf.log and native-exports.log. Native startup/sync was deliberately not invoked.

Fresh-sandbox access: PASS. The inspected APK was installed only on emulator-5580 / H02_P0_API36_X64. A standalone helper ran under run-as without initializing Pocket or LC. The probe confirmed wallet Room/preferences/key-backup/native-store paths remained absent. It verified remote error status, an all-byte transfer and overwrite refusal, then left Pocket disabled. The final helper additionally created a generated SQLite database under files/h02-probe-*, committed in WAL mode and reopened it read-only under the actual app UID. Evidence: emulator-install.log, empty-sandbox-probe-final2.log and device-negative.log. See P2_TOOLING_DESIGN.md for the transport defects this caught and corrected. No wallet recovery or sync was run.

## Reproduction recipe

Run from H02-P0 on this Windows host. The pinned source, SDK, JBR, Windows SDK, Git Perl and mingw32-make paths above must exist. Preparation verifies hashes before extraction; a changed/download-corrupt dependency refuses the build.

```powershell
python scripts/prepare-host-crt.py
python scripts/prepare-perl-modules.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-pocket-native.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-pocket-android.ps1 -Task assembleDebug
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-helper.ps1
python scripts/test_package.py
```

scripts/test_android_helper.py additionally requires the designated running AVD with Pocket absent. It uses generated SQLite/WAL fixtures only. Do not execute actual export/stage/commit against a recovered wallet before PM approves WO-3. AVD creation/boot instructions and completed tests are in P2_EMULATOR_READINESS.md and P2_SECURITY_CHECK.md.

This is a recorded repeatable build recipe with locked source/dependencies, not a demonstrated bit-for-bit reproducible APK. Generated debug signing identity, packaging timestamps, local tool paths and uncaptured remote dependency-cache behavior can affect output bytes. Retain and use the exact inspected APK digest for both arms.

## Remaining WO-3 requirements

WO-2 does not supply the funded disposable fixture, trusted testnet genesis/H/F oracle or complete exact-state observation run. PM must approve WO-3 and establish those inputs before either arm. All cells/history/DAO/post-H/restart/signing-readiness acceptance predicates in P1_LOST_DEVICE_EXPERIMENT_CONTRACT.md remain mandatory. No speed threshold or H02 result follows from compilation or synthetic passes.

WO-2 readiness verdict: GO for PM review of the later disposable-emulator experiment. No unresolved build or known-secret-separation blocker remains. Actual wallet recovery, startup/registration replay and acceptance correctness remain unproven. All five P2 reports are complete; D2 does not enter the next phase by this result.
