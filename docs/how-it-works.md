# How wallet-state recovery works

Waymark separates key recovery from state recovery. Normal wallet recovery restores signing authority and creates destination security. State-assisted recovery then restores selected prior scanning work and continues reconciliation with the chain. Pocket Node 1.8.5 is the implementation validated here; another wallet needs its own state model, importer and evidence.

## A coherent saved-state checkpoint

First establish a correct source wallet with settled discovery, known historical coverage, coherent per-Script/native/application progress, and no pending payment or DAO actions. Independently check its canonical chain anchor and exact wallet state. Stop the whole application process and disable the package before extraction; stopping only the embedded node/service is insufficient because native globals can retain database handles.

Pocket's Room database mixes public metadata and encrypted key material. Copying it to a host and deleting key rows can leave ciphertext in free pages, WAL or temporary files. Instead, a standalone Android helper selects explicit public fields inside the stopped source sandbox. It reads committed SQLite WAL state and constructs new logical output. It never loads Pocket's Application or starts its light client.

The native SQLite store is separate. Copy its approved logical rows into a fresh SQLite database rather than copying only its main file while ignoring WAL. Room, native state and preferences are separate stores, so identity and cursor consistency must be checked across them. Exporting just a high cursor without the transactions, indexes and checkpoints it describes could skip required scanning.

## Saved-state package

Exactly three regular files are admitted; symlinks, extra files, nested members and sidecars are refused.

| Member | Preserved content |
| --- | --- |
| `manifest.json` | Format/profile, source commit and native tree, app version/code, source APK digest/ABI, Room schema/identity, native schema, network/genesis, saved height/hash, coverage floors, full packed Scripts, progress, capture method, omissions, payload sizes and SHA-256 hashes. |
| `app.json` | Public wallet IDs, type, derivation path, parent/account relationships and addresses; per-account sync progress; genuine discovery candidate identities/states/coverage; selected non-security sync preferences; count-derived settled/migration/key-presence checks. |
| `native.sqlite` | Fresh logical `kv(key BLOB PRIMARY KEY,value BLOB)` snapshot containing native transactions, live Cell and history indexes, headers, filter checkpoints, registrations, progress and admitted persisted work. |

The tested profiles admit one mnemonic parent account or that parent plus derived account 1, with distinct secp256k1-blake160 lock Scripts, TESTNET and `ALL_WALLETS`. The fixture has an empty mnemonic passphrase. Arbitrary accounts, networks, pending actions or changed builds are outside the retained policy.

Wallet projection fields are `walletId`, `type`, `derivationPath`, `parentWalletId`, `accountIndex`, `mainnetAddress`, `testnetAddress`. Progress records bind wallet/network to `lightStartBlockNumber`, `localSavedBlockNumber`, `updatedAt`. Candidate records bind parent/path/index/Script args to state, creation time and registered-from height. They have no network column, so this profile does not infer cross-network discovery completeness.

Selected preferences are network, sync strategy, active wallet, and each owned wallet's testnet sync mode/custom height, initial-sync flag, zero-Cell-rescan flag and gap-limit flags. An unset sync strategy is normalized to Pocket's effective `ALL_WALLETS` default. Missing selected source flags restore defaults; unrelated destination preferences remain intact. An initial-sync flag is a policy value, not proof of complete history.

The native admitted prefixes are 0 (transactions), 32/64 (lock/type live indexes), 96/128 (history), 160/192 (headers and block mapping), 208 (filter checkpoints), and 224 (enumerated metadata/work). Required metadata includes genesis, chain state, recent headers, max checkpoint and minimum filtered height. Recent headers contain zero or more 40-byte number/hash pairs. These structural checks and funded-fixture dataset guards cannot prove historical non-omission.

## Security and trust boundary

Never transfer the source mnemonic, seed, private keys, PIN/hash/salt, Android credential, Keystore objects, authentication/session/migration state, encrypted key rows, legacy encrypted preferences or PIN-encrypted key backups. Encrypted signing material remains secret material: a PIN-protected backup can be attacked offline. Neither encryption nor an excluded Android backup path makes it acceptable state-package content.

Raw source Room/WAL/SHM files, generic SQL dumps, peer identity, pending signed broadcasts/reservations, pending DAO actions, logs, APKs, arbitrary files, contacts and free-form labels/notes are excluded. The package omits application transaction, balance, header and DAO caches; normal reconciliation rebuilds them.

Structural selection is the primary protection. The host also refuses known secret structures, backup/Keystore magic, private-key formats, extended private keys and twelve consecutive BIP39 dictionary words. This is bounded pattern detection, not forensic proof: an unlabelled random secret can resemble a hash. Public chain content can also trigger conservative refusal.

Retain the manifest digest, expected APK digest and genesis independently. Hashes inside an editable package cannot authenticate themselves. The destination trusts the source's pre-checkpoint work and chain state; SQLite integrity and authenticated provenance do not prove complete historical scanning. Stored account associations are privacy-sensitive despite being non-secret. Export output remains under ignored local `runs/`, with restricted Windows ACLs (current user, SYSTEM and Administrators) or 0700 permissions. No cloud or encryption protocol is implemented.

Pocket sets `allowBackup=false` and explicitly excludes key backups and selected security preferences in its extraction rules. That is not a blanket guarantee about every Android/OEM transfer path. This research's selective export is the relevant boundary.

## Destination reconstruction and activation

Normal recovery first creates fresh destination wallet UUIDs, account relationships, encrypted key rows, PIN and Android Keystore protection. The package supplies no key authority. Recover the parent and use the supported Add account flow for the second account; do not inject wallet/key rows.

Decode addresses with checksum/network checks and compare full packed Scripts together with derivation paths and account indexes. Check exact parent and candidate identity matches. Translate source public UUID references to the destination's existing UUIDs; source IDs never replace destination key IDs.

After package validation, stop and disable the destination and inspect its public state. Stage an internal copy of the **destination's** Room files inside its own sandbox, modify only approved metadata/progress/discovery and selected preferences, clear rebuildable testnet caches, and install the native snapshot. Internal destination key-byte digests must remain identical. Those stage/original files contain destination ciphertext and must never be pulled, packaged or tracked.

Stage records live-file hashes and absence. Commit refuses a changed baseline before journaling or replacement. A durable journal, retained originals and file/directory fsync support rollback after interruption. The app remains disabled on failure. Explicit enable refuses an outstanding journal and does not launch Pocket. This is a research filesystem protocol, not a production wallet importer.

Normal startup then reconciles with peers and rebuilds application projections. Pocket's registration/discovery policy matters: registration can replay historical work, and `ALL` registrations are not protected by a partial-rewind clamp. Genuine settled discovery state and explicit coverage prevent misleading resume assumptions. Default `RECENT` coverage (200,000 blocks) omitted the fixture's older activity; the proofs used explicit historical floors instead.

Pocket starts its embedded node during application initialization and registers a recovered account before showing the post-import sync picker. An explicit resync rewinds scanning; invoking it after restoration merely to configure the UI can undo continuation work. A current registration start or Room `lightStartBlockNumber` is a resume value, not necessarily the original historical birthday, so the manifest retains coverage floors separately.

Mnemonic import creates ten account-axis and 41 chain-axis public discovery candidates. They are not recovered signing accounts. Discovery `EMPTY` uses heuristic coverage/tip conditions, not a universal absence proof; no fixture candidates were fabricated or advanced to produce a timing win. `ALL_WALLETS` caps simultaneous owned-wallet registrations at three, and candidate registrations are additional. This two-account proof does not qualify arbitrary unknown-account discovery or passphrase-backed sub-account families.

DAO positions are derived from lock-Script history and typed Cells. Partial cached headers or an `OUTSIDE_WINDOW` cache row cannot establish present live status, maturity or authority. The proof rebuilds DAO caches and checks exact canonical position rather than importing those assertions. A broader feature must separately handle pending broadcasts, reservations and withdrawal/unlock markers so restoration cannot replay old user intent.

## Compatibility and rejection

The retained policy pins Pocket source, native tree, 1.8.5/code 27, Room 17 and its identity hash, SQLite KV schema/user version 0, x86 source capture, exact APK, TESTNET/genesis and one/two-account profile. It checks payload integrity, JSON keys/types/duplicates, native schema/integrity/free/trailing pages, key families, required metadata, Scripts and cursor consistency. Coverage must reach the declared boundary and not exceed corresponding native progress. It refuses synthetic packages for device restoration.

These checks precede destination mutation where possible. Recovered destination accounts/candidates, settled pending state and completed migration must also match. Canonical checkpoint/hash and full wallet semantics need independent acceptance checks beyond package policy.

The phone proof used a separate destination policy: preserve original x86 package provenance and independently qualify the ARM APK against the same source/schema/network and audited native encodings. It did not substitute a phone hash into the manifest or loosen the retained x86 validator. This qualification establishes the exact tested payload's compatibility, not arbitrary cross-version or cross-backend portability.

## Retained reference tooling

| File | Responsibility and limits |
| --- | --- |
| [state_package.py](../tools/state_package.py) | Existing strict validator/sealer and restore-plan functions; standard-library host code. Its CLI validates a supplied package; `PACKAGE_POLICY_PASS` is not wallet recovery acceptance. |
| [pocket_sandbox.py](../tools/pocket_sandbox.py) | Existing emulator-only `export`, `stage`, `commit`, `rollback`, `enable` transport. Requires explicit serial, named API-36/x86_64 AVD, debuggable Pocket and exact installed APK. It refuses physical devices and never launches Pocket. |
| [PocketStateSandbox.java](../tools/android/PocketStateSandbox.java) | Standalone public projection/logical snapshot, destination staging/key invariants, public observation, journaled activation and rollback. No network, key derivation, signing or UI logic. |
| [build-state-helper.ps1](../tools/build-state-helper.ps1) | Compile/dex the helper against Android API 36 with bytecode 17/minimum API 26; output under ignored `runs/state-helper`. It does not build Pocket. |
| [bip39-english.txt](../tools/bip39-english.txt) | Public reference dictionary for conservative secret-pattern refusal. Attribution is in [third-party notices](../tools/THIRD_PARTY_NOTICES.md). |

The Windows transport expects Android SDK under `%LOCALAPPDATA%/Android/Sdk`; the compiler wrapper expects Android Studio JBR under `C:/Program Files/Android/Android Studio/jbr` and build-tools 36.0.0. The public AVD guard is now `Pocket_State_API36_X64`; configure a dedicated disposable lab AVD with that identity. Historical device names, class names and binary digests belong to the sealed records, not to a newly built renamed helper. Existing transport buffers payload/base64 bytes and is not qualified for large-database streaming.

Use `python tools/state_package.py --help` and `python tools/pocket_sandbox.py --help` to inspect the existing command surface. No high-level recovery CLI has been added. The retained host tests are the offline entry point shown in the [README](../README.md).

The [optional Android integration test](../tests/test_android_state_helper.py) exercises generated Room/native/WAL canaries, default preferences, staging/commit, changed-baseline refusal, interrupted activation/rollback and destination key/PIN preservation. It requires a dedicated running API-36/x86_64 emulator on explicit `emulator-5580`, named as above, **with Pocket absent**, the newly compiled helper, and Pocket's pinned Room-17 schema at `repos/pocket-node/android/app/schemas/com.rjnr.pocketnode.data.database.AppDatabase/17.json`. That upstream checkout stays ignored. The test operates only on synthetic `/data/local/tmp` files. It was not executed during presentation cleanup; no phone or wallet operation is needed for the offline suites.

## Evaluating another wallet

Identify the wallet's authoritative keys, derived public state, local intent and device security. Design explicit allowlists and a coherent stopped-process snapshot; specify separately how pending actions and metadata outside this settled fixture would be handled. Bind supported versions, storage encodings, network and accounts before import. Preserve independently recovered destination security and let the chain resolve stale state.

Use independent normal-recovery and state-assisted destinations with a disposable fixture, activity after backup, exact canonical live Cells/history/ownership/coverage, real destination signing and restart checks. Include source/export and import costs and repeat under controlled conditions before making performance claims. A maintainer would still need supported import/export UX, privacy protection, recovery failure handling and version maintenance. Pocket's proof supplies evidence for this pattern, not compatibility certification for another wallet.
