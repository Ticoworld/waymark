# WO07-R5: Genuine Neuron Recovery

Date: 31 October 2026

## Verdict

**FIXTURE OR RUNTIME BLOCKED.** I prepared an isolated copy of the installed Neuron v0.204.1 release that sets Electron `userData` to a dedicated `%TEMP%` profile before Neuron loads its controllers. That profile was preselected to TESTNET Light Client. The copied executable then exited immediately with code 0 and opened no window. No Neuron-created wallet, address, Script, sync-progress row, TESTNET activity, source artifact, or application replay was produced.

The R3 adapter is destination-import only, so it cannot export a new Neuron-owned Script artifact. That exporter work was not started because the required Neuron wallet could not be created. There is no application or acceleration result to report.

## Runtime and isolation attempt

- Installed and copied Neuron binary: v0.204.1.0, SHA-256 `74abd9a83cf3a4bfbfb70d6edca49c12d73dc8f272f219ea56dfde9f5f50cc18` (same hash in the installed and temporary copy).
- Installed `resources/app.asar` SHA-256 before the experiment: `ef42a37d28bebd729b4703266e1733315e3aa0605e66d8df6d92ee83c4a251bb`.
- Temporary application copy: `%TEMP%\\wo07-r5-neuron-app`.
- Isolated user-data path: `%TEMP%\\wo07-r5-neuron-userdata`.
- The temporary archive entry `dist/main.js` was changed to call `app.setPath("userData", process.env.WO07_R5_USER_DATA)` before importing Neuron controllers. The archive patch tool re-read the produced ASAR and verified the entry hash and injected override. The installed program directory was not changed.
- The isolated profile contained only `networks/index.json`, selecting `light_client_testnet`, network type Light, with TESTNET genesis `0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606`. No wallet/settings/SQLite/key files were created.
- Launch attempts of the temporary copy exited with code 0 within eight seconds, no surviving Neuron process, no stdout/stderr, and no app window. A diagnostic attempt with `--enable-logging` exited with code 9 because the Neuron executable rejected those arguments. The installed app was never launched.
- The computer-use helper failed during initialization with `failed to write kernel assets: The system cannot find the path specified (os error 3)`. UI interaction was unavailable.
- C: had 5,464,600,576 bytes free at inspection and about 4.90 GB after copying the installed application. It remained above the 4 GB reserve. No build, dependency installation, chain download, or node synchronization occurred.

The existing Neuron profile was not read or modified. No mnemonic, password, private key, xpub, or wallet database was accessed. No TESTNET transaction was sent.

## What is established from prior executable work

WO07-R3 remains valid: the pinned D2 adapter imported the existing Pocket artifact into a copy of the independently validated CKB Light Client v0.5.4 RocksDB store, and the released RPC returned its exact historical results.

WO07-R4 remains valid: a Neuron-shaped grouped `get_transactions` request returned eight transaction groups from that artifact. On a disposable store, Neuron-like `set_scripts(..., "partial")` rewound the native cursor to the supplied start boundary while leaving imported history queryable. That explains why the two-phase lifecycle matters, but it did not establish a genuine Neuron wallet or run Neuron's cache/queue/persistor.

Neuron source at `a926e3383d3a3e305b3bde7d233474515ef01a2e` derives account identity through `AccountExtendedPublicKey.ckbAccountPath`, produces address metadata through Lumos, and creates default lock Scripts from the derived Blake160. It initializes missing `SyncProgress` from the ordinary start floor, then calls `set_scripts` for newly registered scripts. No R5 runtime established the exact account 0 Script under a Neuron-generated wallet ID.

## Required work not reached

| Requirement | R5 result |
| --- | --- |
| Isolated Neuron UI startup and supported wallet creation | Blocked; copied app exits before a window |
| Neuron-generated wallet ID and exact derived Script | Not produced |
| Genuine TESTNET receive and spend | Not attempted; no wallet address |
| v0.5.4 source export for the Neuron-owned Script | Not implemented; existing adapter is destination-only |
| App progress initialization barrier and cursor preservation | Not run in Neuron |
| `LightSynchronizer.upsertTxHashes()` | Not run |
| `IndexerTxHashCache`, normal queue, `TransactionPersistor` | Not run |
| Exact history/input-output/Cell/balance comparison | Not run |
| Interrupted replay and cold application restart | Not run |
| DAO state | Not tested |
| Filtering avoided or performance | Not measured |

No activity or successful recovery is fabricated. The old Pocket fixture was not reassigned to a Neuron wallet.

## New supporting files

- `tools/wo07-r5/patch-isolated-neuron-asar.js`: creates a modified ASAR in the disposable app copy, updating the Neuron main entry integrity and verifying the new entry.
- `tools/wo07-r5/testnet-networks-index.json`: isolated initial built-in network selection.

The actual temporary app copy, patched ASAR, and isolated profile are under `%TEMP%`; the installed app, Neuron source, original Waymark evidence, Pocket source and D2 pinned checkout were not modified. The computer-use helper was unavailable, so no screenshots or UI values exist.

## Exact next action

Resolve the packaged-app startup issue before creating any wallet. Reproduce the failure with a copy of v0.204.1 while capturing Electron's earliest startup diagnostics and confirming the `userData` override is received. If the packaged app still exits, use a dedicated Windows test account or a minimal isolated Electron test harness that loads the exact Neuron v0.204.1 modules and writes all user data to a verified temporary path; do not point the installed app at the existing user profile.

After isolated startup works, create the disposable wallet through Neuron's supported UI and keep its seed local. Confirm the account-0 lock Script and wallet ID from Neuron-generated public metadata. Then determine whether the pinned D2 experiment can export the genuine v0.5.4 native store; implement a source exporter only if needed. Establish the app's legitimate progress row before importing, stop synchronization at a controlled barrier, import through the isolated adapter, and replay with Neuron's normal cache/queue/persistor. At each stage check whether startup resets the native cursor and whether `[floor,H+1)` includes any H transaction. Require exact state and restart before assessing acceleration.

Do not proceed to a comparative performance test until genuine Neuron ownership and normal application replay both pass.

## Pinned references

- Neuron release runtime: `v0.204.1`; source: `nervosnetwork/neuron` at `a926e3383d3a3e305b3bde7d233474515ef01a2e`.
- CKB Light Client target: `v0.5.4`; source `778590aa3ad7f71ee80b2d4c54af02c42e2dfa25`.
- Prior native adapter evidence: [WO07-R3](WO07_R3_NATIVE_ROCKSDB_ADAPTER.md).
- Prior Neuron initialization and grouped RPC evidence: [WO07-R4](WO07_R4_NEURON_APPLICATION_REPLAY.md).
- Neuron wallet and sync implementation links are pinned in [WO07-R4](WO07_R4_NEURON_APPLICATION_REPLAY.md#pinned-source-references).
