# P1 — Current Pocket recovery map

Date: 2026-10-05. WO-1, source archaeology and experiment design only.

**Verdict: YES — but test instrumentation required.** A same-version restore of selected non-secret state is technically testable with an unmodified Pocket v1.8.5 application in a disposable debuggable sandbox. It is not an existing supported release-app restore feature. Success, completeness and speed remain unmeasured. No backup implementation, build, installation, sync run or D2 integration was performed.

## Source and provenance

| Item | Verified value |
|---|---|
| Isolated source | C:/Users/timot/Desktop/2026/CKB/H02-P0/repos/pocket-node |
| Origin, fetch and push | https://github.com/RaheemJnr/pocket-node.git |
| Release tag | v1.8.5 |
| Commit | b28979de744798ffb75367b031d4871ec3af1a12 |
| Checkout | Detached at release commit; clean |
| Acquisition | Local clone with --local --no-hardlinks --no-checkout from the accepted clean D-BOOTSTRAP donor; independent copied objects, no alternates; only refs/tags/v1.8.5 fetched with --no-tags |
| Release record | [GitHub release](https://github.com/RaheemJnr/pocket-node/releases/tag/v1.8.5); API returned target_commitish matching the commit, published 2026-09-30T18:53:44Z, draft=false, prerelease=false, PocketNode-v1.8.5.apk asset. APK not downloaded. |
| Android identity | com.rjnr.pocketnode; versionName 1.8.5; versionCode 27 |
| Embedded LC | ckb-light-client-lib 0.5.4, vendored within Pocket, not a submodule |
| Exact vendored source identity | Pocket commit above plus Git tree 3ac3e0ce1f4e46897d188b76c5b841b9097fa506 at external/ckb-light-client |
| Official LC commit | Not determinable as one authoritative upstream pin from the inspected vendored metadata. Do not substitute D2's official-LC pin or PR #297's commit. |
| Room | 2.8.4; database schema 17; exported identityHash 091b40f9618fee3fc8032ff01255a9a4 |
| Build | compileSdk 36, targetSdk 36, minSdk 26; AGP 8.13.2, Kotlin/KSP 2.3.10, Gradle 8.14.3; Java bytecode 17; Rust 1.92.0 |
| ABI/build differences | Default arm64-v8a + armeabi-v7a; BUILD_X86_64=1 adds emulator x86_64 in Gradle and JNI script. GitHub release enables updater and background foreground service; playRelease disables both. Use the same debug build from this pin in both future arms, not a mixture of Play/release/debug. |
| Native build | build-android-jni.sh uses release Rust, features jni-bridge,portable, Android native API 21. No native artifacts are tracked in this source checkout. |

Build references: [app configuration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/build.gradle.kts#L10), [wrapper](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/gradle/wrapper/gradle-wrapper.properties), [Rust manifest](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/Cargo.toml), [JNI build](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/build-android-jni.sh), [Room schema](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/schemas/com.rjnr.pocketnode.data.database.AppDatabase/17.json).

All source citations below use this immutable Pocket commit. Paths starting with data/, ui/ or di/ are relative to android/app/src/main/java/com/rjnr/pocketnode/. Native paths are under external/ckb-light-client/light-client-lib/src/.

## 1. Key recovery

Mnemonic import enters MnemonicImportViewModel.importMnemonic in ui/screens/onboarding/MnemonicImportScreen.kt:133; raw-key import enters importPrivateKey:204. AddWalletViewModel supplies equivalent additional-wallet flows. WalletRepository.importFromMnemonic:191 validates the words, derives the default account, checks duplicate address, generates a NEW UUID, invokes the key-persistence callback, inserts WalletEntity, sets the active ID and RECENT for both networks, then records public discovery candidates. importRawKey:270 also creates a new UUID and RECENT defaults. Imports do not preserve source wallet IDs.

WalletKeyWriter.persistNewWallet:99 drives the authenticated V2 write through KeystoreV2MigrationHelper.writeNewV2Row. Android Keystore alias pocket_node_key_material_v2 encrypts a WalletKeyBundle containing private key and mnemonic under AES-GCM; per-operation device credential/strong biometric authentication is required. The key is not portable to another installation/device. The normal UI has an explicitly consented V1 fallback when no secure device lock exists; that remains Android-Keystore encrypted and is also excluded from H02. Keep the same credential setup in both experiment arms.

KeyManager now owns derivation/legacy-read/migration support rather than being the sole new-key writer. Legacy EncryptedSharedPreferences files ckb_wallet_keys.xml and ckb_wallet_keys_<walletId>.xml use a Keystore-backed MasterKey (StrongBox requested with fallback). These are not state-backup candidates.

KeyBackupManager writes files/key_backups/<walletId>.enc when a session PIN is available. The PNBK format stores version, salt, IV and AES-256-GCM ciphertext of KeyMaterial, including private key and optional mnemonic. Current writes use format 2, Argon2id (64 MiB, t=3, p=4); format 1 PBKDF2-HMAC-SHA256, 600,000 iterations is still readable. First-wallet persistence can occur before any session PIN exists, so existence of a backup is not guaranteed by a key-row write alone.

These PIN blobs are cryptographically self-contained given the PIN; they are NOT harmless device-bound cache data. Pocket deliberately excludes them from transfer because the PIN can be attacked offline. A stronger KDF does not change the H02 exclusion.

| State | Device-bound or portable | H02 treatment |
|---|---|---|
| User's independently retained mnemonic/private key and any applicable passphrase | Normal key-recovery input | Enter through supported UI only; never put in H02 package, scripts, logs, Git, screenshots or result manifests |
| Room key_material, including ciphertext/IV/kdfVersion | Bound to source Keystore alias; still sensitive | Exclude every column/row; preserve destination-created rows unchanged |
| PIN-encrypted PNBK files | Portable encrypted signing material if PIN is known/guessed | Exclude entire key_backups directory and .tmp files |
| Keystore aliases, auth/session material, legacy encrypted prefs | Device-bound or security state | Regenerate normally; never transplant |
| Public addresses, derivation paths, Script identities and non-secret account labels | Portable but privacy-sensitive | Allowlisted metadata only, matched against destination-derived identities |

References: [import](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/ui/screens/onboarding/MnemonicImportScreen.kt#L133), [wallet creation/import](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/WalletRepository.kt#L191), [writer](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/WalletKeyWriter.kt#L99), [Keystore](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/crypto/KeystoreEncryptionManager.kt#L144), [PIN backup](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/crypto/KeyBackupManager.kt#L59), [key row](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/database/entity/KeyMaterialEntity.kt#L7), [legacy prefs](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/KeyManager.kt#L154).

## 2. Light-client state

Let APP be Context's credential-encrypted application data root, normally /data/user/0/com.rjnr.pocketnode (also exposed through /data/data/com.rjnr.pocketnode for user 0). Other Android users have different roots: resolve on the future disposable instance rather than hard-coding user 0.

| Location beneath APP | Purpose |
|---|---|
| files/data/mainnet/store.db | Mainnet native SQLite store |
| files/data/testnet/store.db | Testnet native SQLite store |
| Same basenames with -wal and -shm | SQLite companions; live WAL can contain committed state absent from main file |
| files/data/<network>/network/ | Peer/network persistence and identity; exclude the entire directory |
| files/mainnet.toml; files/testnet.toml | Regenerated from packaged assets with current sandbox paths |

NodeLifecycle.initializeNode:128 copies the packaged TOML and substitutes these absolute paths, then calls nativeInit/nativeStart. Its old flat-data migration is not a backup interface. Network selection causes process restart; do not switch networks after restoring state, because switchNetwork also clears app caches.

The non-WASM native backend is rusqlite 0.29 with bundled SQLite. Storage::new opens a single SQLite table kv(key BLOB PRIMARY KEY, value BLOB), with journal_mode=WAL and synchronous=NORMAL. There is no H02 importer or schema-version compatibility gate in this table. Same crate version alone is not sufficient compatibility evidence; pin the full source/build/schema.

Native row families:

| Key family | Meaning and restore consequence |
|---|---|
| Prefix 0, TxHash | Stored transaction body with block number/index; closure needed for inputs, outputs, history and DAO |
| 32/64, CellLockScript/CellTypeScript | Script-derived cell index |
| 96/128, TxLockScript/TxTypeScript | Script transaction/input-output index |
| 160/192, BlockHash/BlockNumber | Headers/extensions and height/hash mapping |
| 208, CheckPointIndex | Block-filter hash checkpoints |
| 224 + FILTER_SCRIPTS + packed Script + role byte | Registration identity and per-Script cursor; lock=0, type=1; value is big-endian u64 block number |
| Other 224 metadata | GENESIS_BLOCK, LAST_STATE (chain state/work/header), LAST_N_HEADERS, MAX_CHECK_POINT_INDEX, MIN_FILTERED_NUMBER, MATCHED_BLOCKS work records |

Do not transplant only cursor rows or fabricate a high cursor: that can skip reconstruction without restoring its results. A whole consistent same-version native store retains indexed transactions, headers, checkpoints and derived state together. It also retains the source's prior chain state; it is a trusted-self snapshot, not independent re-verification of every pre-H result.

Storage.update_filter_scripts:225 replaces registrations on ALL, upserts on PARTIAL, then recomputes the minimum filter cursor and clears matched-block work. A restored store is therefore subject to Pocket's normal startup registration policy. The app's PARTIAL rewind clamp does NOT protect ALL registrations.

bridge_core::lifecycle::init constructs fresh pending-transaction/peer runtime state, checks stored genesis against the configured chain, cleans invalid matched-block records and starts network/protocol services. A genesis mismatch currently panics in Storage::init_genesis_block:710; this is a backstop, not a safe user-facing wrong-network import gate. Instrumentation must reject before placement/start.

Native stop is NOT a database-close/export barrier. bridge_core::lifecycle::stop has bounded peer shutdown but retains OnceLock-held runtime/storage globals. A complete process exit is needed for an unambiguous offline replacement boundary. Preserve persisted native work records as part of the coherent store and let same-version initialization reconcile them; do not hand-edit their cursors or transplant process memory, handles or sessions.

References: [paths and lifecycle](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/NodeLifecycle.kt#L128), [SQLite and registrations](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/storage/db/sqlite.rs#L76), [key encoding](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/storage/mod.rs#L291), [native initialization](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/bridge_core/lifecycle.rs#L98), [stop semantics](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/bridge_core/lifecycle.rs#L444).

## 3. Application state

Pocket's primary Room DB is APP/databases/pocket_node.db, schema 17, WAL mode, plus pocket_node.db-wal / -shm. AppModule.provideAppDatabase:139 supplies the singleton. Android WorkManager can maintain its own scheduling DB; that is framework runtime state, not wallet recovery content.

The primary DB mixes public wallet state with encrypted secrets. **Do not copy a raw Room DB off-device and then DELETE key_material.** Secret ciphertext can survive in free pages, WAL, journals or temporary copies. A non-secret export must be freshly constructed from explicit columns/rows while still within the source sandbox, and contain none of those raw pages.

| Room table | Required understanding / first candidate policy |
|---|---|
| wallets | walletId, parentWalletId, type, derivationPath, accountIndex, both addresses, name, active flag, timestamps and color. Preserve public logical mapping, but keep fresh destination UUIDs and key records; remap source references to destination IDs by full Script + path + parent identity. |
| key_material | NEVER export/import. Destination keys are generated by normal recovery. A source wallet row with no matching destination key is not a recovered spendable account. |
| sync_progress | (walletId, network), lightStartBlockNumber, localSavedBlockNumber, updatedAt. Required to retain continuation policy, especially ALL_WALLETS. Restore only consistent source values under remapped IDs; never infer completeness from these values alone. |
| sub_account_candidates | (parentWalletId, derivationPath), accountIndex, scriptArgs, state, createdAt, registeredFromBlock. Preserve genuine discovery state/coverage and remap parent ID. It has no network column: restrict first package to one known network and do not infer cross-network discovery completeness. |
| transactions | Ledger/cache, keyed by txHash, includes wallet/network association, direction, amount, fee, confirmations, pending/local flags, and v16 fee_shannons. First candidate may carry only confirmed fixture-network records as stale hints; recompute/check against native history. Do not import pending/local payment intent. |
| balance_cache | Per wallet/network cached capacity/as-of block. Non-authoritative; omit in first candidate and rebuild. |
| header_cache | Partial headers (hash, number, epoch, timestamp, dao, network); NOT a complete serialized header proof. Omit in first candidate; resolve against restored native headers/peer proofs. |
| dao_cells | Cached position/outpoint, deposit/withdraw headers and epochs, status, compensation, wallet/network. Stale hints only. First candidate omits these and reconstructs from complete native fixture coverage, preventing stale cache-only positions from passing as live. |
| pending_dao_withdraws | Persisted deposit outpoint -> withdraw tx intent/status overlay. General recovery must reconcile, never blindly trust. First fixture requires none unresolved at H; therefore none exported. |
| pending_dao_unlocks | v17 withdrawing outpoint -> unlock tx marker. Same exclusion for first quiescent fixture; otherwise export policy/reconciliation must be separately specified before widening scope. |
| pending_broadcasts | signedTxJson, reservedInputs and retry/watchdog state. Excluded. Copying this can replay a user's old payment intent; no unresolved/failed retry entries allowed in first source fixture. |
| contacts | Names, addresses, optional notes/tags and usage metadata; not chain-reconstructible and privacy-sensitive. Optional product-level metadata; omitted from first fixture and its acceptance claim. |

A correct general lost-device product also needs a policy for contacts, labels, failed transactions and pending actions. The first experiment deliberately tests a settled wallet with no unresolved broadcasts; it does not pretend that omitting these is a full general export feature.

APP/shared_prefs/ckb_wallet_prefs.xml holds non-key preferences, but use field selection, not directory copying:
- selected_network; sync_strategy (ACTIVE_ONLY / ALL_WALLETS / BALANCED); active_wallet_id.
- <walletId>_<network-lowercase>_sync_mode and _custom_block_height.
- matching _initial_sync_completed and _zero_cell_rescan_done flags.
- discovery gap-limit flags, sweep fee labels and bulk-transaction labels where present; document inclusion or exclusion.
- migration guard sync_progress_migrated_to_room_v7: preserve the fresh installation's established guard so legacy preference migration cannot overwrite restored Room progress. Do not transplant key-migration or onboarding security state.
- theme, coachmarks, last-seen release, last-sync timestamp, background-sync and network-service switches are UI/runtime preferences. Keep the destination setup for these in the first experiment, with identical network/service choices in both arms.

The label "initial_sync_completed" is misleading as an acceptance metric: registerAccount writes true immediately after successful Script registration (GatewayRepository:587). It does not prove history is scanned. lightStartBlockNumber is also updated on registrations and is not a durable original birthday. Preserve an explicit coverage start per Script in the experiment manifest.

WalletPreferences persists CUSTOM as a block height, not a date. The UI label is "From a specific date", but SyncOptionsSheet presents a Block Height input; do not invent a stored date column.

References: [Room declaration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/database/AppDatabase.kt#L29), [Room initialization](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/di/AppModule.kt#L139), [all entity definitions](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/database/entity), [preference keys](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/WalletPreferences.kt#L233), [registration flag](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L580), [height input](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/ui/components/SyncOptionsSheet.kt#L185).

## 4. Regenerated and excluded state

Regenerate peer identity/network files, live connections, peer bans/address cache as applicable, runtime OnceLocks, JNI/Coroutine handles, in-memory Script-to-wallet map, sync tracker samples/ETA, cell reservations, temporary UI/navigation state, notifications, WorkManager jobs and service state. Do not copy the network directory even if part of it is ordinary peer data; this avoids accidentally copying identity key material.

Exclude cache/, code_cache/, files/updates/, logs/diagnostic journals, APKs, temporary exports, crash reports, screenshots and arbitrary shared_prefs. Authentication settings, ckb_pin_prefs.xml, key_migration.xml, all legacy key prefs, any security migration bookkeeping, Keystore state and files/key_backups are excluded regardless of encryption.

The first native payload is only store.db as a consolidated coherent SQLite snapshot for one network; never the whole files/ tree. No production phone or old D2 database is a source for the first fixture.

## 5. Exact current import flow

The requested conceptual order needs correction. Current code is effectively:

~~~
fresh installation / application dependency initialization
  -> GatewayRepository startup migration / Room initialization
  -> NodeLifecycle initializes and starts native LC (before import can finish)
normal mnemonic or raw-key UI
  -> WalletRepository derives account, allocates NEW UUID
  -> WalletKeyWriter creates DESTINATION Keystore-bound key row
  -> wallets row + active ID + RECENT defaults + mnemonic candidates
  -> GatewayRepository.onActiveWalletChanged
       -> decode address to lock Script
       -> register according to ACTIVE_ONLY / ALL_WALLETS / BALANCED
  -> THEN show post-import SyncOptionsSheet on either network
  -> Apply -> resyncAccount(selected mode, custom height)
       -> re-register; persist chosen policy with race guards
  -> finish onboarding / normal account use and polling
  -> local cells, activity and DAO reads -> Room cache reconciliation
~~~

MnemonicImportViewModel calls onActiveWalletChanged at line 181, before setting showSyncModeDialog at 186. Thus source comments saying the picker always precedes first registration are not the actual call order. AddWalletViewModel similarly stages its post-import choice. RECENT is applied explicitly when selected, not skipped; errors leave the sheet open. Dismissal keeps the import default.

ACTIVE_ONLY registration resumes at max(Room saved height, existing native Script height), unless explicitly force-resyncing. ALL_WALLETS/BALANCED uses each wallet's saved Room height, otherwise the selected mode. Missing Room state can therefore cause avoidable rescan even with native state present.

resyncAccount rewinds deliberately. It is not the correct operation to call after package injection merely to make the UI look configured. Restore the selected policy and consistent progress while stopped, then let ordinary startup run and observe every registration.

SyncPoller.getAccountStatus persists advancing native Script heights for registered wallet mappings and reconciles candidates. Balances/history/DAO are rebuilt through GatewayRepository refresh/read methods, CacheManager, DaoDepositReader and DaoSyncManager. Polling success alone is not evidence that all three views are complete.

References: [ordering and picker](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/ui/screens/onboarding/MnemonicImportScreen.kt#L179), [node startup](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L171), [active-wallet registration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L246), [single registration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L461), [resync](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L592), [multi registration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/SyncCoordinator.kt#L564), [progress/candidate reconciliation](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L1263).

## 6. Multiple wallets, accounts and Scripts

One WalletEntity corresponds to one owned lock Script, recovered from its stored address without decrypting keys. A mnemonic parent plus one sub-account is two WalletEntity rows, two key rows and two owned Scripts, with a parentWalletId relationship. Root path is m/44'/309'/0'/0/0; sub-account N is m/44'/309'/N'/0/0. A raw-key import has one owned Script and no mnemonic discovery.

Mnemonic import additionally derives 10 account-axis candidates (1..10) and 41 chain-axis candidates (account 0, receive/change 0..20 excluding root). These are public Script args with paths, not recovered key rows. Registration initially selects at most five pending account-axis candidates plus all pending/found chain-axis candidates. Thus a single imported parent can initially register 47 statuses including its own Script. This is not a permanent cap: more accounts, later batches and extended chain windows change the set.

ALL_WALLETS caps simultaneous owned wallets at three, now explicitly keeping the active wallet. BALANCED first excludes wallets >100,000 blocks behind the maximum (retaining active), then caps. Candidate statuses are additional. Preserve the chosen strategy and log actual Script sets; never equate wallet count with total registration count.

SubAccountReconciler marks FOUND when activity is observed; EMPTY needs a known tip, scan within 1,000 blocks of tip, registeredFromBlock >0 and at least 50,000 covered blocks. These are discovery heuristics, not proof of universal account absence. The 0 "never registered" sentinel also means a from-genesis candidate cannot satisfy that particular EMPTY condition as written. Do not silently rewrite it or mark candidates EMPTY for the benchmark.

WalletManagerViewModel.restoreFoundSubAccounts prompts to read the parent and persist each discovered sub-account; WalletRepository.createSubAccount(explicitIndex) inherits parent sync policy/progress and retires that candidate. Known contiguous account 1 can also be created through the normal Add sub-account flow. No arbitrary unknown-account discovery completeness is established.

A key performance risk survives whole-store copy: pending/found chain candidates are registered from candidateScanStart (historical policy/earliest cached tx/recent floor), not necessarily their saved native cursors. ALL resets their cursors. Preserve actual candidate states and measure any historical rescan; do not remove inconvenient candidates or advance their cursors to manufacture a win.

For the first fixture use one mnemonic family, empty passphrase, accounts 0 and 1, two populated lock Scripts, ALL_WALLETS, one network. Both arms use supported account creation/recovery; compare exact identity mappings. Current sub-account creation derives from stored words without a supplied passphrase; this experiment does not qualify passphrase-backed account families.

Native LC DB alone cannot supply UUID relationships, signing-key rows, candidate lifecycle, network-specific policy or labels. It is insufficient for complete account recovery.

References: [candidate derivation](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/SubAccountDiscovery.kt#L50), [candidate policy](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/SyncCoordinator.kt#L146), [discovery gate](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/SubAccountReconciler.kt#L56), [sub-account restoration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/ui/screens/wallet/WalletManagerViewModel.kt#L92), [account creation](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/WalletRepository.kt#L333).

## 7. DAO

DAO positions are native lock-Script-derived cells/transactions, filtered by DAO type code hash in the app. Normal registration remains lock-only; DAO does not imply a separately registered type Script.

DaoDepositReader.list:72 pages all matching cells and transactions, builds a spent-outpoint set, removes spent cells, resolves deposit/withdraw transactions and headers, and computes compensation/epoch/unlock state. Both loops have a runaway cap and can log incomplete results; hitting a cap or skipping an unresolved fixture cell is failure, not success.

DaoHeaderResolver.getOrFetchHeader uses Room partial-header cache, then local native header, then peer fetch. Room header cache cannot independently authenticate its own contents: its conversion supplies blank non-cached header fields. In the first candidate omit this cache and reconstruct from native data/normal proof fetches.

DaoSyncManager persists header_cache and dao_cells. GatewayRepository.getDaoDeposits writes live rows, merges cached rows, and applies persisted phase-1 withdraw/phase-2 unlock overlays. v17 pending_dao_unlocks prevents duplicate unlock actions and retires cached spent positions after resolution. Marker age, transaction cache status and chain lookup affect reconciliation.

An absent cached cell can be retained as OUTSIDE_WINDOW. The code's windowStart is the current native Script head, not original coverage start. A stale backup cannot treat absent=unspent, absent=spent, a cached UNLOCKABLE label or a previous CONFIRMED marker as present truth. A DAO spend after H may have no marker in the backup at all. This is why candidate B rebuilds dao_cells instead of importing stale position rows, and why its whole native history must cover the original deposit and later spend.

Required reconciliation: exact DAO outpoint, live/spent status, phase, deposit and withdraw tx/block identities, epochs, compensation, maturity and confirmed post-H transitions. Refresh current tip/headers. Empty/partial results during warm-up cannot retire a position or satisfy acceptance. For broader pending-action recovery, define marker replay/reconciliation before widening the fixture.

References: [DAO enumeration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/DaoDepositReader.kt#L72), [headers](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/DaoHeaderResolver.kt#L124), [merge and overlays](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L2594), [cached-cell fate](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/DaoCellRetirement.kt#L139), [v17 marker](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/database/entity/PendingDaoUnlockEntity.kt#L19).

## 8. Same-version backup feasibility

**YES — but test instrumentation required. Production-source changes are not currently required for the first A/B test.**

The experiment can use the same unmodified v1.8.5 source compiled as debug on two disposable emulators. An external, narrowly scoped test helper running with the debug app's authorized sandbox access can select non-secret rows, consolidate native SQLite, validate a manifest, remap IDs and stage state while the app is stopped. This helper is instrumentation, not a shipped Pocket feature. Its implementation is not part of WO-1.

Do not assume stock Android has sqlite3 or release run-as access. The first helper must establish an app-UID SQLite path (for example a test-only executable staged via run-as) that does not initialize Pocket's Application/GatewayRepository during extraction/injection. Instrumentation that starts the target application could start the LC and invalidate quiescence. Access and observation capability need a bounded readiness check before the timed run.

Destination recovery first creates keys/account rows normally. Match each destination account to the package by network, full packed Script/role, public address, parent relation and derivation path. Translate source UUID references into those existing destination IDs. Do not rename keys, copy source encrypted key rows or replace destination key_material. The fresh signing key must still operate after restoring metadata.

No current production state importer was found. Existing KeyBackupManager handles secret recovery, TransactionExporter exports CSV, and schema JSON is a developer schema export. None is the requested non-secret lost-device state package.

A stock non-debuggable release on an ordinary locked phone has no demonstrated operator-accessible state import path. Shipping this to users would need a wallet-owned export/import surface or comparable approved platform integration. That limitation does not require editing production source to run the laboratory A/B.

## 9. Consistency boundary

Use a settled source with no pending broadcasts/DAO actions. Observe per-Script native progress and Room state through H and record H's hash plus declared coverage. No new user operations during capture.

1. Disable background work through the experiment's fixed setup and finish ordinary UI activity. Stopping a screen or foreground service alone is insufficient: SyncForegroundService is START_STICKY, its destruction cancels its observers, and repository/native work can continue. WorkManager also has catch-up jobs.
2. On the FUTURE DISPOSABLE EMULATOR ONLY, force-stop the package and verify every package process/service has exited before reading files. Keep it stopped throughout native and app-state extraction. No physical-phone force-stop was performed in WO-1.
3. Force-stop supplies a crash-consistent frozen filesystem, not a graceful SQLite checkpoint or a transaction across Room/native/preferences. Keep each DB's main/WAL pair together; record SHM as an ephemeral companion if present. Never assume WAL is empty because the app is gone.
4. Use SQLite-aware tooling within the stopped sandbox. For native state, prefer a SQLite backup into a new clean destination snapshot, then close/check the new file. For Room, SELECT only approved logical records/columns into a freshly constructed export; never export the raw source Room pages/WAL/SHM. These operations must not start the app.
5. If file-copy staging of native data is necessary, capture main + WAL from the same stopped interval (SHM can be retained in private staging, but SQLite can rebuild it). Consolidate and validate on a separate working copy. Do not delete or checkpoint original evidence stores.
6. Check that Room progress does not claim blocks beyond the matching native Script state, that identity/coverage associations are consistent, and that H's fixture state is complete. A checkpoint cannot repair cross-store semantic disagreement. Retry a capture or classify an inconsistency; do not edit cursors upward.
7. On destination, finish normal key/account recovery, force-stop, validate the package before replacing anything, then stage native store plus merged non-secret Room data/preferences. Keep destination-created keys and security prefs in place. Guard against stale destination WAL replay. Commit staged components as a complete set with a test-harness recovery marker; never launch a half-applied set.
8. A completed checkpoint with no writers can make copying only the main DB safe, but an attempted/busy checkpoint or service stop does not. Record successful result/closure rather than assuming it.

SQLite backup alone snapshots one DB; it does not atomically align two databases and SharedPreferences. SharedPreferences.apply is asynchronous, so verify persisted values after stop, rather than assuming the last UI action reached disk.

Android Auto Backup/D2D is inappropriate as this test's selective export mechanism: it is disabled/restricted, lacks the required logical key exclusion/remapping contract, and is not a measured consistent wallet-state snapshot. A production-friendly selective app export would be needed later if this experiment justifies it.

External behavior checked 2026-10-05:
- [SQLite WAL](https://sqlite.org/wal.html), section 4: WAL is part of persistent state; separating it from the DB can lose committed transactions or corrupt the database. Unclean process exit may leave WAL.
- [SQLite backup API](https://sqlite.org/backup.html): a completed backup creates a consistent database snapshot; not a selective secret filter or a multi-DB transaction.
- [Android adb / activity manager](https://developer.android.com/tools/adb): force-stop terminates the specified package.
- [Android Auto Backup](https://developer.android.com/identity/data/autobackup): allowBackup=false and Android 12+ D2D behavior differ on some manufacturers; explicit extraction rules matter.

Source references: [foreground service](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/sync/SyncForegroundService.kt#L32), [background scheduler](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/sync/SyncWorkScheduler.kt), [native stop](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/bridge_core/lifecycle.rs#L444), [WAL configuration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/di/AppModule.kt#L139).

## 10. Security boundary and limits of trust

AndroidManifest.xml sets allowBackup=false. data_extraction_rules.xml explicitly excludes key_backups/, ckb_pin_prefs.xml and key_migration.xml from cloud backup and device transfer. It is not an explicit blanket exclusion of every app file for every Android/OEM transfer path. Do not broaden the claim or weaken these protections. H02 must be stricter about secret exclusion than copying the remaining app directory.

Approved first-package content:
- One coherent same-version native SQLite snapshot for the declared test network.
- Public logical account/parent/path/Script map.
- Consistent remapped sync_progress and genuine candidate state.
- Selected non-security sync preference values and confirmed history hints.
- A manifest pinning app commit/build hash, LC tree hash, Room schema/identity, network/genesis, full Script identities/coverage, H/hash, file sizes/digests, capture method and package version.

Excluded:
- Raw Room files, WAL, SHM or generic SQL dumps; key_material even encrypted.
- Phrase, private keys, passphrases, PIN/hash/salt, PNBK blobs, Keystore/legacy key prefs, auth or migration security state.
- Peer/network identity, pending signed broadcasts/reservations, logs or UI captures containing recovery secrets.
- Arbitrary remote URLs, executable content, symlinks or path-traversing members from an archive.

A separately retained trusted digest/provenance record is needed for the laboratory package. A digest stored only inside an attacker-editable archive is not authentication. Controlled host storage must restrict access because Script/account associations reveal financial privacy. Cloud infrastructure/encryption-product design is outside WO-1.

The destination can check integrity, origin under this trusted-self experiment, supported version/schema, network/genesis, structural validity, identity mapping, internal cursor consistency, known fixture outputs and subsequent locally verified chain activity. It still trusts the source to have honestly and completely scanned declared pre-H coverage. Neither package authentication nor a SQLite integrity check proves historical non-omission. Full native copy also imports the source's old chain state; no claim of independent destination reconstruction of pre-H authority is made.

No speed result exists for current v1.8.5 recovery. Do not import the historical 0.24-second ADB-copy number as an H02 result. See the separate two-arm contract and delta report.
