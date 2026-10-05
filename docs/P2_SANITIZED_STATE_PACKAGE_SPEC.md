# WO-2 sanitized state package, version h02-p0-v1

Scope: test-only, trusted-self, Pocket v1.8.5 at b28979de744798ffb75367b031d4871ec3af1a12; LC tree 3ac3e0ce1f4e46897d188b76c5b841b9097fa506; Room 17 / 091b40f9618fee3fc8032ff01255a9a4. No D2. This is an experiment profile, not a supported Pocket backup format.

The first profile is deliberately limited to TESTNET, ALL_WALLETS, one empty-passphrase mnemonic parent and account 1, two distinct populated secp256k1-blake160 lock Scripts, and no pending payment/DAO actions. Normal key/account recovery must already have run on the destination. Other networks, account types, extra wallets, changed builds and unknown fields are refused. A trusted expected testnet genesis hash and exact APK SHA-256 must be supplied independently by the operator; they are not learned from the package being validated.

## Files and included data

Exactly three files are permitted. No archive extraction, symlinks, sidecars, nested paths or arbitrary extra members are accepted.

| File/dataset | Exact allowed content | Why it is included |
|---|---|---|
| manifest.json | format, kind, Pocket commit/version/code, LC tree, Room version/identity, native SQLite/KV schema and user_version 0, ABI x86_64, capture method/explicit omissions, all native registration cursors, exact APK digest, TESTNET/genesis, boundary height/hash, coverage starts keyed by source wallet ID, exact packed lock Scripts keyed by wallet ID, byte lengths and SHA-256 of the other two files | Pin the compatibility/trust context; detect incomplete transfer; bind metadata to the expected identities and declared coverage |
| native.sqlite | A NEW SQLite database with only `kv(key BLOB PRIMARY KEY,value BLOB)`, filled from the frozen native store's logical rows | Retain transactions, Script indexes, chain headers, filter checkpoints, registrations/progress and persisted matched work together, without carrying arbitrary source file free pages |
| app.json: wallets | walletId, type, derivationPath, parentWalletId, accountIndex, mainnetAddress, testnetAddress | Translate public source identity to freshly recovered destination UUIDs. Addresses are decoded with checksum/network checks and compared as full packed Scripts; source IDs never replace destination key IDs |
| app.json: progress | walletId, network, lightStartBlockNumber, localSavedBlockNumber, updatedAt | Prevent multi-wallet startup policy from treating recovered accounts as unsynchronized. Room saved progress must not exceed the matching native cursor |
| app.json: candidates | parentWalletId, derivationPath, accountIndex, scriptArgs, state, createdAt, registeredFromBlock | Preserve genuine account discovery state and coverage. Destination-derived candidate public identities must match. Unknown/extended candidates absent on destination cause refusal in this profile |
| app.json: prefs | selected_network, sync_strategy, active_wallet_id; each owned wallet's TESTNET sync_mode, custom_block_height, initial_sync_completed, zero_cell_rescan_done, gap_limit_signal, gap_limit_banner_dismissed when present | Preserve explicit coverage/registration policy and avoid unnecessary reset behavior. initial_sync_completed is a policy flag, not historical completeness evidence |
| app.json: checks | schema, identity, migrationReady, pendingFree, keysPresent | Capture source schema and settled-state prerequisites. keysPresent is a count-derived boolean only; no secret column is exported. These are test preconditions, not proof of signing authority |

The helper's `W`, `P`, `C` and `SUFFIX` constants in scripts/helper/H02State.java are the on-device extraction allowlist. scripts/h02_package.py independently enforces the complete JSON schema. There is no `SELECT *` export. The only `SELECT * FROM key_material` is an internal destination-only digest comparison during staging, whose bytes and digest are never exported or printed.

Native key families are 0, 32, 64, 96, 128, 160, 192, 208 and 224. Metadata names are explicitly enumerated. Checkpoint indexes are u32: prefix-208 keys are five bytes, MAX_CHECK_POINT_INDEX values four bytes (storage/mod.rs:282 and sqlite.rs:496 at the pin). This detail was established while implementing the validator. The validator checks SQLite integrity, schema objects/columns, no freelist pages/trailing data, expected genesis, required native metadata, owned registrations and progress. Candidate packages additionally require transaction/header/live-cell/history dataset presence for the funded fixture. These are coarse completeness guards; they do not prove transaction closure or historical non-omission.

LAST_N_HEADERS consists of zero or more 40-byte number/hash pairs; the source legitimately writes an empty list during genesis initialization. The helper and validator preserve that empty value, refuse malformed lengths, and reject empty values in the other admitted native records. Synthetic fixtures exercise this actual layout detail.

## Regenerated and excluded data

| Excluded material | Normal destination treatment / reason |
|---|---|
| Mnemonic, private key, passphrase, disposable fixture signing credentials | User enters independently retained recovery material through Pocket's normal supported flow. Never supplied to this tooling |
| All source key_material columns/rows, including encryptedPrivateKey, encryptedMnemonic, iv, walletType, mnemonicBackedUp, updatedAt, kdfVersion | Fresh normal recovery creates destination Keystore-bound rows. Tooling never imports source key records or rewrites destination key values |
| files/key_backups, PNBK blobs, PIN hash/salt, ckb_pin_prefs.xml | New destination PIN/security setup; Pocket may generate its own local PIN backup through normal behavior. No source encrypted signing material is transferred |
| Android Keystore objects/aliases, legacy key preferences, key_migration.xml, authentication/session state | Recreated through normal destination security setup; device-bound ciphertext is not portable state |
| Raw source Room DB, WAL/SHM, SQL dump or whole sandbox | Never pulled off-device. Public rows are selected inside the frozen sandbox into a fresh JSON representation |
| Native peer/network directory, secret_key, connections, runtime handles | Regenerated by the destination; only the native store's approved logical rows are retained |
| balance_cache, header_cache, dao_cells | Rebuilt from native data and normal peer reconciliation. Cached DAO status or a partial cached header is not authority |
| transactions cache | Omitted in this first implementation. Rebuild activity from native history; any extra candidate replay caused by the absent earliest-transaction cache counts in B's timing |
| pending_broadcasts, pending_dao_withdraws, pending_dao_unlocks | Source and destination must have zero rows in these tables for this first fixture. No replay of signed transactions or old action intent. Non-confirmed/local transaction rows also cause refusal |
| Contacts, arbitrary account labels/notes/colors, custom UI preferences | Keep freshly created destination metadata; outside this fixture's recovery claim. Excluding free-form labels also avoids carrying a phrase pasted into a label |
| WorkManager DB, logs, crash dumps, screenshots, APKs, .env, arbitrary files | Regenerate or omit; never part of the package |

The destination's sync_progress_migrated_to_room_v7 guard must already be true and stays destination-owned. Other preferences, including unrelated sensitive values, remain in the destination XML and are never exported from the source.

One source-backed default is normalized: WalletPreferences.getSyncStrategy() returns ALL_WALLETS when sync_strategy is absent, so the public export explicitly records ALL_WALLETS in that case. Unknown or non-ALL_WALLETS stored values still refuse this profile. The synthetic Android fixture deliberately leaves this preference unset and verifies the effective value. Native schema/user_version checks follow external/ckb-light-client/light-client-lib/src/storage/db/sqlite.rs at the pinned Pocket commit.

## Snapshot and restore boundary

The emulator-only host command checks the named AVD, qemu property, release version/code, debuggable package and installed APK digest before mutation. It force-stops and disables the package, verifies no Pocket process exists, and leaves it disabled. Disabling prevents normal app/background startup while the standalone helper operates. The helper runs through app_process under run-as; it never initializes Pocket's Application, foreground service or LC.

Read Room and native WAL state with SQLite while no writer exists. Export only selected Room records. Construct the native file from a single SELECT snapshot into a new database, then close it. Do not copy the main native file alone or mutate historical evidence. Native/Room/preferences are not one database transaction: cross-store identity/progress checks are mandatory, and any existing semantic inconsistency causes refusal.

Destination staging creates an internal copy of the DESTINATION Room DB and sidecars inside the destination sandbox, applies allowed rows/preferences, clears TESTNET caches for rebuilding, and checks key-record bytes are unchanged. These internal files contain destination encrypted keys and MUST NEVER be exported or added to a package. They are not a workaround for source secret filtering.

Activation has a durable journal before any rename, retained originals, file/directory fsync, and explicit rollback. Pocket remains disabled on error/interruption. A separate enable command refuses while a journal exists; it does not launch Pocket. Backup originals remain private to the destination sandbox. Later cleanup is outside WO-2.

Staging records hashes/absence of every destination activation file. Commit refuses a changed baseline before journaling; rollback verifies those same hashes before removing the journal. Selected sync preferences absent from the source projection are removed from the destination so their default behavior is restored; all unrelated destination preferences remain untouched.

## Trust and limits

The operator retains the manifest SHA-256 separately in a trusted record. An attacker-editable manifest cannot authenticate itself. Package hashes establish integrity against that separately retained digest. Expected genesis and APK hash are supplied independently. H's hash and earliest coverage are operator/fixture declarations; per-Script cursor checks constrain them but do not prove pre-H completeness or a canonical H header by themselves.

The destination trusts the source's historical work and copied chain state. This is not independent historical reconstruction, an untrusted bootstrap proof, an encrypted backup protocol, or cross-version portability. No cloud or encryption is implemented. Package files are privacy-sensitive public-chain/account associations stored under the user's private runs directory.

Synthetic packages carry kind=synthetic and are refused by device restore. Passing these checks is not wallet recovery acceptance; WO-3 must still enforce the complete WO-1 cells/history/DAO/post-H/restart contract.
