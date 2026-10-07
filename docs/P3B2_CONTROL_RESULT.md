# WO-3B2-R4 CONTROL A2 result

**PASS, including restart and both-account local signing readiness.**

Pocket v1.8.5/code 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`; approved APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. TESTNET. API 36 / x86_64 / 2048 MiB / 2 vCPUs / WHPX / Intel Iris Xe HOST GPU / headless / no snapshots. Explicit emulator serial `emulator-5580`. Physical Samsung untouched; D2 excluded; production Pocket source unchanged.

Fresh independent userdata/encryption backing was created from the installed API-36 image. Pre-launch free space: 20.093 GiB (21,575,032,832 bytes). Pre-install Pocket was absent; before first launch Room DB, native TESTNET store, Pocket preferences and key backups were absent. Exact APK installation/hash and role registry were verified. New destination UUIDs and Keystore state were retained; source security/key rows were never restored. Provisioning evidence: `control/boot/provision.json`, `control/fresh-runtime.json`.

Pre-install Android boot ANRs/crashes recorded: 2. Where nonzero, the existing settled-Android gate required seven Settings/Home/system-server observations for at least 180 seconds without new ANRs/crashes before installation. This is recorded as a boot qualification caveat, not claimed as an ANR-free first boot.

Normal automatic mnemonic recovery and supported Add account flow produced the expected account-0/account-1 identities and parent relationship. No Room/account row injection. Both CUSTOM historical floors were verified. UI switching continuations and discovery replays are included in total elapsed time, not deducted.

No H2 package was used. An initial exact check already matched all owned canonical facts but rejected unsettled discovery/global native progress (four pending probes). That incomplete capture is retained at `control/r4-first`; normal Pocket resume completed the replay. A second capture, `control/r4-settled-first`, had complete discovery/progress but its latest native tip differed from the public node's canonical block at the same height; the audit refused it. Its public anchor diagnostic is retained, and F2 itself remained canonical. Normal catch-up then passed the full canonical gate. Startup UI timing refusals were handled by a bounded public-authentication wait in the harness; Pocket was not modified, and all such elapsed time remains included.

Accepted per-account native/Room progress after restart:

| Account | Local wallet UUID | Parent UUID | Native registration | Native global minimum | Verified tip | Room saved cursor |
|---|---|---|---:|---:|---:|---:|
| 0 | `4ec0c3b2-bf3d-4575-bf7d-c87831d7e856` | `None` | 22652933 | 22652933 | 22652934 | 22652933 |
| 1 | `8bb0e517-1f46-4c53-a0fe-c01027ba68a2` | `4ec0c3b2-bf3d-4575-bf7d-c87831d7e856` | 22652933 | 22652933 | 22652934 | 22652933 |

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
| control r4-canonical-first | 22652907 | 2740637 | 2620971 | 36632 |
| control r4-canonical-restart | 22652930 | 2752152 | 2631983 | 38220 |

Force-stop/normal authentication/relaunch preserved the canonical semantic hash `0f9c153bd08918b9231c4b32131f9552e9bb3a515833795e7066e017e749190e`. Challenge signatures for both accounts verified locally against their expected Scripts before and after restart; no transaction was broadcast for signing checks. This covers emulator V1 security, not physical-device V2 authentication. Full acceptance result: `control/result.json`; first observation `r4-canonical-first`, restart observation `r4-canonical-restart`.

Total recovery time from before first Pocket launch through complete restart acceptance: **2239.181 seconds**. Key/security: 38.464 s. TESTNET account-0 registration requested at 89.713 s. Account-1 coverage requested at 311.732 s.

Registration-to-first exact acceptance: 1939.635 s, an inclusive reconstruction interval containing account setup, UI reconciliation, discovery, replay and audit; pure historical reconstruction and post-F2 tip catch-up were not independently separable. Runtime retired only after accepted captures and hashes were sealed; free afterward 20.048 GiB (21,526,282,240 bytes).
