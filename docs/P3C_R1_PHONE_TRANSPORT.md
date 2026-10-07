# WO-3C-R1 separate phone destination transport

`scripts/p3c_phone_destination.py` implements a separate Samsung policy. Original `h02_device.py` and `h02_package.py` remain unchanged: source validation still requires the original x86_64 APK/capture profile.

## Gate ordering

1. Verify trusted hashes of the artifact receipt and cross-ABI audit, then the actual local APK hash.
2. Require pinned commit/native tree, package `com.rjnr.pocketnode`, 1.8.5/code 27, Room 17/identity, native SQLite KV schema and TESTNET/genesis.
3. Require ARM64 light-client/signer JNI, debuggable transport and certificate `bb4cbddbe25b03a1bac59f9c139f845b15869d0507198a9271103f3a64c96b9a`.
4. Re-run exact source-code/payload audit and unchanged source validator. Never substitute the destination hash for source provenance.
5. For installed checks require allowlisted serial `R5CW6127VPR`, physical Samsung SM-S9180, API 36, arm64-v8a and exact destination APK hash. Reject emulators.

R1 CLI provides validation/read-only installed checks only. Future PM-authorized Candidate code must explicitly enable execution for stage/commit/rollback/enable; default refusal occurs before mutation. R1 never invokes activation.

## Prepared activation

PhoneDevice reuses sandbox transfer/digest/stopped-process operations and deploys the hash-bound B2 Java/Dex helper, which has no JNI dependency and does not load Pocket's Application. Before staging, normal destination recovery must satisfy strict account/path/Script checks. Original restore-plan logic remaps only approved logical state to destination IDs.

The helper copies destination Room/security state locally, modifies allowlisted progress/discovery/sync fields, clears rebuildable TESTNET caches, installs exact native bytes, and verifies the destination key-material digest remains unchanged internally. No key/ciphertext values cross the transport boundary. No source Keystore/PIN/security flags are imported. Journaled activation/rollback, quiescence and disabled/stopped checks remain intact.

Real-phone staging, activation durability and authentication preservation are **not executed or claimed by R1**. They remain Candidate acceptance after PM review. P-A must first complete and seal evidence before Pocket-only reset/P-B. The DAO reader defect stays separate.

## Read-only security/state probe

`scripts/phone-helper/H02PhoneReadOnly.java` and `scripts/p3c_r1_probe.py` query public wallet/address/DAO/progress/balance fields and kdfVersion using READONLY SQLite handles. No decryption, credentials, Cipher, authentication, wallet migration or state activation occurs. A hash-verified read-only helper jar resides at an H02-specific `/data/local/tmp` path.

KeyguardManager/BiometricManager report secure lock and successful strong-biometric and strong-biometric-or-device-credential capability checks (code 0). This establishes capability, not signing authentication. Existing wallet kdfVersion is 2. Genuine later prompts remain under user control.

Evidence and final receipt/audit digests are under `runs/wo3c-r1`. No mnemonic entry, data clear, transaction or H2 activation is authorized by this preparation.
