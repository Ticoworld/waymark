# WO-3B2-R4 CANDIDATE B2 result

**PASS, including restart and both-account local signing readiness.**

Pocket v1.8.5/code 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`; approved APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. TESTNET. API 36 / x86_64 / 2048 MiB / 2 vCPUs / WHPX / Intel Iris Xe HOST GPU / headless / no snapshots. Explicit emulator serial `emulator-5580`. Physical Samsung untouched; D2 excluded; production Pocket source unchanged.

Fresh independent userdata/encryption backing was created from the installed API-36 image. Pre-launch free space: 20.051 GiB (21,530,075,136 bytes). Pre-install Pocket was absent; before first launch Room DB, native TESTNET store, Pocket preferences and key backups were absent. Exact APK installation/hash and role registry were verified. New destination UUIDs and Keystore state were retained; source security/key rows were never restored. Provisioning evidence: `candidate/boot/provision.json`, `candidate/fresh-runtime.json`.

Pre-install Android boot ANRs/crashes recorded: 0. Where nonzero, the existing settled-Android gate required seven Settings/Home/system-server observations for at least 180 seconds without new ANRs/crashes before installation. This is recorded as a boot qualification caveat, not claimed as an ANR-free first boot.

Normal automatic mnemonic recovery and supported Add account flow produced the expected account-0/account-1 identities and parent relationship. No Room/account row injection. Both CUSTOM historical floors were verified. UI switching continuations and discovery replays are included in total elapsed time, not deducted.

The immutable H2 package was validated against trusted digest `56d4a6506641c62797531eb0f093c4930131a9046d26351377c292568d7d879e`, mapped to freshly recovered destination accounts, transferred, staged and activated using the approved WO-2 helper. Activated native payload hash matched `8a027384037de94cd7bad5903b563b8dc593452fe89be35814c17993dd747dc1` before launch. The actual guest pre-launch capture `candidate/r4-restored-H2` proves U was restored live and both post-H2 transactions absent, with progress at H2. Room DAO, transaction and balance caches were empty, as intended; source caches were not restored. Proof: `candidate/restored-stale-proof.json`. Normal catch-up removed U, indexed account-0 replacements and account-1 incoming Cell, and reconstructed application/DAO caches. Neither Script acquired the other's state.

Accepted per-account native/Room progress after restart:

| Account | Local wallet UUID | Parent UUID | Native registration | Native global minimum | Verified tip | Room saved cursor |
|---|---|---|---:|---:|---:|---:|
| 0 | `60c276f2-6df6-486c-9cab-eed34e73c53b` | `None` | 22653036 | 22653036 | 22653040 | 22653036 |
| 1 | `1dcacc05-9def-4303-b980-884e53b9dacf` | `60c276f2-6df6-486c-9cab-eed34e73c53b` | 22653036 | 22653036 | 22653040 | 22653036 |

Exact accepted live set:

| Account | Outpoint | Capacity (CKB) | Kind |
|---|---|---:|---|
| 0 | `0xb23fbbb1db9ca0da48f76993e9258fdadb0f3bc81d9999924561e72583aa5d5a:1` | 7499.99997000 | ordinary |
| 0 | `0xce0b13ba3f23babc6e4cc011a992b1f7bf610dd92b4f6719afde1c91a5e2ab39:0` | 100.00000000 | ordinary |
| 0 | `0xce0b13ba3f23babc6e4cc011a992b1f7bf610dd92b4f6719afde1c91a5e2ab39:1` | 9899.99999000 | ordinary |
| 1 | `0x2a6b71946100aef488a9bb505b27bc819d34754a4f6611d4bf6edbec53b5f00f:0` | 100.00000000 | ordinary |
| 1 | `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2:0` | 1000.00000000 | DAO deposit |
| 1 | `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2:1` | 999.99999000 | ordinary |

Both spendable balances and six/three covered histories match F2; all app transactions are CONFIRMED/nonlocal. Account 1 retains its exact canonical DAO owner/lock/type/outpoint/principal/data/stage/live status/deposit block/hash/epoch/history, with null withdrawal/unlock metadata. Discovery is settled. Compensation refresh is bound to a fresh canonical header interval and matches the known 61-CKB formula; an unexplained estimate or unchanged old H2 cache would be rejected.

| Observation | Inferred estimate header | Pocket compensation (shannons) | Canonical compensation (shannons) | Cache age at capture (ms) |
|---|---:|---:|---:|---:|
| candidate r4-first | 22653011 | 2792705 | 2670766 | 40388 |
| candidate r4-restart | 22653038 | 2806222 | 2683693 | 30958 |

Force-stop/normal authentication/relaunch preserved the canonical semantic hash `0f9c153bd08918b9231c4b32131f9552e9bb3a515833795e7066e017e749190e`. Challenge signatures for both accounts verified locally against their expected Scripts before and after restart; no transaction was broadcast for signing checks. This covers emulator V1 security, not physical-device V2 authentication. Full acceptance result: `candidate/result.json`; first observation `r4-first`, restart observation `r4-restart`.

Total recovery time from before first Pocket launch through complete restart acceptance: **730.317 seconds**. Key/security: 33.823 s. TESTNET account-0 registration requested at 82.510 s. Account-1 coverage requested at 160.887 s.

Package transfer: 1.059 s; validation: 0.774 s; total package restore including mapping/staging/activation: 15.961 s. Launch request to first exact acceptance: 284.511 s, inclusive of catch-up, app reconciliation and acceptance audit. Pure native catch-up was not independently isolated. Accepted Candidate runtime is stopped/sealed and retained for PM review.

The first qualifying synced watcher sample occurred 106.382 s after launch request (about 33-second sampling granularity). It is an observed startup/catch-up bound; final exact acceptance still required the later canonical/native/Room audit.
