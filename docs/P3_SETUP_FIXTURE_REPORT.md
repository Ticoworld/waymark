# WO-3 setup: disposable Pocket fixture

Date: 2026-10-05. Setup and read-only investigation only. No emulator wallet import, transaction, full-history sync, state-package restore or A/B timing was run.

**Result:** the existing phone contains the original D2 Pocket test fixture. Its recovery material has been recovered and independently matched to its public identities. Reuse it on TESTNET. Existing funds suffice, but the current fixture has only one populated Script and no DAO position: it does not yet satisfy the accepted two-account/DAO benchmark contract.

The latest PM instruction authorizes this disposable phone and private secret acquisition, superseding the earlier P1/P2 prohibition on those specific operations. It does not change the sanitized Candidate B package policy. D2 is a historical identity reference only; no D2 artifact or integration enters the experiment.

## Physical phone and installed application

| Fact | Observation |
|---|---|
| Explicit ADB serial | R5CW6127VPR |
| Model / OS | Samsung SM-S9180; Android 16, SDK 36 |
| Package / sandbox | com.rjnr.pocketnode; /data/user/0/com.rjnr.pocketnode |
| Version | 1.8.3, versionCode 25; minSdk 26 / targetSdk 35 |
| Debug / access | DEBUGGABLE; run-as works; UID 10364 (u0_a364) |
| Installed APK SHA-256 | 13441d8d5904ff0480415b557642c57f594d308b87261794a29eb34f8a14ea98 |
| Room version | 15; therefore incompatible with the WO-2 schema-17 package contract |
| Selected network | TESTNET |
| Wallets / sub-accounts | One mnemonic parent, account 0; no sub-account records or discovery-candidate records |
| Process state | Pocket was already stopped; remained stopped throughout inspection. No force-stop, launch, disable, install, uninstall, clear, preference edit or helper deployment on the phone |
| Integrity of acquisition | Before/after SHA-256 agreement for every acquired source file, and a final repeat check after all investigation. No app/native/backup file bytes changed |

The installed APK hash equals the historical `_work/g3-1-pocket-node/android/app/build/outputs/apk/debug/app-debug.apk` hash. This establishes artifact identity; do not describe it as an unmodified v1.8.5 release build. The historical G3 source pin is `6eda0b7a4601050b011591d41cc702f0dc7a7c38` with that experiment's documented build context.

## Secret custody and verification

Private fixture: `C:/Users/timot/Desktop/2026/CKB/H02-P0/private/pocket-disposable-fixture.json`.

The directory is Git-ignored, with inheritance removed and access granted to the local user, SYSTEM and Administrators. These ACLs are local access control, not encryption at rest. Nothing beneath `private/` is committed or admitted to a Candidate B package.

The wallet has a V2 Room key row and a PNBK format-2 backup. The historical supported reveal flow calls `WalletSettingsViewModel.loadSensitiveData(activity)` and `WalletKeyReader.readKeyMaterial`, requiring authenticated key access. To leave the stopped app untouched, acquisition used the user's authorized option B: read its existing backup through run-as, then decrypt locally using the known app PIN supplied once in a masked local dialog. No PIN guessing, authentication downgrade, key replacement or phone unlock bypass occurred. The acquisition helper did not read PIN preferences or Android Keystore material.

`p3_fixture.py` reproduces the inspected historical `data/wallet/KeyBackupManager.kt` PNBK decoder: Argon2id v19, 64 MiB, three iterations, four lanes, followed by AES-256-GCM authentication. PIN input is not stored by the helper. Raw encrypted acquisition files and any diagnostic scratch data stay under `private/`; they are not the state package. Working SQLite copies were opened read-only, preserving the captured main/WAL pairs and the original phone files.

Before saving, the helper checked BIP39 checksum; derived `m/44'/309'/0'/0/0` with empty passphrase; matched that derived private key to the backup's private-key field in memory; and matched its compressed public key/CKB Script to both stored network addresses. The saved fixture retains only the mnemonic and necessary recovery/public provenance metadata, not a duplicate derived private key or PIN. A subsequent separate `verify` invocation also returned MATCH. Account 1 was derived publicly for planning only; it was not created in Pocket.

| Public identity | Value |
|---|---|
| Wallet UUID | e3fe1cfc-cd01-49f9-bbe0-b2fd19c661d8 |
| Path | m/44'/309'/0'/0/0 |
| Compressed public key | 0x02fd4cef263d5b9cf7c75a6050fa481ab6f4294d3f04455874a072b0231dc94eb4 |
| Lock code hash / type | 0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8 / type |
| Lock args | 0xbc5882c4309431ee23ad7bbad4b5c3325539eebd |
| Script hash | 0x4cff5ae9aa82be7814fc9c058a09098bed951a71aa1b8971518446d0a724568d |
| Mainnet address | ckb1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdutzpvgvy5x8hz8ttmht2ttsej25u7a0gs3stp0 |
| Testnet address | ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdutzpvgvy5x8hz8ttmht2ttsej25u7a0g7rmyth |

Proposed account 1: path `m/44'/309'/1'/0/0`, args `0x2da024570462b0e2421d87abcbfebd4567d52ad5`, Script hash `0x29958c7362d950f80cdb5994d47e408b38a4d2cc5e41f7a0087214ff3f421a24`. Its testnet address is `ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqfd5qj9wprzkr3yy8v8409la029vl2j44g8qpweu`. Public queries found no history/Cells on either network. This is not a claim to have exhaustively searched all possible derivation paths.

## Relationship to D2

Classification: **SAME D2 POCKET FIXTURE**.

The historical source Room DB was opened with `mode=ro&immutable=1`, without replaying experiments or touching WAL state. It contains the identical UUID, path and both addresses. The historical native source contains both funding transactions below, and the execution report records the identical packed lock Script. The current installation also retains the later D2 self-transfer. These are stronger evidence than device/version identity alone.

Historical references (read-only):

- `../ckb-script-port/docs/G3_1R1_POCKET_EXECUTION_EVIDENCE.md`.
- `../ckb-script-port/_work/g3-1-pocket-node/_g3-1r1-evidence/pocket-testnet-real-room-source-1.db`.
- Same directory, `pocket-testnet-real-pocket-source-1.db`.
- Historical boundary H = 22,370,055, hash `0x46c067702c9b8b9e4d633679bbdc8015914862f1b37fbe0cb0333ec04f08bdbf`. This is **not** the future H02 backup boundary.

## Separate chain inventories

Read-only public observations came from `https://testnet.ckb.dev` and `https://mainnet.ckb.dev`, starting 2026-10-05 14:13:35 UTC. Each query checked genesis/indexer tip, paginated exact-Script Cells and transactions, fetched transaction bodies/activity headers, and checked every returned outpoint with `get_live_cell`. All three testnet outpoints returned live. Initial requests with the default Python user-agent failed; an explicit inspector user-agent succeeded. No signing or broadcast method exists in the query helper.

These are public RPC/indexer observations, not a cryptographic proof of historical completeness or absence. The phone's native state independently agrees on the three known testnet transactions and three live outpoints through its older cursor. The future experiment must recheck canonical facts and use local verifier observations for acceptance.

| Observation | TESTNET | MAINNET |
|---|---|---|
| Genesis | 0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606 | 0x92b197aa1fba0f63633922c61c92375c9c074a93e85963554f5499fe1450d0e5 |
| Public query final tip | 22,642,926 | 20,647,822 |
| Unique primary-Script transactions | 3 | 0 reported |
| Live Cells | 3, all untyped with empty data | 0 reported |
| Total / plain live capacity | 1,999,999,999,000 shannons = 19,999.99999 CKB | 0 |
| DAO positions | 0; no typed live Cells and no DAO transactions among the three matches | 0 observed |
| Known populated owned Scripts | 1 | 0 |
| Phone native Script progress | 22,632,491 | 20,411,782 |
| Phone Room saved progress | 22,632,491 | 20,411,782 |
| Phone saved sync mode | NEW_WALLET | NEW_WALLET |
| Phone lightStartBlockNumber | 22,583,073 | 20,411,634 |

Default sync strategy is ALL_WALLETS when its preference is absent. Each native store has one lock-Script registration matching the primary identity; no other registered Script was observed. Room holds three confirmed testnet history records, one testnet balance cache, no DAO rows or pending broadcasts/DAO withdrawals. Cached transaction timestamps are zero: use canonical header timestamps, not this cache, for fixture age.

Earliest known activity: block **22,369,938**, 2026-09-10 07:10:02.731 UTC. Latest known activity: block **22,370,275**, 2026-09-10 07:52:27.142 UTC. Thus there are three transactions about 25 days old, not a dense historical wallet; roughly 273,000 blocks separate the first activity and the observation tip. No speed result follows from that span.

| Transaction | Block | Role |
|---|---:|---|
| 0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66 | 22,369,938 | Original funding; output 0 remains live |
| 0xb7503283af42a8fd1595306e2d5dd4a789e103980207fdafb5229b2e20b7113c | 22,369,943 | Second funding; consumed by the self-transfer |
| 0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894 | 22,370,275 | Self-transfer; outputs 0 and 1 remain live |

| Live outpoint | Capacity (shannons) |
|---|---:|
| 0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66:0 | 1,000,000,000,000 |
| 0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894:0 | 100,000,000,000 |
| 0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894:1 | 899,999,999,000 |

The keys are verified and these are ordinary live Cells, so the capacity is available for disposable fixture spending, subject to normal fees/transaction validation. No spend was executed to demonstrate it. Same key/Script on MAINNET does not carry any TESTNET funds or history across networks.

## Automation readiness and limits

- `scripts/p3_phone_snapshot.py`: narrowly pinned, stopped-phone read-only acquisition; secret-bearing captures only in `private/`; allowlisted public metadata reporting. It does not change the WO-2 emulator-only transport guard.
- `scripts/p3_fixture.py`: private PNBK acquisition, public verification and prospective account derivation. Four synthetic tests pass, including both PNBK KDF versions, wrong credential, corrupt/truncated/unsupported backup refusal, checksum and identity mismatch.
- `scripts/p3_public_chain.py`: repeatable read-only network inventory; no secret inputs.
- `scripts/helper/H02FillPhrase.java` and `scripts/p3_fill_phrase.py`: compiled emulator-only normal-screen phrase entry. Uses accessibility ACTION_SET_TEXT, not secret command arguments, clipboard or text-injection logging paths. No UI dump, screenshot, app launch or import submission. Temporary secret transport stays in the emulator app-private sandbox and is removed in cleanup. Host tool captures/suppresses raw runner output and prints fixed status only.
- Helper SHA-256: `b75bc7f53c7605dca3dc2b280d42ad58e4bbfa430eaa9ee08726b898b3f29e25`. **Compiled but not run against Pocket.** Selector compatibility and API-36 legacy UiAutomator execution must pass an untimed source preflight. Navigation, sync selection, account-1 creation and emulator PIN setup remain to be exercised; do not claim a completed automatic Android recovery.
- No repeated user phrase entry is required by design. Source/control/candidate will use identical emulator security configuration and normal Pocket flows. Existing default no-device-lock emulator permits Pocket's supported, consented V1 Keystore fallback; any chosen V2 device-credential profile must be identical in both arms and automated with emulator-only credentials. Do not reuse or persist the physical phone's PIN for this.
- Existing 33 WO-2 package tests still pass, including physical-device refusal and all secret-exclusion tests. Non-fatal synthetic SQLite ResourceWarnings were emitted. Pocket source remains clean at v1.8.5.
- `scripts/p3_audit_private.py` passed an actual-fixture leak check across experiment documents, scripts and the new public/generated setup outputs. It checks mnemonic sequences and derived private-key bytes/hex without emitting those values, plus Git exclusion. This is a scoped content check, not perfect forensic secret detection or secure memory erasure. The fixture file inherits the restricted private-directory ACL.

Public observations are in ignored `runs/wo3-setup/phone-public.json`, `phone-chain-public.json`, `fixture-public-verified.json`, `installed-apk-public.json`, `testnet-public-rpc.json`, `mainnet-public-rpc.json`, and `account1-query/`. Private acquisition/analysis directories are deliberately separate. The actual fixture mnemonic never appears in these public outputs.

**Setup verdict: GO for PM review.** Recovery material and public fixture identity are ready. Timed A/B execution still requires PM approval, source UI-automation preflight, second-account/DAO preparation, complete acceptance observation tooling, and a settled same-version source boundary. No external funding or replacement primary wallet is currently needed.
