# WO-3B2 fixture ? not established

**B2-INCONCLUSIVE before recovery: host disk space prevented SOURCE boot.** No two-account/DAO acceptance fixture was established. This is not a wallet-state failure.

Pocket v1.8.5, commit `b28979de744798ffb75367b031d4871ec3af1a12`; TESTNET intended. Approved APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. No production source changes, D2, Samsung access, mnemonic entry or B2 transactions. B1 remains PASS and its evidence is preserved.

## Retained public fixture, not new B2 measurements

The retained B1 F oracle (`runs/wo3b1-r2/oracle-F.json`, boundary 22,646,322) records account 0 with four transactions, four live Cells and 1,999,999,998,000 shannons. Those are historical B1 observations, not a fresh B2 chain query. The earlier three-transaction setup fixture was extended by B1's authorized self-transfer.

| Account | Derivation | Expected lock args | B2 status |
|---|---|---|---|
| 0 | `m/44'/309'/0'/0/0` | `0xbc5882c4309431ee23ad7bbad4b5c3325539eebd` | Existing funded fixture; not recovered in B2 |
| 1 | `m/44'/309'/1'/0/0` | `0x2da024570462b0e2421d87abcbfebd4567d52ad5` | Previously derived public identity only; not created/funded |

Both use secp256k1 lock code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`. The private fixture stays at `private/pocket-disposable-fixture.json`, ignored by git. It was not consumed by this B2 attempt.

No relay key, account-1 funding, DAO deposit, DAO transition, H2, F2 or B2 package exists. DAO lifecycle coverage: **NOT TESTED**. No new funds are needed on the evidence available; existing disposable TESTNET funds were not spent in B2.

## Required continuation

After resolving storage, recover account 0 through normal UI with historical floor 22,369,937. Create account 1 through the supported sub-account flow and verify exact derivation/parent/Script associations. Set correct coverage through UI; new sub-accounts default to fresh-wallet sync mode, which must not be confused with recovered historical coverage.

Establish distinct account-1 history through the independently controlled path, then a real DAO deposit. Record canonical headers/outpoints and explicit public DAO rows before selecting H2. Only test a later real DAO stage if protocol timing permits. No Room injection or synthetic DAO rows.
