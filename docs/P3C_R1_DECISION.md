# WO-3C-R1 decision

**Artifact and payload/policy qualification PASS. Full non-destructive phone launch qualification is incomplete: normal authentication into the existing wallet is required. Control P-A must not begin yet.**

No H02 recovery failure occurred. Neither phone arm ran and H2 was not activated.

## Completed

- Official v1.8.5 release/tag match the pinned commit and expected APK SHA-256. ARM64 light-client and secp256k1 JNI are present, but its certificate differs from the installed signer. Official overwrite was not attempted.
- The repository stable debug certificate exactly matches installed Pocket 1.8.3: `bb4cbddbe25b03a1bac59f9c139f845b15869d0507198a9271103f3a64c96b9a`.
- ARM64 debug APK built from unchanged pinned Pocket/native source, normal repository signing and isolated test packaging. All native ELF architectures, version/package/SDK/source marker and signature pass.
- Qualified phone APK SHA-256: `2cb5f4597b732938105b3a6ca08e7a513d792d19fb4d59b16e2ae82fb8f3a717`.
- Signature-compatible `install -r --no-streaming` succeeded. Installed destination hash/profile checks pass. Pocket was not uninstalled or cleared.
- Existing wallet IDs, derivation/address/account relationships and kdfVersion 2 remain unchanged. Normal app launch applied registered additive Room migrations from 15 to 17 and produced the correct schema identity.
- Exact immutable H2 member/provenance/secret gates pass. All 11,378 native records use architecture-independent explicit encoding. No RocksDB, executable, raw native memory or unknown payload is present. Native snapshot transfer requires no ABI transformation; normal destination UUID reconciliation still applies.
- Separate phone destination tooling and ten offline acceptance/refusal checks pass. Original emulator validator/transport hashes and behavior remain unchanged.
- Android APIs establish a secure device lock and successful strong-biometric/device-credential capability. No credential was requested/extracted or authentication bypassed.

## Remaining non-destructive gate

Pocket reaches its ordinary locked authentication screen. No fingerprint button/system prompt is currently presented in that existing Pocket configuration. The user was asked to unlock Pocket directly using its normal flow, without sharing credentials. At the latest observation Home was not visible.

Full existing-wallet opening, active native light-client startup/public-state reconciliation and restart after normal wallet access are **NOT TESTED**. Successful installation, Room migration, public identity and V2 metadata checks do not substitute for that gate. There is no evidence of a Pocket authentication defect; the existing app authentication has not yet been completed.

Leave the existing installation/data intact. Do not switch security settings, inject authentication, recover keys, reset data or start either arm to avoid this gate. The next action is normal manual on-phone Pocket authentication, then completion of launch/native/restart checks within R1. If normal unlock cannot be completed, PM must decide whether to defer or revise qualification; R1 grants no reset exception.

## Android page-size warning

Android displayed a debug warning that native libraries are not 16 KB-aligned. Actual phone page size is 4096 bytes. The warning was acknowledged once with OK and remains enabled. No production code or security behavior changed. The APK reaches normal application authentication on this phone; 16 KB-page binary execution is not qualified. This is a packaging limitation, not an H2 payload architecture failure. Full native startup on this phone remains pending authentication.

## Trusted inputs for subsequent review

| Input | SHA-256 |
| --- | --- |
| Phone APK | `2cb5f4597b732938105b3a6ca08e7a513d792d19fb4d59b16e2ae82fb8f3a717` |
| Phone artifact receipt | `d0f69fd873008f4ec528ddfe1427f4cfac43535f5b10177b4ff7de1bc77ea8ee` |
| Cross-ABI audit | `b9adf7b0e47e86191808615d05d05b154311f00e1191bcb56c18b4d5cca26b05` |
| Original H2 manifest | `56d4a6506641c62797531eb0f093c4930131a9046d26351377c292568d7d879e` |

The later compatibility rule validates source provenance with the original emulator hash and independently validates the hash-bound ARM destination against the same Pocket commit/native tree, Room/native schemas, account/Script model, TESTNET/genesis and exact audited payload. The package is never resealed and the emulator gates are never relaxed.

No historical cleanup was performed. The optional ARMv7 build was stopped after ARM64 succeeded, and its generated files remain retained. H02 private material, historical evidence and original B1/B2/WO-3C reports remain unchanged. No mnemonic entry, account/DAO creation, transaction, app-data clear, H2 activation, production-source edit or D2 use occurred. Current H02 product boundary remains **POCKET FEATURE**; real-device recovery/security/signing acceptance is still ahead.

**STOP. Do not begin Control P-A automatically. Wait for PM review.**
