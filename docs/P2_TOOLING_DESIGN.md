# WO-2 test-only tooling design

The harness preserves the source/key separation identified in WO-1. Pocket production source stays pinned and unchanged. No D2 artifact or integration exists.

```
frozen + disabled SOURCE Pocket sandbox (future WO-3)
  standalone Java helper, under run-as; Pocket Application never loaded
    Room explicit public SELECTs -> app.json
    native kv logical snapshot   -> native.sqlite
  host strict schema/secret checks + manifest + SHA-256
    private local package + independently retained trusted digest

fresh DESTINATION: normal key/account recovery first (future WO-3)
  host package/version/network/Script checks
  freeze + disable -> inspect public destination identities
  source UUID -> destination UUID / candidate identity mapping
  stage native + destination Room copy + selected preference merge
  key-byte invariant -> journaled activation / rollback
  explicit enable only after no pending journal; no automatic launch
```

## Components

| Component | Responsibility |
|---|---|
| scripts/h02_package.py | Exact schema, address checksum and packed Script identity, expected network/genesis/APK, native KV shape/progress, SHA-256 validation, known-secret gate, manifest creation and UUID/candidate mapping |
| scripts/h02_device.py | Explicit emulator serial/AVD gating, installed APK checks, process stop + package disable, run-as transport, approved-file-only pull, separate stage/commit/rollback/enable commands |
| scripts/helper/H02State.java | Standalone Android SQLite/XML operations; public extraction inside source sandbox; logical native snapshot; destination-only staging, key-byte invariant, durable activation journal and rollback |
| scripts/build-helper.ps1 | Compile helper against API 36 and dex for API >=26 without modifying or linking Pocket |
| scripts/test_package.py | Synthetic positive/negative policy tests; no adb or historical data |
| scripts/test_android_helper.py | Synthetic API-36 emulator SQLite/WAL/export/stage/activation/interruption/rollback checks. Refuses if Pocket is installed; never opens a Pocket wallet sandbox |
| scripts/probe-empty-sandbox.py | Verify emulator/APK/run-as/helper execution in a freshly installed, unlaunched Pocket sandbox; refuses initialized wallet files, does not initialize Pocket or LC, leaves app disabled |
| scripts/build-pocket-native.ps1 / build-pocket-android.ps1 | Pinned build entry points with generated output under runs and an emulator-only native ABI |
| scripts/wo2-build.init.gradle | External output redirection and x86_64-only APK ABI selection, without changing application behavior |
| scripts/create-avd.ps1 | Create the named fresh AVD under runs; refuses an existing target |

The helper has no network, encryption, key derivation, signing, backup-provider or UI functionality. General app security settings and key records are not in the source export. Errors return fixed codes and helper method/line positions, not SQL values, recovery inputs or database dumps.

## Actual debug-sandbox transport verification

The freshly installed, unlaunched APK was probed on emulator-5580 after the shell-UID synthetic SQLite tests. This caught two defects not exercised by those earlier tests: legacy adb exec-out lost useful remote exit status/quoting semantics, and Windows adb shell truncated raw binary stdin at Ctrl-Z. The truncated helper was 705 bytes, exactly its first Ctrl-Z offset, instead of 11,827 bytes; Android refused to load it. Those were helper transport failures, not Pocket/LC startup failures.

The final transport uses adb shell -T (shell v2, no PTY) for real remote exit codes, shlex-quoted command arguments and base64 for all uploaded/downloaded file bytes. Every upload is checked against a remote SHA-256 before use. No raw Room file is added to the allowed download paths. A 65,792-byte generated fixture covering all 256 byte values round-tripped exactly under the actual app UID; a failed remote test and attempted overwrite both refused, with original bytes intact. The helper then passed its probe without loading Pocket's Application. An incorrect installed-APK digest also refused before mutation. Evidence: runs/wo2/empty-sandbox-probe-3.log and device-negative.log.

The final probe also creates a nonsensitive h02_probe(value INTEGER) scratch database beneath its own files/h02-probe-* directory, writes/commits in WAL mode and reopens read-only. This passed under the actual app UID after an emulator restart (empty-sandbox-probe-final2.log). It does not create the app's Room database, keys, preferences or native store. The earlier complete export/stage/rollback synthetic tests used generated /data/local/tmp fixtures; the real-UID probe validates the actual transport and framework SQLite access without performing a wallet restore.

The host currently buffers each transferred file and its base64 representation in memory. This is adequate for the bounded fixture preparation, not a qualified large-database streaming transport. All transfer/check/staging time belongs in B's future measurements.

## Fail-closed behavior

Host package rejection happens before any destination mutation. Unknown members/JSON fields, wrong build/schema/network/genesis, mismatched scripts/candidates, bad hashes, missing data and known sensitive structures refuse the operation. The manifest's trusted digest is mandatory. Export creates an exclusive new output directory; a failed extraction does not produce a successful receipt.

Source and destination freeze include package disable and process checks; no foreground-service-only shortcut. The host will not target a physical serial, an arbitrary AVD or an unverified APK. ADB commands always carry an explicit emulator serial. Package source/destination data never determine shell commands or extraction paths.

Stage touches only newly created files in the disabled destination sandbox. It checks that the public destination snapshot still matches the inspected one. Keys must already exist, exactly two wallets must match, and no pending actions are permitted. Source IDs are translated to destination IDs; source key IDs/ciphertext are never installed. All target key rows are compared internally before/after staging.

Commit checks staged file hashes, writes/fsyncs a journal, moves originals into a private sandbox directory, and installs the complete staged set. Any interruption leaves the app disabled and journaled. Rollback restores original files, including their sidecars, before removing the journal. Directory syncs bound filesystem ordering. This is a test harness protocol, not a transactional Pocket importer or a guarantee against an operator manually bypassing package disable.

Commit also requires the live destination file hashes/absence to match the staged baseline. A user launching or changing the destination between stage and commit cannot silently overwrite newer destination state with an old stage. Rollback verifies full baseline hashes before declaring success. These checks and an interruption after the first rename passed in the Android synthetic test.

## Command surface for later PM-approved WO-3

Run `python scripts/h02_device.py --help` and each subcommand's `--help` for exact required arguments. No command launches Pocket. Paths for export output must resolve beneath H02-P0/runs.

```
python scripts/h02_device.py export --serial emulator-5580 --apk-sha256 <recorded-apk-sha256> --genesis <trusted-testnet-genesis> --boundary <H> --boundary-hash <H-hash> --coverage <public-coverage.json> --out runs/wo3/package-B
python scripts/h02_package.py runs/wo3/package-B --trust <trusted-manifest-sha256> --apk-sha256 <recorded-apk-sha256> --genesis <trusted-testnet-genesis>
python scripts/h02_device.py stage --serial emulator-5580 --apk-sha256 <recorded-apk-sha256> --genesis <trusted-testnet-genesis> --package runs/wo3/package-B --trust <trusted-manifest-sha256>
python scripts/h02_device.py commit --serial emulator-5580 --apk-sha256 <recorded-apk-sha256> --token <printed-stage-token>
python scripts/h02_device.py rollback --serial emulator-5580 --apk-sha256 <recorded-apk-sha256> --token <stage-token>
python scripts/h02_device.py enable --serial emulator-5580 --apk-sha256 <recorded-apk-sha256>
```

Rollback is used only after an interrupted activation; stage failure before journaling leaves live destination state unchanged. Export freezes the source and leaves it disabled, suitable for later loss simulation. No restore command has been run against an actual wallet in WO-2.

Coverage JSON maps source public wallet UUIDs to earliest correct nonnegative block heights. Expected genesis, H hash and the independent fixture ledger must be established before a real run. Placeholder values above are not ready-to-run recovery instructions.

## Remaining measurement boundary

The helper observes public account metadata and native registrations. It does not yet automate all WO-1 acceptance observations: exhaustive live cells/history, DAO compensation/maturity, post-H spends, signing readiness and restart behavior still require the WO-3 oracle/observation plan. Synthetic passes cannot certify these outcomes. No speed threshold or recovery-time claim follows from this work.
