# P1 — Delta from the D2 Pocket pin

Date: 2026-10-05. Static source comparison only; no old proof was rerun.

Historical commit: 6eda0b7a4601050b011591d41cc702f0dc7a7c38.
Current release: v1.8.5, b28979de744798ffb75367b031d4871ec3af1a12.

Both commits were compared in the NEW H02-P0/repos/pocket-node checkout. Existing historical donors and evidence remained read-only.

The consequential deltas are the import/sync coordination changes and Room 15 -> 17, particularly durable DAO unlock reconciliation. The raw native SQLite layout remains effectively the same, but the embedded bridge and application behavior have changed. The old proof is useful provenance, not evidence that current whole-wallet recovery already works.

## Classification by requested area

| Area | Classification | Historical -> v1.8.5 finding | Consequence for H02 |
|---|---|---|---|
| Native DB path/backend/key layout | UNCHANGED | Per-network files/data/<network>/store.db, SQLite kv BLOB table, WAL/NORMAL, packed Script/role cursor keys. sqlite.rs diff is only four added lines creating the parent directory before opening. | Reuse storage knowledge, not captured databases. Same layout does not permit mixing app versions or prove package completeness. |
| Native directory creation | CHANGED BUT NOT H02-RELEVANT | Storage::new now ensures parent directory exists. No row-format migration shown by this diff. | No separate backup architecture justified by this change. |
| Embedded LC declared version | UNCHANGED | ckb-light-client-lib remains 0.5.4. | Version number is too coarse; exact Pocket commit and vendored tree are required. |
| Embedded LC bridge/lifecycle | H02-RELEVANT | JNI logic extracted into bridge_core, UniFFI/iOS bridge added, native stop fixed to avoid deadlock. Globals still survive stop; restart required. Last subtree commits include c297a4e6 (stop) and 66a72a72 (bridge extraction). | Reconfirm runtime entry points and quiescence. Never treat nativeStop as a closed SQLite snapshot barrier. |
| Official upstream LC commit of vendored tree | UNKNOWN | No authoritative one-commit upstream pin established. | Record current Pocket commit plus tree 3ac3e0ce1f4e46897d188b76c5b841b9097fa506 instead of inventing an official LC SHA. |
| Room DB/schema | H02-RELEVANT | Historical AppDatabase version 15; current 17. Migration 15_16 adds transactions.fee_shannons; 16_17 adds pending_dao_unlocks and its wallet/network index. | First package is v1.8.5/schema-17 only. Old Room captures are not current fixtures and must never be injected. |
| Key-backup format/security boundary | UNCHANGED | Historical backup already writes PNBK format 2 with Argon2id, 64 MiB/t3/p4 and reads legacy PBKDF2 format 1. Keystore V2 key_material shape also unchanged. | Do not claim v1.8.5 newly invented PIN backup or that the blob became safe to export. Secrets stay excluded. |
| Key-backup implementation | CHANGED BUT NOT H02-RELEVANT | KeyBackupManager moved data/wallet -> data/crypto, uses shared Argon2id instead of direct BouncyCastle calls; logging abstraction changed. Pinning/tests matter, but no new non-secret state-export outcome. | Read current paths; no H02 key migration. Existing KeyBackupCompatibilityTest documents intended compatibility; not run here. |
| Wallet/account schema | UNCHANGED | WalletEntity and KeyMaterialEntity have no diff. UUID IDs, parentWalletId, accountIndex, addresses and path already exist. Native DB alone was not sufficient then either. | Preserve/remap public identity without source ciphertext. Multi-account support is not new H02 work. |
| Import defaults | H02-RELEVANT | Old import did not persist explicit wallet sync defaults; new markImportedWalletSyncMode sets RECENT on both networks for mnemonic/raw-key imports. NEW_WALLET remains the generated-wallet default. | Correct control uses current supported recovery; do not benchmark the old faulty tip default. |
| Post-import sync flow | H02-RELEVANT | Picker offered for imports on both networks; RECENT choice actually applies; failure stays visible; settings applied with wallet-specific guards. | Trace actual call order: initial active-wallet registration precedes picker. Injection follows completed normal key recovery at a process-stop boundary. |
| Script registration/sync concurrency | H02-RELEVANT | Registration mutex, active-wallet staleness checks, per-wallet resync overrides, multi-wallet set preservation and active-wallet priority under the three-wallet cap. | Current tests must cover both owned Scripts, actual setScripts calls and restart. Old one-Script evidence cannot establish this. |
| Rewind clamp/discovery windows | UNCHANGED (core policy) | PARTIAL rewind clamp and 10 account-axis + 41 chain-axis discovery scheme already present at old pin. SubAccountReconciler diff is logger injection, not a new coverage proof. Candidate historical-start and ALL reset hazards remain. | Preserve genuine candidate state; measure repeat scans. Do not attribute all #332/#382 functionality to the later release. |
| Sync preference shape | H02-RELEVANT (callers/semantics), largely unchanged storage | Preferences split into shared interfaces; public keys still in ckb_wallet_prefs. getSyncModeOrNull already existed; new race-safe registration callers preserve/apply explicit choices. New service/UI preferences also exist. | Transfer only allowlisted sync values with mapped UUIDs; no wholesale SharedPreferences copy. |
| DAO persistence/reconciliation | H02-RELEVANT | v17 durable phase-2 unlock marker and cache retirement logic (#529), spend/outpoint normalization and reconciliation refinements. Historical phase-1 markers already existed. | A stale backup must not resurrect unlocked positions. DAO cache is not authority. First settled fixture rebuilds DAO cache and tests post-H transition. |
| Recovery UUID identity reuse | UNCHANGED | Both imports allocate a fresh random UUID. No address-identity reuse or full-state restore importer added. | A host-side metadata translation is still necessary for laboratory state injection. |
| App backup policy | UNCHANGED | No diff in AndroidManifest.xml/data_extraction_rules.xml: allowBackup=false and targeted secret exclusions for cloud and D2D remain. | Do not turn a lab test into copying protected secret blobs. The XML is targeted, not a blanket all-files D2D exclusion. |
| Contact entity/transaction CSV export | UNCHANGED | No diff in ContactEntity or TransactionExporter. CSV export is not a complete state restore interface. Contacts remain app-only personal metadata. | Do not claim normal export solves native state continuity. First fixture does not claim contact restoration. |

"UNCHANGED" here is a source comparison in the named area, not a guarantee of binary compatibility. "H02-RELEVANT" means the experiment must account for it, not that a new product is warranted.

## Evidence used

Current immutable references:

- [Room version/migrations](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/database/Migrations.kt#L550) and [schema](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/database/AppDatabase.kt#L78).
- [Wallet import and UUID creation](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/WalletRepository.kt#L191).
- [Current import UI](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/ui/screens/onboarding/MnemonicImportScreen.kt#L179).
- [Registration serialization](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/SyncCoordinator.kt#L287).
- [Resync across wallets](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L592).
- [PIN backup format](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/crypto/KeyBackupManager.kt#L59).
- [Native SQLite](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/storage/db/sqlite.rs#L76).
- [Stop semantics](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/bridge_core/lifecycle.rs#L444).
- [Backup exclusions](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/res/xml/data_extraction_rules.xml).

Historical read-only references, under C:/Users/timot/Desktop/2026/CKB/ckb-script-port:

- docs/G3_1_POCKET_REFERENCE_INTEGRATION.md — initial source/build archaeology. Its initial blocked attempts are superseded for execution claims by G3-1R1.
- docs/G3_1R1_POCKET_EXECUTION_EVIDENCE.md — actual device flow, host-side D2 staging, continuation/restart and raw-copy measurement.
- docs/G3_FINAL_REFERENCE_PRODUCT_CHECKPOINT.md — accepted one-exact-Script scope, candidate/account responsibilities and limitations.
- _work/g3-1-pocket-node/_g3-1r1-evidence — presence checked by directory listing; no database connection, WAL replay, checkpoint or application execution.

The historical 0.24 s copy of native+Room files did not exclude all encrypted secret pages and was not a lost-device benchmark. It is evidence that a file-copy control deserves examination, not a security-approved package template. The historical source Room capture remains private evidence.

## What carries forward

Reuse the path map, separation of native/Room state, exact Script identity model, restart acceptance concept, and evidence discipline. Do not reuse source UUIDs, raw Room DBs, old encrypted keys, old APKs, completed D2 proof scripts or speed claims.

The next experiment asks only whether current same-version wallet-owned non-secret state restore beats correct current normal recovery while meeting every acceptance check. It does not reopen G3 or add D2.
