# WO-3C-R1A phone launch qualification

**R1-PASS.** Normal on-phone user authentication, ARM64 light-client execution and one cold restart pass. The user confirmed authentication again after relaunch; the post-restart Home screen and preserved wallet/native state were independently observed before that confirmation. Artifact, signer, cross-ABI and phone-policy qualification are accepted from R1 and have not been repeated. No Control/Candidate recovery, H2 activation, reset, signing test or transaction occurred.

## Read-only observations

The existing Pocket process is running on Samsung SM-S9180, serial R5CW6127VPR. The accepted version is 1.8.5/code 27; phone artifact SHA-256 is `2cb5f4597b732938105b3a6ca08e7a513d792d19fb4d59b16e2ae82fb8f3a717`. Its accepted unchanged signer is `bb4cbddbe25b03a1bac59f9c139f845b15869d0507198a9271103f3a64c96b9a`.

`runs/wo3c-r1a/phone-pre-unlock.json` records an executable ARM64 light-client mapping in Pocket PID 20996. Android maps the library directly through base.apk; the observation resolves the APK member offset and its executable ELF PT_LOAD segment, rather than relying on a library basename in /proc maps. ELF machine 183 identifies AArch64. This is a running-process observation, not a new artifact qualification.

The existing TESTNET Script registration remains present. Its saved native progress was 22,654,994 before the unlock observation, compared with 22,652,000 in the prior R1 after-overwrite capture, then 22,655,047 at the unlocked capture. Room progressed with the native state. The initial retained log buffer had no matching startup-success event for that old process; fresh explicit JNI initialization/start success was subsequently captured during restart.

The read-only projection matches the prior wallet UUID, account 0 path, public addresses and kdfVersion 2. Room schema 17 and identity `091b40f9618fee3fc8032ff01255a9a4` remain coherent. No later B2-oracle balance equality is required in this upgrade/startup gate. secp256k1 JNI is not presently mapped; no signing/key-touch operation was requested, and this is not a signing qualification.

The restricted lifecycle/error log summary contains no observed UnsatisfiedLinkError, skipped light-client load, native-init/start failure, fatal Java exception, migration error or selected authentication/Keystore exception. This describes only the available buffer, not an end-to-end authentication result. No raw log output, UI hierarchy, editable input or credential is retained by the R1A observer.

## Authentication and restart gate

The user reported Pocket open after being asked to authenticate directly on the Samsung. The read-only initial UI observation found Pocket's Wallet/Activity/Testnet labels without an auth screen. The first tag-only detector found no Home tags; that negative detector result is retained and is not an authentication failure. The later post-restart observations identify `home-balance-row` and `home-peers-shortcut` explicitly. A credential supplied in chat was not used or copied into project files, tool inputs or evidence.

One Back action closed the foreground app, followed by a Pocket-only force-stop to guarantee a cold process boundary. No storage was cleared. The old PID 20996 was verified absent before a single normal MainActivity launch; the new PID is 29656. The restart action is recorded in `restart-action.json`.

The new process emitted exactly one matched `Initializing embedded node for TESTNET` and one `Node started successfully on TESTNET` lifecycle event. In the pinned `NodeLifecycle.kt`, the latter event is emitted only after `nativeInit` and `nativeStart` return successfully. The ARM64 executable light-client mapping was present again. Script progress was 22,655,064 in the first restart observation and 22,655,077 in the settled observation. This proves native initialization, native execution and continuing public state on the real ARM device.

Both post-restart UI observations show Home and no auth screen. Wallet identifiers, account path/addresses, V2 key metadata and Room 17 identity match the original accepted phone projection after restart. No observed native-init/start failure, UnsatisfiedLinkError, skipped load, fatal Java exception, migration error or selected Keystore/authentication exception occurred in the new-process filtered buffer. R1A does not exercise signing or an authenticated Keystore Cipher; those remain part of WO-3C.

The user confirmed that they authenticated again after relaunch. Authentication completion is supported by that direct user confirmation and the independently observed post-restart Home screen. The credential, exact input and prompt contents were not captured. This does not establish a CryptoObject-bound Keystore operation or signing readiness; WO-3C must still prove those using its authorized signing tests. No agent credential input or authentication bypass occurred. No additional phone check followed the user's request not to check again. Control P-A is qualified to begin under the next PM work order and was not started here.

## Page-size follow-up

A read-only `getconf PAGESIZE` returned **4096**. The previously observed Android 16 KB alignment warning is a separate Pocket/native packaging follow-up and does not block H02 on this device. No 16 KB-page execution support is claimed and no production patch was made.

**R1-PASS. Can WO-3C Control P-A begin: YES, following PM review.** Normal user authentication, native/startup/metadata and cold-restart observations pass. No authentication, native or upgrade failure was observed. D2 was not used. Pocket data remains intact. The initial incomplete checkpoint is retained under `runs/wo3c-r1a/pre-unlock-checkpoint`; the original R1 documents/manifests remain unchanged historical evidence. This report completes their previously pending launch gate.

**STOP. Wait for PM review. Do not begin Control P-A automatically.**
