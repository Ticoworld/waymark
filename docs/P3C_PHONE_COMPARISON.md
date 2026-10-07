# WO-3C phone A/B comparison

**PHONE-PASS. Canonical recovery equivalence YES; recovery-specific DAO divergence NO.**

Samsung SM-S9180 (`R5CW6127VPR`), Android 16/API 36, arm64-v8a, 4096-byte pages. Pocket 1.8.5/code 27, TESTNET, source commit `b28979de744798ffb75367b031d4871ec3af1a12`. Phone APK SHA-256 `2cb5f4597b732938105b3a6ca08e7a513d792d19fb4d59b16e2ae82fb8f3a717`; signer `bb4cbddbe25b03a1bac59f9c139f845b15869d0507198a9271103f3a64c96b9a`. Physical phone used; D2 excluded.

| Requirement | Control P-A | Candidate P-B |
| --- | --- | --- |
| Fresh Pocket sandbox and Keystore | PASS | PASS, independent of Control |
| Normal two-account key recovery | PASS | PASS before H2 |
| Exact account/Script/parent mapping, no leakage | PASS | PASS |
| Canonical Cells, balances, covered history | PASS | PASS |
| Both B2 post-H2 activities | PASS | PASS after stale H2 catch-up |
| DAO canonical position/header/history | PASS | PASS |
| Known estimate defect only | PASS | PASS, separately audited |
| Genuine Android signing auth and confirmed transaction | PASS | PASS after restore |
| Cold restart/native persistence | PASS | PASS |

Common FP **22,655,648 / 0x5746d7a8268374be4b3bf39e9d81625ca0acc6cee2ddb198103d3f436ae21b23** includes Control transaction `0x2067edf16ab143e7bff9ef91803e36ce6a32347c632c75a37d382443ae379738`. Control post-restart and Candidate caught-up canonical states have identical semantic SHA-256 `e3075d29259b8b39c440691296b7d9c29cba8ab664361e1fc51bea9c6ea60c21`. UUIDs are normalized through exact account/Script identity rather than compared across independent recovery installations. Native and Room histories, live Cells, balances, historical coverage and canonical DAO fields all pass.

Candidate's later transaction `0xe4cbdffa9002b0283c2c71cc19ec646b85cb58274b8f45d72496e78ae96b4cbd` is explicitly accounted for. Its canonical inputs are removed from FP live Cells and its self outputs added; this exactly produces the final oracle. Account-0 history adds exactly this transaction and spendable capacity falls only by its **1000 shannon** fee. Account 1/DAO history and live state remain identical. Later final tips are not compared blindly against Control's earlier tip.

Destination security remains independent: Control aliases were absent after reset, Candidate created fresh authenticated V2 security normally, activation preserved its creation/protection metadata and encrypted rows, and confirmed real-device signing succeeded afterward. No source security material was imported, no system credential collected and no Android authentication bypass used.

H2 manifest/package, original emulator APK, x86 validator/transport, B1/B2 evidence and production Pocket source remain unchanged. No physical data outside Pocket was touched; no historical H02/D2/iBytes cleanup occurred. Device page size is 4096; recurring 16 KB alignment warning is acknowledged normally and retained as a separate native packaging follow-up, with no H02 block or claim of 16 KB support.

Timing includes manual auth/setup and Control discovery/automation delays and is not a controlled performance benchmark. Scope: one disposable TESTNET fixture, two accounts/Scripts, one active DAO deposit, same pinned Pocket source/debug build on this Samsung; DAO withdrawal and cross-version/16 KB-device behavior were not required or demonstrated. Evidence: `runs/wo3c/phone-ab/comparison.json`, both arm evidence manifests, FP/final oracles and `final-evidence-manifest.json`.
