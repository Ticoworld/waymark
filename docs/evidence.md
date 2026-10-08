# Evidence and provenance

The authoritative technical closure is commit **`918efa774622497f673fa0e588d9d0e26c96d3a5`**. Presentation cleanup adds a descendant commit; it does not amend or rewrite this checkpoint. The [Pocket proof](pocket-proof.md) explains the findings and the [recovery model](how-it-works.md) explains their scope.

## Availability and custody

Git contains research source, synthetic tests, explanatory records and digest bindings. Raw manifests, chain oracles, APKs, runtime databases, captures and security evidence remain intentionally ignored in local custody. A public clone does not include them or the protected recovery fixture. Hashes bind retained bytes; they do not make private artifacts public or prove historical non-omission.

The closure review verified the six indexed evidence manifests below and their 20, 30, 16, 55, 40 and 10 members, plus the immutable saved package. Those are historical verification attestations. Cleanup rechecks available indexed files and package bindings offline; it performs no new device, transaction or wallet experiment. Nothing under local `private/`, `repos/` or existing runtime/evidence custody is removed or republished.

Some manifests bind historical public reports/tool source as well as local captures. After consolidation those report/source members are recovered from the closure commit, with their historical Windows checkout line endings when needed to match byte digests. The remaining raw members retain their exact local bytes. The manifests themselves are not rewritten to point at the new presentation files.

Historical IDs and local paths in this document serve only to locate exact original records. Older intermediate reports can say blocked, untested or inconclusive; the accepted final proof supersedes those conclusions without erasing them.

## Pocket and build pins

| Property | Sealed value |
| --- | --- |
| Pocket upstream | [RaheemJnr/pocket-node](https://github.com/RaheemJnr/pocket-node/tree/b28979de744798ffb75367b031d4871ec3af1a12) |
| Source/tag | `b28979de744798ffb75367b031d4871ec3af1a12` / `v1.8.5` |
| Application | `com.rjnr.pocketnode`, 1.8.5, versionCode 27, min SDK 26, compile/target 36 |
| Embedded native library | ckb-light-client-lib 0.5.4; vendored tree `3ac3e0ce1f4e46897d188b76c5b841b9097fa506` at `external/ckb-light-client`; no separately authoritative upstream commit was substituted |
| Room | 2.8.4, schema 17, identity `091b40f9618fee3fc8032ff01255a9a4` |
| Native storage | Logical SQLite KV, user version 0, explicit fixed-width/packed encodings |
| TESTNET genesis | `10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606` |
| Emulator APK | 49,764,015 bytes; SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f` |
| Emulator signer SHA-256 | `52bdccbe47ca004b6bfd7ffd374ba16bd4c41ad62e15ec9df398aeb0ead42ddc` |
| Phone APK | 48,502,369 bytes, ARM64 debug; SHA-256 `2cb5f4597b732938105b3a6ca08e7a513d792d19fb4d59b16e2ae82fb8f3a717` |
| Phone signing certificate SHA-256 | `bb4cbddbe25b03a1bac59f9c139f845b15869d0507198a9271103f3a64c96b9a` (Pocket repository debug certificate, matching prior installed signer; APK signature scheme v2 verified) |
| Official release, not selected | 38,174,535 bytes; APK SHA-256 `34a3f649bd3365de2caa6148d68fd548f061d02e85ca51158bd84c035cec2ee2`; signer `9c5130307bf2cbe9f9f918ed1fbba231ef040294aadc33b97f60c76662303f16`, incompatible with prior installed debug signer |
| Production Pocket source edits | None |

Actual build tools were Android Studio JBR/OpenJDK 21.0.10 (target bytecode 17), Gradle 8.14.3, AGP 8.13.2, Kotlin/KSP 2.3.10, Rust/Cargo 1.92.0 with locked dependencies, NDK 27.0.12077973/clang 18.0.1, Android native API 21 and `jni-bridge,portable`. Windows build adapters supplied host CRT/Perl prerequisites and redirected output without changing Pocket/Cargo.lock. JBR/NDK choices differ from exact release-CI selections; the final build used retained native inputs. This is recorded reproducible provenance, not a timestamp-independent byte-identical rebuild claim. Full host lock files and build recipes remain at the closure revision.

The x86 light-client shared library was 17,611,888 bytes, SHA-256 `fb8262af9279cd7379a2ab6d3a9c5397106647443012343af4241297859e402f`. The initial historical helper JAR was 12,193 bytes, SHA-256 `3c8c858e006c9ba082cb5e543dcf5198bd6e74a6489d9ce165f85768384d31ae`; later helper qualification belongs to its artifact/audit receipts. Renaming the public helper does not reproduce those historical binary hashes.

## Tested device and environments

Physical device: **Samsung SM-S9180**, Android 16/API 36, `arm64-v8a`, **4096-byte pages**. The exact sealed serial is `R5CW6127VPR`; it is historical device identity, not an instruction to target that phone. V2 destination key rows, authenticated Keystore creation/protection metadata and real signing were checked. No device credential or source Keystore material is published. The 16 KB alignment warning is separately recorded, not evidence of 16 KB support.

Emulator: API-36 default x86_64 image revision 2/extension 17, emulator 36.5.11.0/build 15261927, WHPX, Intel Iris Xe host graphics/driver 32.0.101.7088, 2048 MiB RAM, two vCPUs, Pixel 6 display, 6 GiB data partition, headless/no snapshots. One emulator ran at a time with explicit serial `emulator-5580`. Historical AVD `H02_P0_API36_X64` differs from the descriptive guard in the cleaned tools. Bounded qualification is not a minimum-resource or long-duration stability guarantee.

## Saved-state and comparison checkpoints

| Checkpoint | Height / canonical hash | Binding |
| --- | --- | --- |
| Initial saved state | 22,646,283 / `0x764023cd6da7a464f6c9b98fdffb2fd022c3384991f7f11a7cbf48142ecd30cc` | Manifest `f89fc4feeb019b47b625be8df71f5ef9cd64acdf2104cd793f113e0c9530fd12`; native payload `93792af4a841e5db03190aabb1749d4510b6665117a080ec12997387119fa719` |
| Initial comparison | 22,646,322 / `0xcf2e87ef4e69972230c850c681a3c411cd5228cb966985b381bcf0bba0e2ebd9` | Common semantic digest `13cb9e9b74c918a9fe27bb9a9205545125998bfcb86fb5f02408a23db754567a` |
| Richer saved state, also used on phone | 22,652,549 / `0x3f96acadbf4ef0d847db36468ca13feb37630fd5a156a5540713897c0dd4e3ee` | Manifest `56d4a6506641c62797531eb0f093c4930131a9046d26351377c292568d7d879e`; native payload `8a027384037de94cd7bad5903b563b8dc593452fe89be35814c17993dd747dc1` |
| Richer emulator comparison | 22,652,587 / `0x906b72dc199e58ece8ad3962685dba415642272085ae629ffc8c5ad18ac6c8c3` | Common semantic digest `0f9c153bd08918b9231c4b32131f9552e9bb3a515833795e7066e017e749190e` |
| Phone canonical comparison | 22,655,648 / `0x5746d7a8268374be4b3bf39e9d81625ca0acc6cee2ddb198103d3f436ae21b23` | Common semantic digest `e3075d29259b8b39c440691296b7d9c29cba8ab664361e1fc51bea9c6ea60c21` |
| State-assisted phone final restart | 22,655,881 / `0x7b03fcad102f69a2753dfc3c115c496b2430f11410970736a5a525c290cdff05` | Final oracle binding in the local digest index below; includes the later state-assisted transaction |

The richer package has exactly `manifest.json`, `app.json`, `native.sqlite`, totaling 1,904,717 bytes. Its unchanged member sizes/hashes are retained below. Source capture and phone destination qualification are separate; no manifest resealing or payload transformation occurred.

## Public fixture and transactions

The protected recovery fixture was established separately from an earlier Pocket 1.8.3 backup in local custody. The experiment source rebuilt the tested state normally under 1.8.5; it did not import the old phone's Room/native state or any D2-transplanted chain state. The recovery material stayed private and entered normal key-recovery flows, never the non-secret saved-state package. This origin is custody context, not a compatibility claim for the earlier version or another wallet.

Both locks use code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`.

| Account | Path | Lock args | Coverage floor |
| --- | --- | --- | ---: |
| Parent 0 | `m/44'/309'/0'/0/0` | `0xbc5882c4309431ee23ad7bbad4b5c3325539eebd` | 22,369,937 |
| Derived 1, parent 0 | `m/44'/309'/1'/0/0` | `0x2da024570462b0e2421d87abcbfebd4567d52ad5` | 22,647,000 |

| Event | Canonical transaction |
| --- | --- |
| Initial stale-state event, 100 CKB self-transfer at 22,646,305 | `0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7`; consumes `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894:0`, creates owned outputs 0/1, fee 1,000 shannons |
| Richer account-0 post-backup spend | `0xce0b13ba3f23babc6e4cc011a992b1f7bf610dd92b4f6719afde1c91a5e2ab39`; consumes `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66:0` |
| Richer account-1 post-backup incoming 100 CKB | `0x2a6b71946100aef488a9bb505b27bc819d34754a4f6611d4bf6edbec53b5f00f` |
| Baseline phone signing, 61 CKB self-transfer | `0x2067edf16ab143e7bff9ef91803e36ce6a32347c632c75a37d382443ae379738` |
| State-assisted phone signing after equivalence, 61 CKB self-transfer | `0xe4cbdffa9002b0283c2c71cc19ec646b85cb58274b8f45d72496e78ae96b4cbd` |

The two richer post-backup events share block 22,652,580/hash `0x413f758d5930756b01db459c3cdfa60e6a486414b4d296c2d52de521135e543a`. Spent-Cell RPC returned `unknown`, not literal `dead`; canonical committed inputs plus absence from the live index establish consumption. The common phone checkpoint includes baseline's signing transaction. The later state-assisted transaction is accounted for by exact input/output changes and its 1,000-shannon fee, rather than compared against baseline's earlier tip.

The initial comparison's four transactions are the initial stale-state self-transfer above, `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66`, `0xb7503283af42a8fd1595306e2d5dd4a789e103980207fdafb5229b2e20b7113c`, and `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894`. First relevant activity was 22,369,938 and last original activity 22,370,275. Exact final live capacity was 1,999,999,998,000 shannons.

| Initial comparison live outpoint | Capacity (shannons) |
| --- | ---: |
| `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66:0` | 1,000,000,000,000 |
| `0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7:0` | 10,000,000,000 |
| `0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7:1` | 89,999,999,000 |
| `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894:1` | 899,999,999,000 |

| Richer emulator comparison account / live outpoint | Capacity (CKB) |
| --- | ---: |
| 0 / `0xb23fbbb1db9ca0da48f76993e9258fdadb0f3bc81d9999924561e72583aa5d5a:1` | 7,499.99997000 |
| 0 / `0xce0b13ba3f23babc6e4cc011a992b1f7bf610dd92b4f6719afde1c91a5e2ab39:0` | 100.00000000 |
| 0 / `0xce0b13ba3f23babc6e4cc011a992b1f7bf610dd92b4f6719afde1c91a5e2ab39:1` | 9,899.99999000 |
| 1 / `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2:0` (DAO) | 1,000.00000000 |
| 1 / `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2:1` | 999.99999000 |
| 1 / `0x2a6b71946100aef488a9bb505b27bc819d34754a4f6611d4bf6edbec53b5f00f:0` | 100.00000000 |

These live sets are bound to their respective comparison points, not the later phone signing state. Richer source loss followed canonical anchoring and a 117-file compact evidence seal; only approved disposable runtime images were retired at that historical stage. Source databases were not consulted afterward. Presentation cleanup does not repeat that storage work.

## DAO position and independent diagnosis

The DAO belongs to account 1: `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2:0`, principal 100,000,000,000 shannons, state `DEPOSITED`, data `0x0000000000000000`. Type code hash is `0x82d76d1b75fe2fd9a27dfbaa65a039221a380d76c926f378d3f81cf3e7e13f2e`, hash type `type`, empty args. Deposit block **22,647,433**, hash `0x7cb42962be61200f1b21caec71cdf4be5387b706b647bf8bfaa869346ce8a2e5`, epoch `0x7080128003681` (13,953 + 296/1,800), timestamp 1,791,246,343,189 ms. Withdraw/unlock metadata remained null; ordinary spendable balance excludes the principal.

Fixed comparison header **22,647,478**, hash `0x92579b1939123c32c33dc77d1fedb3fbd2853d917061a0c08556ac0fca3fcdb7`, yields DAO rate **11,926,646,310,766,507** against deposit rate **11,926,643,449,081,918**. Correct occupancy is 10,200,000,000 shannons; Pocket reader supplies 6,100,000,000. The formula in [Pocket proof](pocket-proof.md) gives correct maximum **100,000,021,546** versus reader maximum **100,000,022,530**. The node RPC `calculate_dao_maximum_withdraw` returned `0x1748773c2a`, matching the correct calculation. Matching cache header is inferred, while captured native tip was 22,647,479. Before restart at inferred header 22,647,449, observed reward 8,010 versus correct 7,661 proves the discrepancy predates restart.

Protocol references: [CKB capacity rules](https://github.com/nervosnetwork/ckb/blob/52c2be1a104edbf0ee1b6e261ada7d0db10af740/util/gen-types/src/extension/capacity.rs), [capacity units](https://github.com/nervosnetwork/ckb/blob/52c2be1a104edbf0ee1b6e261ada7d0db10af740/util/occupied-capacity/core/src/units.rs), [DAO calculator](https://github.com/nervosnetwork/ckb/blob/52c2be1a104edbf0ee1b6e261ada7d0db10af740/util/dao/src/lib.rs#L290), and [RFC 0023](https://github.com/nervosnetwork/rfcs/blob/62a6e08e16a995ab94562581978ceac3726c31e6/rfcs/0023-dao-deposit-withdraw/0023-dao-deposit-withdraw.md). Four fixed-header RPC crosschecks matched canonical occupancy; offline calculation also reproduced the RFC example maximum of 200,155,259,131 shannons. Archived reference bytes and calculation/RPC/source-provenance records are bound by the diagnosis evidence manifest.

| Observation | Inferred estimate header | Pocket reward | Canonical reward |
| --- | ---: | ---: | ---: |
| Richer source | 22,652,548 | 2,560,902 | 2,449,084 |
| Richer baseline first / restart | 22,652,907 / 22,652,930 | 2,740,637 / 2,752,152 | 2,620,971 / 2,631,983 |
| Richer state-assisted first / restart | 22,653,011 / 22,653,038 | 2,792,705 / 2,806,222 | 2,670,766 / 2,683,693 |
| Phone baseline | 22,655,655 | 4,116,416 | 3,936,679 |
| Phone state-assisted | 22,655,899 | 4,238,572 | 4,053,501 |

Amounts are shannons. Distinct header-dependent rewards are not expected to equal each other. Known reader error was separately bounded/audited; canonical DAO position acceptance stayed exact. No mature withdrawal/unlock execution or correct reward/APC claim follows.

## Native cross-architecture audit

All **11,378** actual records were audited: prefix 0: 9; 32: 4; 96: 16; 160: 8; 192: 8; 208: 11,326; 224: 7. Transactions/indices use fixed u64/u32 big-endian fields and packed CKB structures. Metadata uses explicitly encoded u64 big-endian registrations, U256 little-endian chain work plus packed header, 100 recent u64 little-endian/hash pairs, u32 big-endian checkpoint index and u64 little-endian minimum filtered height. No persisted native pointer/usize/native-endian dump was found. Type-index families and matched-work records were absent in this payload; source defines their explicit encoding. Container format alone was not the compatibility argument.

## Source provenance and license

Original project contributions are distributed under the [MIT License](../LICENSE),
copyright 2026 Timothy, using the name supported by this repository's authorship
records. The retained files were checked against their introduction/change
history, source headers and pinned upstream references on 2026-10-08.

The package validator, sandbox transport, build wrapper and synthetic policy/Android
tests originated in `45c5088832c63d830fe8acb2d93c7f225a135f89`; the single-account
profile/test originated in `0305fbbf40b3c3f48b6a4e97f0b0e9b91a0698ce`. The standalone
Android helper originated in the first commit, evolved in the second, and its
DAO-aware variant was introduced in `fa42264`. These are original research
implementations referencing Pocket's schema, formats and defaults; no copied
Pocket or other upstream implementation was identified. The Android integration
test reads Pocket's separately obtained Room schema at runtime; generated data
stays under ignored local runs, and no upstream schema or tool binary is bundled.

The copied reference-data exception is `tools/bip39-english.txt`, extracted from
Pocket's pinned word list and byte-identical to the BIP39 English dictionary:
SHA-256 `2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda`.
Its attribution and applicable MIT notice are retained in
[third-party notices](../tools/THIRD_PARTY_NOTICES.md). Pocket's pinned
[license](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/LICENSE)
is MIT; no Pocket native implementation is redistributed here.

## Historical identifier mapping

| Historical ID | Human-readable meaning / authoritative record |
| --- | --- |
| H02 | Wallet-state recovery research; closure at `918efa774622497f673fa0e588d9d0e26c96d3a5` |
| B1 / R2 | Initial one-account emulator proof accepted at `0305fbbf40b3c3f48b6a4e97f0b0e9b91a0698ce`; older environmental failure is inconclusive |
| R1 (emulator) | Host-graphics environment qualification, `08eaab4...`; did not itself prove recovery |
| B2 / B2R4 | Final richer two-account/active-DAO emulator proof, accepted in closure reports |
| B2 R2/R3 | Earlier compensation-inclusive halt and independent DAO diagnosis; `fa42264ebb67cd681aed388c146fef89b060a6d8` is an intermediate gate, not the final recovery verdict |
| P3C / R1 / R1A (phone) | ARM artifact/cross-architecture qualification, launch/authentication/restart qualification, then final real-phone recovery proof |
| P-A / Control | Baseline recovery |
| P-B / Candidate | State-assisted recovery |
| H / H2 | Initial / richer saved-state checkpoint |
| F / F2 / FP | Initial / richer / phone canonical comparison checkpoint |
| D2 | Separate historical research layer, not used or necessary for the tested Pocket recovery path |

Two immutable legacy wire-format literals remain inside the validator/helper: `h02-p0-v1` (two accounts) and `h02-p0-b1-one-account-v1` (single account). They identify sealed bytes and are not public filenames, class names or CLI profile choices. The scanner also retains rejection of the historical synthetic canary `h02_test_secret`, alongside its renamed canary. Public helper class/package, actions, success/refusal messages, AVD guard, staging/journal paths and test names now use descriptive names. Those naming changes do not alter the saved evidence bytes or expand supported recovery profiles.

Recover any old record with `git show <revision>:<historical-path>`. The report map and complete closure digest index follow. Ignored paths are custody references, not broken links or promised clone contents.

D2 was unnecessary for this tested Pocket recovery path and was not used.

## Immutable package member bindings

| Member | Bytes | SHA-256 |
| --- | ---: | --- |
| `app.json` | 14528 | `83c3651595d9528e6dc6ea02e8eb744f2d0b7cc5dc408d4025f24c297e5b3890` |
| `native.sqlite` | 1888256 | `8a027384037de94cd7bad5903b563b8dc593452fe89be35814c17993dd747dc1` |

## Complete closure digest index

These are unchanged bindings from the closure record. Files remain local-only.

| Retained manifest | Members checked against stored digest/size |
| --- | ---: |
| `runs/wo3b2-r3/evidence-manifest.json` | 20 |
| `runs/wo3c-r1/evidence-manifest.json` | 30 |
| `runs/wo3c-r1a/evidence-manifest.json` | 16 |
| `runs/wo3c/phone-ab/control/evidence-manifest.json` | 55 |
| `runs/wo3c/phone-ab/candidate/evidence-manifest.json` | 40 |
| `runs/wo3c/phone-ab/final-evidence-manifest.json` | 10 |

| Evidence/index retained locally | Bytes | SHA-256 |
| --- | ---: | --- |
| `runs/wo3b1-r1/qualification-summary.json` | 4813 | `258689cac42b74f1c4cee07db09c108b0ab0540b685ff7124c03d05cf82147d0` |
| `runs/wo3b1-r1/preserved/failed-evidence-hashes.json` | 1251 | `6145fbb0aebada155c5e29c377c99eb647f887eb842a777fcecbf20c2532b3f5` |
| `runs/wo3b1-r2/comparison.json` | 3587 | `6802e39580a2957233ee6ae2d74d1091611523d08f1e5399844201e7a5543a31` |
| `runs/wo3b1-r2/final-audit.json` | 1820 | `058d0d81da7a45f5d2c608cbc91354334cac53bbd2ce4c87adde16d757646360` |
| `runs/wo3b1-r2/oracle-F.json` | 15735 | `f71ca50e86d153d115012403355a112550763bea2b6e45f37d798e50e9836bd2` |
| `runs/wo3b1-r2/package-H-immutable/manifest.json` | 1552 | `f89fc4feeb019b47b625be8df71f5ef9cd64acdf2104cd793f113e0c9530fd12` |
| `runs/wo3b2-r3/evidence-manifest.json` | 3670 | `1ab4b9c2bdf759a5a5c7b518c3ed0aab3d26f7f3b7462bbb84261cc86bcdfde7` |
| `runs/wo3b2-r4/result.json` | 1135 | `863da2d6d27b698c5bec1a2ffc9f44b453f0e9f834ed0d39bb1203a628be83bf` |
| `runs/wo3b2-r4/previous-b2-reports/hashes.json` | 646 | `6c7f6eccbb961015d32b06132918a0d3e9d8db505652a86e3832fbccf0766eb0` |
| `runs/wo3b2/control/result.json` | 592 | `0577068c4f75fc12aa1f82bd074e6c8c4be4f8cc4daba5aee98ef2424eeca5c0` |
| `runs/wo3b2/candidate/result.json` | 576 | `4fc747d62db63d9fd161476286117302ba2da86b75d29b1233048b42b9ed7163` |
| `runs/wo3b2/oracle-H2.json` | 22674 | `cb4b83db2a789178f9a3f8624b7f78c512b52d0eab535f93e949e858f9ebb643` |
| `runs/wo3b2/oracle-F2.json` | 28653 | `d079781ce17eee0b48e5e68b8163c534f4bb1b2a15782aafb5e3dd9343023aa3` |
| `runs/wo3b2/final-boundary.json` | 2331 | `3deac156a2353e28792a15f475dd2ba81e63a2e1fdc57284903d77db942ee521` |
| `runs/wo3b2/package-H2-immutable/manifest.json` | 1933 | `56d4a6506641c62797531eb0f093c4930131a9046d26351377c292568d7d879e` |
| `runs/wo3c-r1/phone-artifact.json` | 3709 | `d0f69fd873008f4ec528ddfe1427f4cfac43535f5b10177b4ff7de1bc77ea8ee` |
| `runs/wo3c-r1/cross-abi-audit.json` | 2913 | `b9adf7b0e47e86191808615d05d05b154311f00e1191bcb56c18b4d5cca26b05` |
| `runs/wo3c-r1a/qualification-result.json` | 1136 | `fb9e40f8353fb4c18aabe77cbf3e737ad40f4e7eefb7634332c22cc97b3876a1` |
| `runs/wo3c-r1a/evidence-manifest.json` | 2518 | `2f02235a33ab9390d5309d4db387635618f804688cdce71addd86b66a66131e0` |
| `runs/wo3c/phone-ab/control/result.json` | 943 | `b852e43a22467c956dd358e8166a2448c5fdb0bdd96475859c22a6b711ad37f2` |
| `runs/wo3c/phone-ab/control/evidence-manifest.json` | 8385 | `7e9d99585314217b366d6907f248f25093fd8cec6b8a32aaaac490cadc305b62` |
| `runs/wo3c/phone-ab/candidate/result.json` | 948 | `ad457d88133e43278dd1ddbbc95353952e0cc17d285ac5b2293689094c8fdec1` |
| `runs/wo3c/phone-ab/candidate/evidence-manifest.json` | 6188 | `62b96bf7dbd0c02be0128646276315ac38b4fb7e8484d3473b7cba0b7517b729` |
| `runs/wo3c/phone-ab/comparison.json` | 1490 | `a67115b59ab784f2e1807f1b2b9e32c849245d886922053ccd9864a6d33ff4e4` |
| `runs/wo3c/phone-ab/final-evidence-manifest.json` | 1388 | `1d6e08145dfc1ad248b380d2a726469322d17f0ee2df508db65eeef22ac8a6f8` |
| `runs/wo3c/phone-ab/oracle-FP.json` | 31592 | `fba15392eb1ad1fc9ee90924280d32b43ef2c395547ec7f677b538921426a2d0` |
| `runs/wo3c/phone-ab/oracle-final.json` | 34531 | `ec22cf379f402c14f4978fdf6b4af00e59ba50d090f7da26b4a752b387b26edd` |
| `runs/wo3c/phone-ab/retained-phone-runtime.json` | 201 | `40039b46fcb6fb6ed283ecfd0e237da5166d6788a86694eb82d557afda1beee1` |
| `runs/wo3c-r1/evidence-manifest.json` | 4216 | `9cab085c815d2f69b196cc6c18f934e3af26deaba48d524ab4fe7f4372fa4bad` |

## Pinned implementation source map

All links below use the exact Pocket commit. These preserve the original source-backed recovery map without its work-order narrative.

**Source and provenance**: [GitHub release](https://github.com/RaheemJnr/pocket-node/releases/tag/v1.8.5).

**Source and provenance**: [app configuration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/build.gradle.kts#L10), [wrapper](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/gradle/wrapper/gradle-wrapper.properties), [Rust manifest](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/Cargo.toml), [JNI build](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/build-android-jni.sh), [Room schema](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/schemas/com.rjnr.pocketnode.data.database.AppDatabase/17.json).

**Key recovery**: [import](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/ui/screens/onboarding/MnemonicImportScreen.kt#L133), [wallet creation/import](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/WalletRepository.kt#L191), [writer](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/WalletKeyWriter.kt#L99), [Keystore](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/crypto/KeystoreEncryptionManager.kt#L144), [PIN backup](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/crypto/KeyBackupManager.kt#L59), [key row](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/database/entity/KeyMaterialEntity.kt#L7), [legacy prefs](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/KeyManager.kt#L154).

**Light-client state**: [paths and lifecycle](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/NodeLifecycle.kt#L128), [SQLite and registrations](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/storage/db/sqlite.rs#L76), [key encoding](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/storage/mod.rs#L291), [native initialization](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/bridge_core/lifecycle.rs#L98), [stop semantics](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/bridge_core/lifecycle.rs#L444).

**Application state**: [Room declaration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/database/AppDatabase.kt#L29), [Room initialization](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/di/AppModule.kt#L139), [all entity definitions](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/database/entity), [preference keys](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/WalletPreferences.kt#L233), [registration flag](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L580), [height input](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/ui/components/SyncOptionsSheet.kt#L185).

**Exact current import flow**: [ordering and picker](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/ui/screens/onboarding/MnemonicImportScreen.kt#L179), [node startup](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L171), [active-wallet registration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L246), [single registration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L461), [resync](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L592), [multi registration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/SyncCoordinator.kt#L564), [progress/candidate reconciliation](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L1263).

**Multiple wallets, accounts and Scripts**: [candidate derivation](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/SubAccountDiscovery.kt#L50), [candidate policy](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/SyncCoordinator.kt#L146), [discovery gate](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/SubAccountReconciler.kt#L56), [sub-account restoration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/ui/screens/wallet/WalletManagerViewModel.kt#L92), [account creation](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/wallet/WalletRepository.kt#L333).

**DAO**: [DAO enumeration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/DaoDepositReader.kt#L72), [headers](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/DaoHeaderResolver.kt#L124), [merge and overlays](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L2594), [cached-cell fate](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/DaoCellRetirement.kt#L139), [v17 marker](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/database/entity/PendingDaoUnlockEntity.kt#L19).

**Consistency boundary**: [foreground service](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/sync/SyncForegroundService.kt#L32), [background scheduler](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/sync/SyncWorkScheduler.kt), [native stop](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/bridge_core/lifecycle.rs#L444), [WAL configuration](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/di/AppModule.kt#L139).

**Additional diagnosis/data references**: [DAO reader arguments (deposited/withdrawing)](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/DaoDepositReader.kt#L242), [Correct DAO occupied-capacity constant](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/shared/src/commonMain/kotlin/com/rjnr/pocketnode/data/gateway/models/DaoConstants.kt#L26), [Native DAO calculation](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/external/ckb-light-client/light-client-lib/src/bridge_core/dao.rs#L93), [Android phase-2 unlock recomputation](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/app/src/main/java/com/rjnr/pocketnode/data/gateway/GatewayRepository.kt#L3193), [Unlock transaction builder](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/shared/src/commonMain/kotlin/com/rjnr/pocketnode/data/transaction/TransactionBuilder.kt#L641), [Pocket BIP39 dictionary source](https://github.com/RaheemJnr/pocket-node/blob/b28979de744798ffb75367b031d4871ec3af1a12/android/shared/src/commonMain/kotlin/com/rjnr/pocketnode/core/crypto/Bip39EnglishWordlist.kt).

## Historical report map

Every historical path below is under `docs/` at closure commit `918efa774622497f673fa0e588d9d0e26c96d3a5`. Material recovery facts are consolidated before current-tree removal; superseded process inventories remain in history.

| Original report | Consolidated material / disposition |
| --- | --- |
| `H02_LOCAL_INVENTORY.md` | Local workspace inventory; process-only paths remain historical, custody unchanged. |
| `H02_REPO_CLOSURE.md` | Evidence: full digest/member index, custody, final verdict and preserved checkpoint. |
| `P1_CURRENT_POCKET_RECOVERY_MAP.md` | How it works: source/secret/state/account/lifecycle map; evidence: pinned citations above. |
| `P1_DELTA_FROM_D2_POCKET_PIN.md` | Evidence: final source/native pins and D2 exclusion; superseded comparison stays historical. |
| `P1_ENVIRONMENT_READINESS.md` | Evidence: accepted toolchain; preliminary inventories/build status superseded. |
| `P1_LOST_DEVICE_EXPERIMENT_CONTRACT.md` | How it works / proof: independent key recovery, source loss, exact canonical coverage, stale-state/restart criteria; broader DAO lifecycle remained untested. |
| `P2_BUILD_REPORT.md` | Evidence: exact build/artifact/toolchain provenance, reproduction limits; full host adapters remain historical. |
| `P2_EMULATOR_READINESS.md` | Proof/evidence: qualified host-GPU profile supersedes initial environment. |
| `P2_SANITIZED_STATE_PACKAGE_SPEC.md` | How it works: members, allowlists, exclusions, mapping, trust, schema/network/coverage and activation gates. |
| `P2_SECURITY_CHECK.md` | How it works: bounded scanner, key boundary, synthetic tests; evidence: dictionary hash and historical audit scope. |
| `P2_TOOLING_DESIGN.md` | How it works: logical snapshot, guarded transfer, changed-baseline refusal, staging/journal/rollback and existing commands. |
| `P3B1_CANDIDATE_RESULT.md` | Proof: initial one-account outcome, stale spend/catch-up/restart, exact capacity/timing; evidence: checkpoints, digest and archive. |
| `P3B1_COMPARISON.md` | Proof: initial one-account outcome, stale spend/catch-up/restart, exact capacity/timing; evidence: checkpoints, digest and archive. |
| `P3B1_CONTROL_RESULT.md` | Proof: initial one-account outcome, stale spend/catch-up/restart, exact capacity/timing; evidence: checkpoints, digest and archive. |
| `P3B1_DECISION.md` | Proof: initial one-account outcome, stale spend/catch-up/restart, exact capacity/timing; evidence: checkpoints, digest and archive. |
| `P3B1_R1_EMULATOR_DIAGNOSIS.md` | Proof: prior environmental inconclusive outcome, unresolved cause; evidence: qualification/archive bindings. |
| `P3B1_R1_STABLE_PROFILE.md` | Proof/evidence: accepted API-36 host-GPU profile and bounded two-boot qualification. |
| `P3B1_SOURCE_RESULT.md` | Proof: initial one-account outcome, stale spend/catch-up/restart, exact capacity/timing; evidence: checkpoints, digest and archive. |
| `P3B2_CANDIDATE_RESULT.md` | Proof: accepted richer two-account/active-DAO result and limitations; evidence: identities, events, exact live set, source-loss boundary and digest bindings. |
| `P3B2_COMPARISON.md` | Proof: accepted richer two-account/active-DAO result and limitations; evidence: identities, events, exact live set, source-loss boundary and digest bindings. |
| `P3B2_CONTROL_RESULT.md` | Proof: accepted richer two-account/active-DAO result and limitations; evidence: identities, events, exact live set, source-loss boundary and digest bindings. |
| `P3B2_DECISION.md` | Proof: accepted richer two-account/active-DAO result and limitations; evidence: identities, events, exact live set, source-loss boundary and digest bindings. |
| `P3B2_FIXTURE.md` | Proof: accepted richer two-account/active-DAO result and limitations; evidence: identities, events, exact live set, source-loss boundary and digest bindings. |
| `P3B2_R1_LOW_SPACE_EXECUTION_PLAN.md` | Historical sequential-host storage accommodation; no recovery prerequisite or new device cleanup. |
| `P3B2_R1_STORAGE_AUDIT.md` | Historical host reclamation/accounting; authoritative evidence preserved and current custody untouched. |
| `P3B2_R3_DAO_SOURCE_DIAGNOSIS.md` | Proof/evidence: exact occupancy/rates/formula, fixed-header RPC crosschecks, pinned reader/unlock trace, narrowed canonical position contract. |
| `P3B2_R3_POCKET_DAO_BUG_DRAFT.md` | Proof/evidence: cause, impact, fixed-header reproduction and proposed unimplemented fix; unsent draft recoverable. |
| `P3B2_SOURCE_RESULT.md` | Proof: accepted richer two-account/active-DAO result and limitations; evidence: identities, events, exact live set, source-loss boundary and digest bindings. |
| `P3C_DECISION.md` | Proof/evidence: independent fresh V2 destinations, canonical comparison, real signing, prompt-capture caveat, restart, timing and final custody. |
| `P3C_PHONE_CANDIDATE.md` | Proof/evidence: independent fresh V2 destinations, canonical comparison, real signing, prompt-capture caveat, restart, timing and final custody. |
| `P3C_PHONE_COMPARISON.md` | Proof/evidence: independent fresh V2 destinations, canonical comparison, real signing, prompt-capture caveat, restart, timing and final custody. |
| `P3C_PHONE_CONTROL.md` | Proof/evidence: independent fresh V2 destinations, canonical comparison, real signing, prompt-capture caveat, restart, timing and final custody. |
| `P3C_R1A_PHONE_LAUNCH.md` | Proof/evidence: ARM artifact/signer, unchanged source-package provenance, fixed encodings, separate destination policy, startup/auth/restart qualification and 16 KB caveat. |
| `P3C_R1_ARM_ARTIFACT.md` | Proof/evidence: ARM artifact/signer, unchanged source-package provenance, fixed encodings, separate destination policy, startup/auth/restart qualification and 16 KB caveat. |
| `P3C_R1_CROSS_ABI_COMPATIBILITY.md` | Proof/evidence: ARM artifact/signer, unchanged source-package provenance, fixed encodings, separate destination policy, startup/auth/restart qualification and 16 KB caveat. |
| `P3C_R1_DECISION.md` | Proof/evidence: ARM artifact/signer, unchanged source-package provenance, fixed encodings, separate destination policy, startup/auth/restart qualification and 16 KB caveat. |
| `P3C_R1_PHONE_TRANSPORT.md` | Proof/evidence: ARM artifact/signer, unchanged source-package provenance, fixed encodings, separate destination policy, startup/auth/restart qualification and 16 KB caveat. |
| `P3_EXECUTION_PLAN.md` | Proof: source-loss/control method, separate stale events and scoped actual DAO coverage; old execution instructions remain historical. |
| `P3_SETUP_FIXTURE_REPORT.md` | Evidence: fixture came from separately protected recovery material, not imported phone/native state; custody/identity context below. |

Original tooling is likewise recoverable at that revision under `scripts/`. Retained public tooling comes from the validator, emulator transport, newer `b2r2-helper/H02State.java`, sole build wrapper, dictionary and three corresponding tests. Removed drivers include credential/UI entry, fixed-phone qualification/recovery/signing/oracle/comparison, transaction generation, role orchestration, duplicate variants, storage cleanup and host-specific Pocket build adapters. Public tools have no import dependency on them.

## Offline verification

The retained tooling passed all **33 package-policy and six single-account offline tests** with generated data on Python 3.13. The standalone Android helper compiled and dexed on the host; Android integration, wallet experiments, phone tests and transactions were not run. Source/import parsing, local links and pinned Pocket source paths/line anchors passed review. No retained tool imports a removed driver.

The final staged tree received an exact local-private-value scan covering recovery words, derived seed/account keys and known protected credentials in binary/text, hexadecimal, Base64 and UTF-16 forms, plus generic private-key/mnemonic-pattern review. No actual secret match or raw/private tracked artifact was found. The public dictionary and generated rejection canaries are reference/test data. The scanner is a local hygiene check, not a new security certification.

All 29 closure index bindings, all six evidence manifests' members (including historical report/source reconstruction), immutable package/member bindings and upstream notices were verified. The closure commit and original ancestry remain intact. Original reports are recoverable through Git; ignored raw custody and the retained phone installation were not cleaned. The root MIT license covers original project contributions; the copied dictionary retains its upstream notice.
