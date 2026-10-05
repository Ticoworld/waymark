# WO-3B1-R2 SOURCE result

SOURCE correctness before backup: **PASS**. Normal automatic phrase recovery, exact historical reconstruction, settled discovery, and restart succeeded before H. No production Pocket changes, physical phone access, D2, extra account or DAO.

## Fixed environment and identity

Pocket v1.8.5/code 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`; APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. LC 0.5.4/tree `3ac3e0ce1f4e46897d188b76c5b841b9097fa506`. API36/x86_64/default image rev2, 2048 MiB, two vCPUs, WHPX, host GPU/Intel Iris Xe, headless/no snapshots. SOURCE registry `runs/wo2/avd`, AVD `H02_P0_API36_X64`, explicit serial `emulator-5580`. Source userdata is sealed; do not reopen it.

One actual wallet/account: `m/44'/309'/0'/0/0`, source UUID `7ae5c050-48ed-4cd6-9056-d8e27e40468e`. TESTNET address `ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdutzpvgvy5x8hz8ttmht2ttsej25u7a0g7rmyth`. Lock: code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`, args `0xbc5882c4309431ee23ad7bbad4b5c3325539eebd`. Script hash `0x4cff5ae9aa82be7814fc9c058a09098bed951a71aa1b8971518446d0a724568d`. Public identity matches the private fixture; no secret appears here.

Normal flow: recover phrase, explicit no-device-lock consent, create/confirm app PIN, background sync only while open, switch default MAINNET to TESTNET through Settings/restart/PIN, then CUSTOM block floor **22,369,937**, one block before first activity. Default RECENT uses 200,000 blocks and omitted this fixture's September activity; genesis was unnecessary.

## Exact state before H

Independent complete public indexer/RPC observations agreed with native live indexes, transaction history, Room history/balance, account mapping and progress. Capacity: **1,999,999,999,000 shannons = 19,999.99999 CKB**.

| Live outpoint | Capacity (shannons) |
|---|---:|
| `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66:0` | 1,000,000,000,000 |
| `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894:0` | 100,000,000,000 |
| `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894:1` | 899,999,999,000 |

Three historical transaction hashes are the two above plus `0xb7503283af42a8fd1595306e2d5dd4a789e103980207fdafb5229b2e20b7113c`. First relevant block 22,369,938; last original activity 22,370,275. All live Cells use the primary Script, no type Script, empty data. No DAO or pending app actions.

Normal mnemonic import creates **51 public discovery candidates** even for one account. Initially 47 native Scripts were registered (primary plus 46 probes). After those 46 became EMPTY, restart registered the remaining five and replayed filters from the earliest cached transaction minus 1,000 (22,368,938). Primary saved progress did not regress; new-block processing and spending waited behind discovery. This was observed **before any H02 restoration**. After the second pass all 51 were EMPTY. A further restart registered from 22,646,277 and caught up normally, without another historical replay. No second wallet/account was created.

The first exact accepted state/restart pair through 22,646,032 had semantic SHA-256 `05cfc89850604901d80f23a4b06e246359116a8a8456169e6dae80418fbbee04`. Final pre-H observation: verified tip 22,646,287, primary/native/global/Room saved progress 22,646,283, zero matched work. The latest registration start was 22,646,277; this field is a resume cursor, not the coverage floor. CUSTOM coverage remains 22,369,937.

Source references: `WalletRepository.importFromMnemonic`, `SyncCoordinator.candidateScanStart/selectCandidatesForRegistration/setScriptsAndRecordLocked`, `GatewayRepository.getAccountStatus`, and `SubAccountReconciler` in the unchanged Pocket checkout. Source preparation included automation repair and discovery diagnosis; it is **not** Control A timing.

## H package

H **22,646,283**, hash `0x764023cd6da7a464f6c9b98fdffb2fd022c3384991f7f11a7cbf48142ecd30cc`. Source verified tip hash `0x220ff28b737c5bdf36a26edd14291439d787d2e270fdd7aa65baa94984af478a` at 22,646,287 was also checked against the public canonical header. Pocket was force-stopped, disabled and verified absent before the logical snapshot.

Package profile `h02-p0-b1-one-account-v1`, distinct from the earlier two-account profile. Immutable copy: `runs/wo3b1-r2/package-H-immutable/`. Total **1,895,341 bytes**; export **3.412449 seconds**. This export interval includes approved extraction and sealing, not the earlier acceptance observation. Manifest SHA-256 **`f89fc4feeb019b47b625be8df71f5ef9cd64acdf2104cd793f113e0c9530fd12`**, retained independently.

| Member | Bytes | Purpose |
|---|---:|---|
| native.sqlite | 1,880,064 | Logical approved native chain, Script, history/live-cell and progress state |
| app.json | 13,725 | Public wallet/account identities, candidate states, coverage preferences and progress |
| manifest.json | 1,552 | Exact versions, network/genesis, H, schemas, identities and hashes |

Security/schema/network/hash gates: **PASS**. No raw source Room DB, keys, phrase, PIN hash/salt, key backup, Keystore, peer identity or arbitrary preferences. Transaction/balance/header/DAO app caches are omitted and must be rebuilt normally. All 51 discovery rows are EMPTY. Native state in the package matches the frozen acceptance observation. Hashes provide integrity against a separately trusted digest; they do not prove historical completeness or remove trust in the source's pre-H work.

## Deliberate post-H stale event and loss

Through Pocket's normal Send UI, sent **100 CKB to the same primary TESTNET address**, with 1,000-shannon fee. Exactly one input U was consumed: `0xcfdba9a3ee86405a258a363ddf30ac28d33b0d84c500dd394f6eecc24d7e6894:0`, previously live in H.

Transaction **`0x69c04b470dbc5470ff554b2901fcc047edda082b46d8af523ae84a99e03d62b7`**, committed at **22,646,305**, block hash `0x45616351d7448a21ba0dad75383119f293f089d8bd5d95320293a7cd49082226`. Its outputs :0 (10,000,000,000 shannons) and :1 (89,999,999,000) both belong to the same Script. No DAO/second account/other transaction.

F **22,646,322**, hash `0xcf2e87ef4e69972230c850c681a3c411cd5228cb966985b381bcf0bba0e2ebd9`, 17 blocks after inclusion. Independent public observations show four transactions, four live Cells and **1,999,999,998,000 shannons = 19,999.99998 CKB**. `get_live_cell(U,false)` returns `unknown` (not `live`); the canonical committed transaction explicitly spends U. Do not misquote this response as literal `dead`.

SOURCE was stopped; AVD files were hashed and made read-only before the loss declaration at **2026-10-05 21:46:19.245638 UTC**. `source/LOST.json` records the seal. No source emulator, native/Room DB or userdata may be consulted after that declaration. Later arms use the private recovery fixture, sanitized package, already recorded public oracle and public chain only. Source's public report/receipt is retained evidence, not a live state source.

## Evidence and limits

Public evidence under `runs/wo3b1-r2`: `oracle-preH-settled.json`, `oracle-F.json`, `source/acceptance-discovery-settled.json`, `source/final-restart-watch.jsonl`, `source/final-restart-protocol.json`, `source/package-receipt.json`, and `source/LOST.json`. Frozen observations and original run evidence are retained but SOURCE databases are sealed against further experiment consultation. Earlier failed B1 report is preserved with hashes under `previous-b1-reports/`; R1 diagnosis is unchanged.

Test-only automation repairs: API36 runner classpath, bounded Compose text readback, safe click actions and public selectors. All recovery keys used the supported UI. One-account package policy and synthetic checks preserve the known secret exclusions. Source success establishes a valid input to the experiment; A/B equivalence remains separately measured. This is a **LIMITED PERFORMANCE FIXTURE**.
