# WO-3C phone Control P-A

**PASS. Normal recovery, real device security, confirmed signing and cold restart verified.**

Samsung SM-S9180 (`R5CW6127VPR`), Android 16/API 36, arm64-v8a, 4096-byte pages. Pocket 1.8.5/code 27, TESTNET, source commit `b28979de744798ffb75367b031d4871ec3af1a12`. Phone APK SHA-256 `2cb5f4597b732938105b3a6ca08e7a513d792d19fb4d59b16e2ae82fb8f3a717`; signer `bb4cbddbe25b03a1bac59f9c139f845b15869d0507198a9271103f3a64c96b9a`. Physical phone used; D2 excluded.

Pre-destructive custody gates verified the protected fixture, both known paths, exact approved artifact, immutable H2 and historical evidence/oracles. Only Pocket user-0 data was cleared. Fresh-state evidence proves absence of wallet/Room/native/preferences/key backups/restore journal and both Pocket Keystore aliases. No unrelated phone data was touched. No H2 package was used in Control.

Protected normal mnemonic recovery and supported Add account created account 0 `m/44'/309'/0'/0/0` and account 1 `m/44'/309'/1'/0/0`. Genuine Android key-encryption/account authentication was observed and manually approved. Normal Pocket setup/unlock used protected input without credential output. Both key rows have kdfVersion 2; fresh V2 alias metadata establishes per-operation authentication and Trusted Environment protection. No source key/security state was imported.

Historical CUSTOM floors: 22,369,937 and 22,647,000. Exact canonical gates PASS for identities, Scripts, account/parent mapping, no cross-account leakage, live outpoints/balances, native/Room history, both B2 post-H2 activities, DAO owner/outpoint/principal/stage/live status/deposit header/epoch and coherent progress. The 1,000 CKB DAO remains DEPOSITED under account 1. Background discovery settled to 50 EMPTY candidates plus one RESTORED account, no pending probes/matched work.

Pocket reviewed and signed a 61 CKB account-0 self-transfer after genuine manually approved Android signing authentication. Transaction `0x2067edf16ab143e7bff9ef91803e36ce6a32347c632c75a37d382443ae379738` was broadcast and confirmed on canonical TESTNET; its recoverable witness signature independently matches account 0's Script. No host private-key signer was used. FP: **22,655,648**, hash `0x5746d7a8268374be4b3bf39e9d81625ca0acc6cee2ddb198103d3f436ae21b23`.

The required post-signing cold restart, normal Pocket authentication and native ARM64 startup PASS. Exact post-restart acceptance includes the FP transaction, both accounts, DAO and persisted progress. Fresh Keystore protection/creation metadata remains unchanged; no auth/Keystore/native/schema errors were observed. FP semantic SHA-256 `e3075d29259b8b39c440691296b7d9c29cba8ab664361e1fc51bea9c6ea60c21`.

At canonical block 22,655,655, Pocket estimate 4,116,416 shannons versus canonical 3,936,679. Canonical occupied capacity 102 CKB; reader 61 CKB. Audit verdict `KNOWN_READER_DEFECT_ONLY`; no recovery-specific DAO divergence. Compensation remains separate from canonical position acceptance.

Elapsed time: 60 min 20 sec (elapsed, including manual authentication and qualification overhead; not a speed benchmark). Two premature captures were correctly refused as unsettled while four discovery probes scanned; navigation before retirement restarted those probes and prolonged Control. These retained observations are not recovery failures. The final uninterrupted retirement and unchanged canonical acceptance gates passed. Public alias metadata receives separate strict schema checks for evidence; original package secret exclusion remains unchanged.

Evidence: `runs/wo3c/phone-ab/control/result.json`, `control/evidence-manifest.json`, `control/ready-initial-acceptance.json`, `control/FP-restart-acceptance.json`, `control/signing-result.json`, `FP-boundary.json`, `oracle-FP.json`. Evidence was hash-sealed/reverified before Candidate's authorized Pocket-only reset.
