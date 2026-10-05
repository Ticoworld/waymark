# WO-2 security check

Result scope: sanitized package and synthetic tooling tests. This is not an audit of Pocket, a production backup feature, or wallet-recovery acceptance.

## Secret boundary

The source Room database never leaves its sandbox. The standalone helper selects only the explicit wallet/public discovery/progress fields documented in P2_SANITIZED_STATE_PACKAGE_SPEC.md. It selects no encrypted key values, PIN values or arbitrary preference entries for export. Native export reads only the separate native `kv` store and writes a fresh logical snapshot. Network identity files, source logs, source key backups and other databases are never pulled.

The destination restore preserves its freshly generated key IDs and key rows. It stages a copy of the destination's own Room files inside that same private destination sandbox and internally compares key-record bytes before/after the allowed metadata edits. Those stage/original files contain destination secret ciphertext and are explicitly prohibited from package contents, host pulls and Git. This distinction is enforced by the transport's approved-member-only pull rule.

Normal recovery remains responsible for the phrase/private key, passphrase if applicable outside this first fixture, destination Keystore and PIN setup. The experiment's source/destination fixture uses no production funds and no existing evidence keys. WO-2 created no real wallet keys.

## Automated gate

scripts/h02_package.py rejects unknown files, nested members, symlinks, duplicate JSON keys, unknown JSON fields/columns/preferences, raw Room schemas, native non-KV objects, missing native datasets, bad sidecar handling, unexpected native metadata, wrong version/schema/genesis/APK, mismatched full Scripts and inconsistent progress.

The content scanner rejects known key_material/backup/PIN/Keystore/private-key labels, PNBK and JKS/JCEKS magic, PEM private keys, extended private keys, synthetic secret canaries and any sequence of twelve BIP39 dictionary words. The public 2048-word dictionary is copied from the pinned Pocket source; SHA-256 2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda. Raw source labels/notes are excluded entirely.

This is intentionally not perfect forensic detection. An unlabelled random 32-byte secret cannot generally be distinguished from a hash or public cell data. Structural source selection is the primary control. A public-chain cell containing a prohibited marker may cause conservative refusal; do not disable the gate to force a benchmark success.

The host suite covers valid generation/hash checks, independently trusted manifest digest, bit corruption, missing members, version/schema/APK mismatch, wrong network and actual native genesis, absent native transaction dataset, key_material records, encrypted key columns, PIN records, backup blobs, Keystore files, mnemonic sequences, private-key markers, native secret payloads, raw key tables, sidecars/extra files, missing or overstated progress, wrong address, duplicate JSON keys, synthetic-package restore refusal, fresh UUID mapping and physical-device rejection before adb.

The Android synthetic test constructs source Room 17 from the pinned schema with nonsigning key/PIN canaries and an unrelated sensitive preference. It retains committed WAL updates during fixture transfer, exports through the real Android helper, validates the sanitized package, stages/activates only within /data/local/tmp/h02-synthetic-*, and injects an interruption after the first activation rename. Rollback restores a coherent baseline; key/PIN canaries remain unchanged and never appear in the export. No actual wallet sandbox was restored by this test.

## Process and activation protections

Every device operation specifies an emulator serial and checks the exact AVD name plus qemu property. The production transport additionally checks Pocket v1.8.5/code 27, debuggability and installed APK SHA-256. Physical serials refuse before adb is called. There is no implicit/default-device command, no Pocket launch command and no UI automation.

The final transport also checks API 36 / x86_64. Its real debug-UID probe passed after replacing legacy exec-out and raw binary stdin with shell-v2 exit statuses, base64 transfers and remote-write hashes. Deliberate remote failure, overwrite attempt and incorrect installed-APK digest refused. A 65,792-byte all-byte fixture survived transfer unchanged. Pocket remained disabled, with wallet/native/security initialization paths absent. These were generated non-wallet files in an empty debug sandbox; no source keys or real Room database were accessed. The earlier helper ClassNotFound crash logs contain only this failed helper startup, not a Pocket recovery attempt.

The final probe additionally passed a generated scratch SQLite/WAL transaction and read-only reopen under the actual app UID after emulator restart (runs/wo2/empty-sandbox-probe-final2.log). Its database is confined to files/h02-probe-*, contains only integer 73 and is not a Pocket database. The final helper hash is recorded in P2_BUILD_REPORT.md. No security policy, Android backup rule, app Keystore protection or SELinux setting was relaxed.

Before extraction/staging, Pocket is force-stopped and disabled. Process checks surround helper work. NativeStop/service-stop is not treated as a DB barrier. Activation is journaled with retained originals and file/directory fsync. The app remains disabled on errors; enable refuses an outstanding activation journal. The synthetic-only interruption hook is refused for a real Pocket sandbox.

Package integrity relies on a separately retained trusted manifest digest; hashes inside the package alone are not authentication. The expected testnet genesis and APK digest are operator-held inputs. Historical completeness remains trusted-self state and must be checked against the WO-3 fixture oracle. Restored native chain state is not independently re-proven by the destination during staging.

New host export directories are created exclusively under runs and receive a restricted Windows ACL for the current user, SYSTEM and Administrators (0700 on non-Windows). There is no encryption or cloud upload. Existing run directories hold generated synthetic/build artifacts and retain their existing ACLs; they are not presented as encrypted or user-exclusive storage.

The ACL path was exercised on a new empty runs/wo2/acl-check-2b8d072c directory. Windows reported protected inheritance and exactly the current user, SYSTEM and Administrators with FullControl. Final host policy run: 33 tests passed (runs/wo2/package-tests-final4.log), including native schema/ABI/cursor-manifest/recent-header format and wrong-destination Script checks. Final Android run: export/WAL, the unset ALL_WALLETS default, valid empty recent-header list, stage/commit, changed-destination refusal, interrupted activation/verified rollback and unchanged secret canaries passed (runs/wo2/android-helper-tests-final4.log). The helper's fixed refusal output in that log is expected for the two deliberate negative operations. No wallet recovery was exercised.

## Boundaries still requiring WO-3 evidence

- Actual source/destination export and merge after normal key/account recovery have not run.
- Real history, live outpoints, DAO phase transitions, stale-snapshot spends, restart persistence and normal signing readiness remain unproven.
- The first fixture excludes pending actions, contacts, free-form source metadata, arbitrary account discovery and cross-version recovery.
- Synthetic refusal and rollback checks establish bounded tooling behavior; they do not establish recovery correctness or speed.

No D2, cloud, PR or grant work was performed. Existing D2/iBytes/Pocket historical evidence and PR #297 worktrees were not modified or used as writable fixtures.
