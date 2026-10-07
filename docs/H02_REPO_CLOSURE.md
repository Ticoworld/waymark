# H02 repository closure inventory

Closure review: 2026-10-07. Repository hygiene only; no experiment, device operation, Pocket source edit, build, transaction, cleanup or D2 use.

## Git boundary

- Branch: `main`
- HEAD before closure: `fa42264ebb67cd681aed388c146fef89b060a6d8`
- Initial tree: 6 modified tracked reports, 52 untracked files; nothing staged.
- Final PHONE-PASS reports were not committed at review start; they are included in the authorized closure commit.
- Historical B1 reports are already tracked. B2 reports now record the accepted R4 PASS; prior R2 conclusions remain in their original Git history and ignored byte-for-byte report archives.

## Exhaustive pending-file classification

Every path below is safe report or experiment-tooling source to preserve in Git. None is a private fixture, raw backup, compiled artifact or production Pocket source. These tools are retained as historical experiment tooling, not a production feature or an instruction to run more experiments.

| Path | Initial status | Disposition |
| --- | --- | --- |
| `docs/P3B2_CANDIDATE_RESULT.md` | Tracked modification | Preserve: H02 report |
| `docs/P3B2_COMPARISON.md` | Tracked modification | Preserve: H02 report |
| `docs/P3B2_CONTROL_RESULT.md` | Tracked modification | Preserve: H02 report |
| `docs/P3B2_DECISION.md` | Tracked modification | Preserve: H02 report |
| `docs/P3B2_FIXTURE.md` | Tracked modification | Preserve: H02 report |
| `docs/P3B2_SOURCE_RESULT.md` | Tracked modification | Preserve: H02 report |
| `docs/P3B2_R3_DAO_SOURCE_DIAGNOSIS.md` | Untracked | Preserve: H02 report |
| `docs/P3B2_R3_POCKET_DAO_BUG_DRAFT.md` | Untracked | Preserve: H02 report |
| `docs/P3C_DECISION.md` | Untracked | Preserve: H02 report |
| `docs/P3C_PHONE_CANDIDATE.md` | Untracked | Preserve: H02 report |
| `docs/P3C_PHONE_COMPARISON.md` | Untracked | Preserve: H02 report |
| `docs/P3C_PHONE_CONTROL.md` | Untracked | Preserve: H02 report |
| `docs/P3C_R1A_PHONE_LAUNCH.md` | Untracked | Preserve: H02 report |
| `docs/P3C_R1_ARM_ARTIFACT.md` | Untracked | Preserve: H02 report |
| `docs/P3C_R1_CROSS_ABI_COMPATIBILITY.md` | Untracked | Preserve: H02 report |
| `docs/P3C_R1_DECISION.md` | Untracked | Preserve: H02 report |
| `docs/P3C_R1_PHONE_TRANSPORT.md` | Untracked | Preserve: H02 report |
| `scripts/b2r3_dao_diagnosis.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_acceptance.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_account.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_export.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_finish_arm.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_gate_regression.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_post_h.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_pre_pocket.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_reports.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_restore.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_resume.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_retire_runtime.ps1` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_seal_arm.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_seal_source.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/b2r4_secret_gate.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c-r1-build.init.gradle` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_acceptance.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_activate.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_compare.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_destination.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_finish.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_oracle.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_preflight.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_recovery.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_signing.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_state.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_ui.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_phone_watch.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_preflight.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_r1_audit.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_r1_build_arm.ps1` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_r1_overwrite.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_r1_policy_checks.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_r1_probe.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_r1_qualify_artifact.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_r1_ui_state.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_r1a_observe.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/p3c_r1a_public_ui.py` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/phone-helper/H02PhoneABReadOnly.java` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/phone-helper/H02PhoneReadOnly.java` | Untracked | Preserve: H02 experiment tooling source |
| `scripts/phone-helper/H02PhoneSecurity.java` | Untracked | Preserve: H02 experiment tooling source |

`docs/H02_REPO_CLOSURE.md` is the additional public inventory/digest index created by this closure review. The historical `docs/H02_LOCAL_INVENTORY.md` is unchanged.

## Private, raw and generated exclusions

- `private/`: disposable recovery fixture, automation credential input, emulator security input, private captures and raw secret backups remain ignored. No private value or private-file digest is published here.
- `runs/`: raw evidence, runtime databases, SQLite/WAL/SHM, AVD/userdata, native captures, APKs/JARs/compiled helpers, build output, environment/toolchain files, logs and local closure audit remain ignored.
- `repos/`: pinned Pocket/native checkouts, checked-in upstream debug keystore and generated native libraries remain outside H02 Git.
- Build intermediates and optional ARMv7 outputs remain local and uncommitted; no files were removed. The retained final phone installation was not touched.
- Existing root deny-by-default and nested secret/build exclusions are unchanged. There are no tracked private/runtime/APK/database/Keystore paths.
- The protected phone-preflight input loader has no encoded PIN fallback; credentials come only from ignored protected input files.

## Secret and content review

Worktree review covered 171 existing public files and all 119 HEAD blobs. Exact local mnemonic, BIP39 seed, derived account private keys and credential values were checked in binary/text, UTF-16, hexadecimal and Base64 forms. No actual secret match was found. Private-key formats, mnemonic word sequences and credential/encoding contexts were reviewed. The only private-key-format match was an existing synthetic rejection-test marker with no key body. The public BIP39 reference list and synthetic gate tests are not private fixtures.
All pending Python source parsed successfully; this is an offline hygiene check, not another experiment. Final index/staged contents receive the same exact-secret scan before commit. Raw experiment evidence is deliberately not staged.

## Evidence index disposition

B1/B2/R1/R1A/phone report references and the public SHA-256 index below belong in Git. The referenced JSON indexes, manifests, oracles and member files remain intentionally ignored under `runs/`; their bytes are retained locally. Git contains digest bindings, not copies of raw runtime/security evidence. Closure does not reseal or transform H2.

| Retained manifest | Members checked against stored digest/size |
| --- | ---: |
| `runs/wo3b2-r3/evidence-manifest.json` | 20 |
| `runs/wo3c-r1/evidence-manifest.json` | 30 |
| `runs/wo3c-r1a/evidence-manifest.json` | 16 |
| `runs/wo3c/phone-ab/control/evidence-manifest.json` | 55 |
| `runs/wo3c/phone-ab/candidate/evidence-manifest.json` | 40 |
| `runs/wo3c/phone-ab/final-evidence-manifest.json` | 10 |

The immutable H2 manifest and both payload hashes match. The original x86 validator and transport hashes match the accepted R1 audit. Final phone arm results are PASS; the final comparison remains PHONE-PASS. Known DAO occupied-capacity discrepancy (102 CKB canonical versus 61 CKB Pocket reader) stays separate.

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

## Closure scope and remaining local custody

One closure commit is authorized after the safe-file classification and staged-secret check pass. No push or owner message is authorized by this hygiene task. The commit hash is reported after creation; it is not embedded in its own content.
Important local-only custody includes immutable H2, B1/B2 historical evidence, ARM artifact/provenance, R1/R1A observations, sealed phone arm evidence, canonical FP/final oracles, original preflight/report archives, private recovery material and the retained Candidate phone installation. A repository clone alone does not contain these raw artifacts. Preserve the local workspace or a separately controlled archive; do not publish private material.
No additional PM decision is needed for this closure commit. Any later evidence distribution, maintainer handoff or further device work remains outside this task.
