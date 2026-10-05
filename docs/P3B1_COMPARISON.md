# WO-3B1-R2 comparison: B1-PASS

Sanitized same-version wallet-owned state recovery worked for the basic one-funded-Script case. Independent normal Control A and package-restored Candidate B converged to the same exact F state and preserved it after restart. B removed a Cell that was live in H, fetched the post-H transaction and new outputs, and rebuilt the omitted app caches.

## Exact shared result

Network TESTNET; account `m/44'/309'/0'/0/0`; CUSTOM coverage start **22,369,937**; accepted through F **22,646,322**. Exact capacity **1,999,999,998,000 shannons = 19,999.99998 CKB**. No DAO. Shared semantic SHA-256: **`13cb9e9b74c918a9fe27bb9a9205545125998bfcb86fb5f02408a23db754567a`**.

| Final live outpoint | Capacity (shannons) |
|---|---:|
| `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66:0` | 1,000,000,000,000 |
| `0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7:0` | 10,000,000,000 |
| `0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7:1` | 89,999,999,000 |
| `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894:1` | 899,999,999,000 |

Covered history (four unique transactions):

- `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66`
- `0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7`
- `0xb7503283af42a8fd1595306e2d5dd4a789e103980207fdafb5229b2e20b7113c`
- `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894`


Both arms independently checked the account mapping, full Script, exact outpoints/capacity, covered history, app caches, U absence, post-H outputs, progress through F and restart persistence. Different destination UUIDs correctly mapped to the same public account. SOURCE was stopped/sealed before either measured arm, with no later source DB/emulator access. Only the retained keys, H package, pre-recorded public oracle and public-chain observations were available. H/F canonical hashes and unchanged final fixture state were rechecked independently after the arms.

## Observed timing

| Observation | Control A | Candidate B |
|---|---:|---:|
| Normal key/security recovery | 35.590 s | 35.108 s |
| Normal network/coverage UI | 52.720 s | 46.365 s |
| Package operation, including transfer/validation/activation | Not used | 8.480 s |
| First exact F-state acceptance from launch | **800.542 s (13m20.542s)** | **208.774 s (3m28.774s)** |
| Additional restart/continuation qualification | 652.532 s | 84.366 s |
| Full measured acceptance | **1,453.074 s (24m13.074s)** | **293.140 s (4m53.140s)** |

A's first reconstruction/catch-up/app reconciliation/exact-check interval after correct coverage request was 712.232 s. Its ordinary restart then activated five remaining automatic discovery probes, adding a 570.329 s discovery/restart/check interval plus an 82.202 s final settled restart. This behavior was already reproduced on SOURCE before H and is not an H02 restore failure. B preserved all 51 EMPTY discovery states and resumed from H; its post-unlock catch-up/app reconciliation/exact-check interval was 106.084 s. Full per-phase tables and unresolved timing separation are in the individual arm reports.

Timer starts before first Pocket launch, after Android/APK provisioning, and ends after exact restart acceptance. Host monotonic events define durations. It includes normal UI automation, package handling, observation intervals, quiescence and exact checks. Native reconstruction, peer acquisition, catch-up and app polling overlap; their pure internal costs are not independently measured. SOURCE preparation/export is separate (export 3.412 s).

**LIMITED PERFORMANCE FIXTURE. Claimable production-user speed result: NO.** One sequential emulator run, roughly 25-day original history, three original transactions plus one deliberate self-transfer, one funded Script and no DAO. The observed reduction demonstrates avoided reconstruction/discovery work in this run. Peer conditions and measurement overhead are uncontrolled; there is no replication, device distribution, older/denser history or production export/import flow. No product-level multiplier or threshold is inferred.

## What the package bought

H retained approved native chain/Script/history/live-cell state plus public wallet/account identity, settled discovery and coverage/progress policy. Three files total 1,895,341 bytes; no raw source Room DB or key/PIN/Keystore data. Destination keys were recreated normally, IDs remapped, and app caches regenerated. The old U-bearing native digest was verified immediately after activation, before normal local catch-up.

This is trusted-self persistence: the destination trusts pre-H source work and the separately retained package digest. It continues normal local chain verification after restoration. It does not independently prove pre-H completeness, tolerate a malicious source, establish arbitrary cross-version/cross-ABI portability, or implement a production backup UX/encryption/cloud protocol. Hash integrity must not be described as historical completeness.

## Negative gates, preservation and scope

Nine actual-package variants all refused before activation: corruption, missing payload, network, genesis, Pocket version, Room schema, native schema, manifest hash, payload hash. Existing 33 legacy and six B1 policy tests and synthetic Android extraction/staging/activation had passed before real execution; no source production changes were required. The known-sensitive-structure gate remains explicit. Final fixture-secret audit: **PASS**, 278 document/script/capture files checked, including the sanitized packages. Secret-bearing AVD userdata and sealed SOURCE native captures are excluded; sealed SOURCE captures are not reread after loss. `runs/wo3b1-r2/final-audit.json` records the audit and staging boundary.

Machine-checkable result: `runs/wo3b1-r2/comparison.json`, generated by `scripts/r2_compare.py`. It enforces U live in H, absent in both arms, both new outputs/history present, exact capacity/semantic equality, restart evidence, and all nine negative refusals. Supporting canonical public check: `public-final-check.json`.

Pocket commit `b28979de744798ffb75367b031d4871ec3af1a12` and production checkout unchanged. The Samsung and D2 were untouched. No second actual account, DAO, additional transaction, cloud/UI feature or B2 work.

The previous environmental B1-INCONCLUSIVE reports are preserved with checked SHA-256 hashes in `runs/wo3b1-r2/previous-b1-reports/`. Original run artifacts, R1 diagnosis and qualified profile remain unchanged.
