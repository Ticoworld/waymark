# WO-3B2-R4 SOURCE result

**PASS under the PM-approved canonical DAO-position contract.** The R2/R3 SOURCE was integrity-checked and resumed, without rebuilding accounts or transactions. The earlier R2 compensation halt remains preserved as history.

Pocket v1.8.5/code 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`; approved APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. TESTNET. API 36 / x86_64 / 2048 MiB / 2 vCPUs / WHPX / Intel Iris Xe HOST GPU / headless / no snapshots. Explicit emulator serial `emulator-5580`. Physical Samsung untouched; D2 excluded; production Pocket source unchanged.

Both accounts matched their public canonical history, exact live Cells and balances before export. Supported UI reconciliation and restart passed, discovery was settled, both Scripts were registered, and per-Script/native/Room progress was coherent. The first proposed H2 capture had a sibling tip and was rejected; no package or event was produced from it. A later capture passed canonical chain anchoring.

| Account | Local wallet UUID | Parent UUID | Native registration | Native global minimum | Verified tip | Room saved cursor |
|---|---|---|---:|---:|---:|---:|
| 0 | `043746a4-de6d-4911-8e00-5d663bdb0e37` | `None` | 22652549 | 22652549 | 22652549 | 22652549 |
| 1 | `36ac4ecb-c83e-4a00-96db-09f2d6be58a7` | `043746a4-de6d-4911-8e00-5d663bdb0e37` | 22652549 | 22652549 | 22652549 | 22652549 |

H2 22652549, hash `0x3f96acadbf4ef0d847db36468ca13feb37630fd5a156a5540713897c0dd4e3ee`. Package `runs/wo3b2/package-H2-immutable`; 1,904,717 bytes; export 4.398 seconds; trusted manifest SHA-256 `56d4a6506641c62797531eb0f093c4930131a9046d26351377c292568d7d879e`. Logical payload: sanitized public wallet/account/mapping/coverage/progress/discovery state and native TESTNET state. The two accounts retain distinct derivations and parent relationships. Balance/history/header/DAO caches, pending actions, contacts/freeform metadata, source key material/security and peer identity are excluded and reconstructed.

Structural and exact-credential exclusion passed: mnemonic, BIP39 seed, both derived private keys and emulator PIN absent in checked encodings. `key_material`, PIN/security preferences, key backups and Android Keystore state are excluded. Manifest, payload hashes, approved version/schema, TESTNET genesis and account/Script checks passed. Receipt: `source/package-receipt.json`.

| Observation | Inferred estimate header | Pocket compensation (shannons) | Canonical compensation (shannons) | Cache age at capture (ms) |
|---|---:|---:|---:|---:|
| SOURCE H2 | 22652548 | 2560902 | 2449084 | 21969 |

After the two authorized confirmed events, F2 22652587 was independently captured. SOURCE remained frozen at H2; no source catch-up was used by either arm. SOURCE was stopped and declared lost, 117 compact files were hashed, and exact allowlisted disposable runtime images were retired. Logical runtime bytes removed: 2,936,888,656; observed host free-space delta: 5,322,153,984; free afterward: 20.093 GiB (21,575,172,096 bytes). The delta is a host observation, not solely logical image size. A PowerShell receipt-size summing error occurred after deletion; every planned path was verified absent before receipt finalization. No additional deletion was performed.

`source/LOST.json`, `evidence-seal-r4.json`, `runtime-retirement-plan.json` and `runtime-retirement.json` preserve this boundary. After loss, arms used only normal recovery secrets, the sanitized package where authorized, retained public facts and public chain access; no SOURCE guest/native/Room state was queried.
