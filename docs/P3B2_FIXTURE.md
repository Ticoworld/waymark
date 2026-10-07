# WO-3B2-R4 fixture

**Two genuinely populated derived accounts and one confirmed active DAO deposit.** Continued from the preserved R2/R3 SOURCE; no account or DAO fixture was recreated.

Pocket v1.8.5/code 27, commit `b28979de744798ffb75367b031d4871ec3af1a12`; approved APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. TESTNET. API 36 / x86_64 / 2048 MiB / 2 vCPUs / WHPX / Intel Iris Xe HOST GPU / headless / no snapshots. Explicit emulator serial `emulator-5580`. Physical Samsung untouched; D2 excluded; production Pocket source unchanged.

Both locks use code hash `0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8`, hash type `type`.

| Account | Derivation path | Lock args | Parent | Historical coverage |
|---|---|---|---|---:|
| 0 | `m/44'/309'/0'/0/0` | `0xbc5882c4309431ee23ad7bbad4b5c3325539eebd` | None | 22369937 |
| 1 | `m/44'/309'/1'/0/0` | `0x2da024570462b0e2421d87abcbfebd4567d52ad5` | 0 | 22647000 |

Account 1 was funded through the independently controlled disposable TESTNET relay; its history is distinct from account 0. DAO owner: account 1; outpoint `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2:0`; principal 1000.00000000 CKB; stage DEPOSITED; data `0x0000000000000000`; type code hash `0x82d76d1b75fe2fd9a27dfbaa65a039221a380d76c926f378d3f81cf3e7e13f2e`, hash type `type`, empty args. Deposit block 22647433, hash `0x7cb42962be61200f1b21caec71cdf4be5387b706b647bf8bfaa869346ce8a2e5`, epoch `0x7080128003681`. No later DAO transition was attempted.

H2 = 22652549, hash `0x3f96acadbf4ef0d847db36468ca13feb37630fd5a156a5540713897c0dd4e3ee`. F2 = 22652587, hash `0x906b72dc199e58ece8ad3962685dba415642272085ae629ffc8c5ad18ac6c8c3`. Both post-H2 events confirmed at 22652580, hash `0x413f758d5930756b01db459c3cdfa60e6a486414b4d296c2d52de521135e543a`. Activity was frozen afterward.

Account-0 transaction `0xce0b13ba3f23babc6e4cc011a992b1f7bf610dd92b4f6719afde1c91a5e2ab39` consumes H2-live U `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66:0` and creates two ordinary owned Cells. The public node reports U as `unknown`, with null Cell; its confirmed canonical spend and absence from the final live index jointly prove consumption. Account-1 transaction `0x2a6b71946100aef488a9bb505b27bc819d34754a4f6611d4bf6edbec53b5f00f` delivers 100 CKB from the existing relay.

Final canonical live set:

| Account | Outpoint | Capacity (CKB) | Kind |
|---|---|---:|---|
| 0 | `0xb23fbbb1db9ca0da48f76993e9258fdadb0f3bc81d9999924561e72583aa5d5a:1` | 7499.99997000 | ordinary |
| 0 | `0xce0b13ba3f23babc6e4cc011a992b1f7bf610dd92b4f6719afde1c91a5e2ab39:0` | 100.00000000 | ordinary |
| 0 | `0xce0b13ba3f23babc6e4cc011a992b1f7bf610dd92b4f6719afde1c91a5e2ab39:1` | 9899.99999000 | ordinary |
| 1 | `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2:0` | 1000.00000000 | DAO deposit |
| 1 | `0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2:1` | 999.99999000 | ordinary |
| 1 | `0x2a6b71946100aef488a9bb505b27bc819d34754a4f6611d4bf6edbec53b5f00f:0` | 100.00000000 | ordinary |

Full transaction bodies, lock/type/data, headers, live-status queries and histories are retained in `runs/wo3b2/oracle-H2.json`, `oracle-F2.json`, `final-boundary.json` and `chain-events/post-H2-account*/`. F2 histories contain six account-0 and three account-1 transactions, with no cross-account transaction overlap.

The known reader defect uses 61 CKB instead of canonical 102 CKB occupied capacity. This trial accepts canonical DAO position continuity; compensation is independently audited and reported separately. See [R3 diagnosis](P3B2_R3_DAO_SOURCE_DIAGNOSIS.md). Later withdrawal, unlock and mature DAO lifecycle execution remain NOT TESTED.
