# WO-3C-R1 ARM artifact qualification

The qualified phone artifact is an ARM64 debug APK built from pinned Pocket commit `b28979de744798ffb75367b031d4871ec3af1a12` and native tree `3ac3e0ce1f4e46897d188b76c5b841b9097fa506`. Its repository debug signer exactly matches the Samsung's installed Pocket 1.8.3 signer. Signature-compatible overwrite succeeded without clearing data or uninstalling Pocket.

## Official release first

Official release: <https://github.com/RaheemJnr/pocket-node/releases/tag/v1.8.5>. The release metadata and tag both identify the exact pinned commit. Asset `PocketNode-v1.8.5.apk` was acquired through the official GitHub asset API (asset 601584694) after the direct download timed out. The verified full artifact is `runs/wo3c-r1/official-api-download.apk`; the failed direct-download placeholder is not trusted or selected.

| Property | Official release |
| --- | --- |
| Bytes / SHA-256 | 38,174,535 / `34a3f649bd3365de2caa6148d68fd548f061d02e85ca51158bd84c035cec2ee2` |
| Package / version | com.rjnr.pocketnode / 1.8.5 / code 27 |
| Min / target SDK | 26 / 36 |
| ABIs | arm64-v8a, armeabi-v7a |
| Required ARM64 JNI | libckb_light_client_lib.so and libsecp256k1-jni.so present |
| APK signature | Verified, v2 |
| Certificate SHA-256 | `9c5130307bf2cbe9f9f918ed1fbba231ef040294aadc33b97f60c76662303f16` |
| Subject | CN=Raheem Hammed |
| Matches installed signer / overwrite compatible | NO / NO; no official-release install attempted |

Evidence: `release-metadata.json`, `release-tag.json`, `official-result.json` and `official-badging.txt` under `runs/wo3c-r1`.

## Repository debug signer

Pinned `android/app/build.gradle.kts` configures checked-in `android/ci/debug.keystore`, alias **smokedebug**, through the normal debug signing configuration. The certificate SHA-256 is `bb4cbddbe25b03a1bac59f9c139f845b15869d0507198a9271103f3a64c96b9a`; subject `CN=smoke, O=ci, L=Lagos, ST=Lagos, C=NG`. This exactly equals the installed phone certificate fingerprint, independently of the matching subject. Certificate evidence is `repo-debug-certificate.txt`.

## Selected phone APK

| Property | Qualified phone test artifact |
| --- | --- |
| Path | runs/wo3c-r1/gradle/app/outputs/apk/debug/app-debug.apk |
| SHA-256 | `2cb5f4597b732938105b3a6ca08e7a513d792d19fb4d59b16e2ae82fb8f3a717` |
| Bytes | 48,502,369 |
| Package / version | com.rjnr.pocketnode / 1.8.5 / code 27 |
| Min / target SDK | 26 / 36 |
| ABI | arm64-v8a |
| Required JNI | ARM64 light client and secp256k1 present; ELF64, little endian, machine 183 |
| Other native libraries | Every packaged .so has the correct ARM64 ELF architecture |
| Signer | Exact repository/installed debug certificate above; signature verifies using v2 |
| Debug source marker | b28979d present in packaged DEX |
| Production source modified | NO; pinned checkout remains clean |

`phone-artifact.json` records each native library's hash, ELF class/endian/machine, source/toolchain/build-input hashes and log hash. Receipt SHA-256: `d0f69fd873008f4ec528ddfe1427f4cfac43535f5b10177b4ff7de1bc77ea8ee`.

## Build provenance and reproduction

`scripts/p3c_r1_build_arm.ps1` adapts the pinned JNI script's ARM64 Cargo invocation to the available Windows host compiler/CRT setup. Rust 1.92.0, NDK 27.0.12077973, native API 21, locked Cargo dependencies, pinned source, `jni-bridge,portable` and the same Android stubs are used. BUILD_X86_64 is unset. `scripts/p3c-r1-build.init.gradle` redirects outputs and constrains test packaging to ARM64; it does not override signing or application behavior. Normal repository Gradle debug build logic supplies the stable signer and application code.

The initial loop completed ARM64 successfully and then began optional ARMv7 compilation. That build tree was stopped specifically after the required ARM64 output was secured; its files were retained, not deleted. The final artifact deliberately qualifies ARM64 for SM-S9180, not 32-bit devices. Final Gradle assembly succeeded. `arm-build.log` retains both phases; `stopped-optional-armv7-build.json` records the stopped task processes. Reproduce with the final build script; `-AndroidOnly` reuses the already built ARM64 libraries. This records reproducible inputs/commands, not a claim of timestamp-independent byte-identical rebuilds.

## Non-destructive overwrite and warning

`scripts/p3c_r1_overwrite.py` checks original installed APK identity, fixture public identity, V2 metadata, qualified artifact and compatibility before `adb -s R5CW6127VPR install -r --no-streaming`. Installation succeeded. Existing wallet/account IDs, paths, addresses and kdfVersion 2 remain unchanged. On normal launch Room migrated additively from version 15 to 17 with expected identity `091b40f9618fee3fc8032ff01255a9a4`.

Android displayed a debug compatibility warning: the APK is not 16 KB-aligned. The phone reports **4096-byte pages**. The warning was recorded and acknowledged with **OK once**; suppression was not selected. No source patch or authentication bypass was used. This artifact does not qualify native 16 KB-page execution. Warning evidence: `android-compatibility-warning.json`.

Pocket reached its normal authentication screen. Full wallet opening/native startup/restart qualification requires normal on-phone authentication; progress/results are recorded in the R1 decision and launch evidence. No mnemonic was entered, no new account/DAO/transaction was created and H2 was not activated.

The original x86_64 APK and immutable H2 hashes remain unchanged. This phone hash supplements their provenance and does not replace them.
