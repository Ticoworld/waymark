# WO-3C-R1 exact-H2 cross-ABI qualification

The exact H2 payload is architecture-independent under the same pinned Pocket/light-client source. Native state can transfer byte-for-byte from x86_64 to ARM64. This is payload/source qualification; phone activation, recovery, authentication and signing remain untested.

## Immutable inputs

- Pocket commit: `b28979de744798ffb75367b031d4871ec3af1a12`.
- Native source tree: `3ac3e0ce1f4e46897d188b76c5b841b9097fa506`.
- Package: `runs/wo3b2/package-H2-immutable`; H2 22,652,549; hash `0x3f96acadbf4ef0d847db36468ca13feb37630fd5a156a5540713897c0dd4e3ee`.
- Manifest SHA-256: `56d4a6506641c62797531eb0f093c4930131a9046d26351377c292568d7d879e`.
- Source APK SHA-256: `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`.
- TESTNET genesis: `10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606`.

Original validation and secret exclusion pass unchanged. `scripts/p3c_r1_audit.py` records exact member checks, pinned source hashes, storage families and encodings in `runs/wo3c-r1/cross-abi-audit.json`.

## Every payload

| Payload | Classification | Evidence / destination handling |
| --- | --- | --- |
| manifest.json | Architecture-independent | JSON provenance, hashes, schema, identities, boundaries and Scripts; original source ABI/APK fields remain unchanged |
| app.json | Architecture-independent | Allowlisted JSON wallet/account relationships, progress, candidates and sync preferences; Room 17 and identity `091b40f9618fee3fc8032ff01255a9a4` match pinned schema |
| native.sqlite | Architecture-independent | Logical SQLite KV snapshot; every actual family uses fixed-width explicit byte order or packed CKB structures |

No raw Room database, executable, RocksDB/SST/MANIFEST, memory dump, Keystore, PIN, key-material payload or peer identity is included. Unknown members are rejected. Application import retains normal Script/derivation-based remapping from source UUIDs to recovered destination UUIDs; this is identity reconciliation, not ABI conversion or package mutation. Native bytes require no transformation.

## Native serialization

Pinned `external/ckb-light-client/light-client-lib/src/storage/db/mod.rs` selects `sqlite` for all non-wasm targets; `native`/RocksDB is commented out. `light-client-lib/Cargo.toml` uses bundled rusqlite; its RocksDB dependency is commented out. ARM and x86 use the same `jni-bridge,portable` features.

`src/storage/mod.rs` defines transaction/output/checkpoint indices as u32 and block numbers as u64. `Key::into_vec`, `Value` conversion and `append_key` write explicit BE indices and packed CKB Script/Transaction/Header/hash bytes. `db/sqlite.rs` has corresponding decoders and explicit BE/LE metadata writers. In-memory usize lookup indices are not serialized as native structures. These persisted paths contain no pointer, native-endian integer or bincode dump.

All **11,378 actual KV records** were audited:

| Prefix / count | Stored format |
| --- | --- |
| 0 / 9 | Hash key; u64 BE block + u32 BE index + packed Transaction |
| 32 / 4 | Raw lock Script + u64/u32/u32 BE Cell index; 32-byte hash value |
| 96 / 16 | Raw Script + fixed BE history indices + u8 input/output tag; hash value |
| 160 / 8 | Hash key; packed Header plus optional packed extension |
| 192 / 8 | u64 BE number key; 32-byte hash value |
| 208 / 11,326 | u32 BE checkpoint key; 32-byte filter hash value |
| 224 / 7 | Metadata below |

Metadata: two FILTER_SCRIPTS records (packed Script/u8 tag, u64 BE progress); GENESIS_BLOCK (hash vector); LAST_STATE (U256 LE, 32 bytes, plus packed Header, 208 bytes); LAST_N_HEADERS (100 records of u64 LE plus hash); MAX_CHECK_POINT_INDEX (u32 BE); MIN_FILTERED_NUMBER (u64 LE). MATCHED_BLOCKS is absent; pinned source defines a u64 BE key and u64 LE count plus hash/u8 records. Type-index families 64/128 are absent and share the fixed-width source serializer.

SQLite integrity/schema/free/trailing-page checks, key-family gates, genesis, registration progress and existing security gates pass. Compatibility is established from actual value encodings and the pinned backend as well as the container format.

## Required contract

Validate immutable source provenance with the original source APK hash. Independently bind the destination APK to its qualified hash/signer, same commit/native tree, Room schema/identity, native SQLite KV schema, TESTNET/genesis and ARM64 JNI. Re-run this audit before later activation. Refuse unknown payloads, schema/source drift or incompatible destination identities.

No architecture-dependent or unknown payload blocker was found. Cross-version/alternate-backend/arbitrary-package portability is outside scope. Real-phone filesystem activation and destination-key preservation remain WO-3C acceptance gates.
