# WO-3B2-R2 fixture

Two real accounts and a real DAO deposit were established. **B2-INCONCLUSIVE at SOURCE correctness, before H2:** Pocket's DAO compensation cache uses an incorrect occupied-capacity argument. The deposit itself, native Cells, account ownership, spendable balances and history match the independent oracle. No A/B arm ran.

Pocket v1.8.5 / code 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`; APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. TESTNET only. API 36 x86_64, 2048 MiB, two vCPUs, WHPX, Intel Iris Xe host GPU, headless, no snapshots. Explicit ADB serial `emulator-5580`. No SwiftShader, production source changes, physical Samsung access or D2. B1 evidence remains unchanged.

## Normal recovery and identity

The existing private fixture was consumed automatically through normal phrase import; no key/account rows were injected. Account 1 was created through Manage Wallets ? parent Settings ? Add account, with name `B2 Account 1`. Public identities and both local signing keys matched. The private fixture remains ignored and unchanged; a separate disposable relay key is stored only under `private/wo3b2/`.

Both locks use code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`.

| Account | Derivation | Lock args | SOURCE UUID | Coverage |
|---|---|---|---|---|
| 0 | `m/44'/309'/0'/0/0` | `0xbc5882c4309431ee23ad7bbad4b5c3325539eebd` | `043746a4-de6d-4911-8e00-5d663bdb0e37` | CUSTOM 22,369,937 |
| 1 | `m/44'/309'/1'/0/0` | `0x2da024570462b0e2421d87abcbfebd4567d52ad5` | `36ac4ecb-c83e-4a00-96db-09f2d6be58a7` | CUSTOM 22,647,000 |

Account 0 is the parent; account 1's `parentWalletId` is account 0's UUID. Script hashes are `0x4cff5ae9aa82be7814fc9c058a09098bed951a71aa1b8971518446d0a724568d` and `0x29958c7362d950f80cdb5994d47e408b38a4d2cc5e41f7a0087214ff3f421a24`. Full network addresses are retained in the allowlisted `source/preH2-restart/app.json` and `summary.json`. No MAINNET activity was created or assumed.

Initial fresh public oracle: account 0 had four transactions/four live Cells, 1,999,999,998,000 shannons; account 1 was empty. This includes B1's self-transfer and supersedes the older three-transaction setup count. Source reconstruction matched before new activity.

## Genuine TESTNET events

| Event | Transaction | Height | Relevant output |
|---|---|---:|---|
| Account 0 funds independent relay, through normal Pocket Send | `0xb23fbbb1db9ca0da48f76993e9258fdadb0f3bc81d9999924561e72583aa5d5a` | 22,647,401 | :0 = 2,500 CKB relay; :1 = account-0 change |
| Relay funds account 1 | `0xa6239ee565e9164ec0742c861c647f9b4c1505cd6dbe3b47dd24e6d89306c515` | 22,647,405 | :0 = 2,000 CKB account 1 |
| Account 1 deposits through normal Pocket DAO UI | `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2` | 22,647,433 | :0 = 1,000 CKB DAO; :1 = 999.99999 CKB change |

Each transaction paid 1,000 shannons. Signed relay material and canonical transactions/headers/input liveness are retained in `runs/wo3b2/chain-events/`. The relay has an independent random key, not another recovered mnemonic account. Its address/Script is in `relay-public.json`. Distinct transaction hashes populate the two owned accounts; their acceptance does not rely on one shared Room transaction row.

DAO deposit header: `0x7cb42962be61200f1b21caec71cdf4be5387b706b647bf8bfaa869346ce8a2e5`; epoch `0x7080128003681` (number 13,953, index 296, length 1,800). Output data is eight zero bytes. DAO type is code hash `0x82d76d1b75fe2fd9a27dfbaa65a039221a380d76c926f378d3f81cf3e7e13f2e`, hash type `type`, empty args. Canonical occupied capacity is 102 CKB: capacity 8 bytes + lock 53 + type 33 + data 8. Tested lifecycle: **confirmed DEPOSITED position only**. The UI offered Withdraw, but no withdrawal was attempted because the SOURCE gate failed before H2. No maturity wait or synthetic DAO rows.

## Retained live state at halt

| Account | Live outpoint | Capacity, shannons | Type |
|---|---|---:|---|
| 0 | `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66:0` | 1,000,000,000,000 | Plain |
| 0 | `0xb23fbbb1db9ca0da48f76993e9258fdadb0f3bc81d9999924561e72583aa5d5a:1` | 749,999,997,000 | Plain |
| 1 | `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2:0` | 100,000,000,000 | DAO deposit |
| 1 | `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2:1` | 99,999,999,000 | Plain |

Account 0: five transactions, 17,499.99997 CKB spendable. Account 1: two transactions, 999.99999 CKB spendable plus 1,000 CKB DAO principal. DAO compensation is not counted as spendable balance. `oracle-halt.json` at tip 22,647,505 independently rechecked unchanged Cells/history after the deposit; this is **not F2**. No H2, post-H2 events, new package or source-loss declaration exists.
