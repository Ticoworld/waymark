# WO-3B2-R1 storage audit and targeted reclamation

2026-10-06 local date (record timestamps use UTC). **Storage blocker resolved; Android B2 was not resumed.** Classification preceded deletion. No recovery, transaction, phone access, D2 experiment, historical source edit, rebuild or global cleanup ran.

## Space accounting

| Observation | Bytes | GiB |
|---|---:|---:|
| C: total | 498,539,163,648 | 464.301 |
| First metadata-scan free space | 7,596,285,952 | 7.075 |
| Immediately before targeted deletion | 7,114,579,968 | 6.626 |
| Immediately after targeted deletion | 16,467,501,056 | 15.337 |
| Net increase over deletion interval | 9,352,921,088 | 8.711 |
| Verification free space | 16,466,493,440 | 15.336 |

The initial scan and cleanup interval have different start times. Other host writes consumed space during classification. Per-group free-space deltas sum to 9,352,994,816 bytes; they differ slightly from the aggregate interval because receipts and other host activity occur between samples. These are observed filesystem deltas, not a claim of perfectly isolated attribution.

H02 before: 10.316 GiB logical / 9.299 GiB estimated disk bytes. After: 0.705 / 0.517 GiB. `runs/` before: 10.240 / 9.223 GiB; after: 0.629 / 0.442 GiB. Small new audit files/commits can change the after totals. CKB workspace before was 21.474 GiB logical / 20.457 GiB estimated disk bytes; only the stated H02 subsets were removed.

## Method and limits

`b2r1_storage_inventory.py` inspected path/size metadata, never wallet-secret contents. Windows disk estimates use `GetCompressedFileSizeW`, accounting for compression/sparse storage where supported; allocation rounding, hardlinks and directory metadata prevent equating their sum with exact drive occupancy. Ranked rows overlap (parents contain children): **do not add them**. Reparse points were not traversed. 1228 reparse entries were skipped and 400 file/directory queries failed, including long historical build paths and inaccessible Windows Temp. Those tree totals are lower bounds, not a claim of a perfect whole-drive inventory. Full errors/metadata are retained in `runs/wo3b2-r1/storage-before.json`.

The scan covered CKB, Android SDK/AVDs, shared Gradle/Cargo/Rustup, user/Windows temp, C:/tmp, C:/temp, C:/w, C:/Ubuntu, C:/mnt, Downloads and .cache. Windows Temp's zero enumerated bytes means inaccessible/unmeasured, not empty. `C:/Ubuntu` contains only 200 enumerated bytes; the active Ubuntu VHD is at the registered AppData path below. No whole-home secret search was performed.

## Ranked relevant directories / VHDs and classification

The four classifications apply to specific candidates. KEEP ? SMALL / USEFUL includes large installed tools where usefulness, not small size, is the reason. An authoritative parent can contain only the explicitly enumerated disposable exceptions below.

| Path | Logical GiB | Disk estimate GiB | Classification | Reason retained |
|---|---:|---:|---|---|
| `C:\Users\timot\AppData\Local\wsl\{95e7ee7f-c472-40f1-9157-e4b250feaf31}\ext4.vhdx` | 77.600 | 76.012 | KEEP ? AUTHORITATIVE EVIDENCE | Contains protected Linux research including ibytes-recurrence; no VHD compaction. |
| `C:\Users\timot\AppData\Local\Docker\wsl\disk\docker_data.vhdx` | 27.427 | 27.427 | UNKNOWN ? DO NOT DELETE | Docker workloads/volumes not inventoried as disposable; retained. |
| `C:\Users\timot\Desktop\2026\CKB` | 21.474 | 20.457 | KEEP ? AUTHORITATIVE EVIDENCE | Mixed workspace; only the exact H02 exceptions below were deleted. |
| `C:\Users\timot\AppData\Local\Android\Sdk` | 15.708 | 15.708 | KEEP ? SMALL / USEFUL | Qualified image/toolchain retained; no SDK uninstall. |
| `C:\Users\timot\.android\avd` | 15.015 | 14.896 | UNKNOWN ? DO NOT DELETE | Other projects? AVD ownership/evidence not established. |
| `C:\Users\timot\.gradle` | 13.406 | 13.406 | KEEP ? SMALL / USEFUL | Shared pinned dependencies/wrappers; avoid unrelated rebuild/download cost. |
| `C:\Users\timot\.gradle\caches` | 12.054 | 12.054 | KEEP ? SMALL / USEFUL | Shared dependencies/transforms, not proven exclusive to H02. |
| `C:\Users\timot\.android\avd\Pixel_8.avd` | 11.373 | 11.313 | UNKNOWN ? DO NOT DELETE | Userdata could contain independent work; not H02. |
| `C:\Users\timot\Desktop\2026\CKB\H02-P0` | 10.316 | 9.299 | KEEP ? AUTHORITATIVE EVIDENCE | Experiment documents, keys and evidence; targeted generated exceptions only. |
| `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs` | 10.240 | 9.223 | KEEP ? AUTHORITATIVE EVIDENCE | Mixed evidence/build/runtime; classified below. |
| `C:\Users\timot\.rustup` | 5.669 | 5.669 | KEEP ? SMALL / USEFUL | Pinned and other toolchains; no upgrade/uninstall. |
| `C:\Users\timot\Desktop\2026\CKB\ckb-script-port` | 5.059 | 5.059 | KEEP ? AUTHORITATIVE EVIDENCE | D2/PR #297 and Pocket history protected. |
| `C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work` | 5.017 | 5.017 | KEEP ? AUTHORITATIVE EVIDENCE | No wholesale historical-worktree cleanup. |
| `C:\Users\timot\.android\avd\Chevta_2C_AOSP36.avd` | 3.642 | 3.583 | UNKNOWN ? DO NOT DELETE | Not the isolated H02 AVD; do not infer disposable from name. |
| `C:\Users\timot\AppData\Local\Temp` | 3.278 | 3.304 | UNKNOWN ? DO NOT DELETE | Includes large full.txt and mixed temporary work; content/provenance not inferred. |
| `C:\Users\timot\Desktop\2026\CKB\H03` | 2.453 | 2.453 | UNKNOWN ? DO NOT DELETE | Separate active research, not disposable H02 output. |
| `C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\upstream\ckb-light-client\_work\build` | 1.409 | 1.409 | UNKNOWN ? DO NOT DELETE | Build-looking historical directory; provenance/required binaries not re-established. |
| `C:\Users\timot\.cache` | 1.295 | 1.295 | KEEP ? SMALL / USEFUL | Installed Codex runtime cache; no unrelated cleanup. |
| `C:\Users\timot\.cargo` | 1.226 | 1.226 | KEEP ? SMALL / USEFUL | Shared registry/git/tool binaries; not H02 target outputs. |
| `C:\tmp` | 0.433 | 0.433 | UNKNOWN ? DO NOT DELETE | Research/temp paths not classified by content. |
| `C:\Users\timot\Desktop\2026\CKB\ckb-script-port\_work\g3-1-pocket-node\android\app\build` | 0.283 | 0.283 | UNKNOWN ? DO NOT DELETE | Historical Pocket build/evidence context, deliberately retained. |
| `C:\Users\timot\Desktop\2026\CKB\grant_find` | 0.268 | 0.268 | KEEP ? AUTHORITATIVE EVIDENCE | Historical research and clean Pocket donor protected. |
| `C:\Users\timot\AppData\Local\Docker\wsl\main\ext4.vhdx` | 0.102 | 0.102 | UNKNOWN ? DO NOT DELETE | Docker workloads/volumes not inventoried as disposable; retained. |
| `C:\Users\timot\Downloads` | 0.057 | 0.057 | UNKNOWN ? DO NOT DELETE | No archive/repository equivalence proved. |
| `C:\temp` | 0.029 | 0.029 | UNKNOWN ? DO NOT DELETE | No broad temp deletion. |
| `C:\w` | 0.016 | 0.016 | UNKNOWN ? DO NOT DELETE | Possible working material; small enough to leave. |
| `C:\Users\timot\Desktop\2026\CKB\iBytes` | 0.008 | 0.008 | KEEP ? AUTHORITATIVE EVIDENCE | Modified/untracked experiments and worktree metadata protected. |

## Largest relevant files (before cleanup)

| File | Logical GiB | Disk estimate GiB |
|---|---:|---:|
| `C:\Users\timot\.android\avd\Pixel_8.avd\userdata-qemu.img.qcow2` | 8.406 | 8.406 |
| `C:\Users\timot\AppData\Local\Android\Sdk\system-images\android-36\google_apis\arm64-v8a\system.img` | 4.112 | 4.112 |
| `C:\Users\timot\AppData\Local\Android\Sdk\system-images\android-37.0\google_apis_playstore_ps16k\x86_64\system.img` | 2.777 | 2.777 |
| `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo2\avd\H02_P0_API36_X64.avd\snapshots\default_boot\ram.img` | 2.000 | 2.000 |
| `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\candidate\avd\H02_P0_API36_X64.avd\snapshots\default_boot\ram.img` | 2.000 | 2.000 |
| `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\control\avd\H02_P0_API36_X64.avd\snapshots\default_boot\ram.img` | 2.000 | 2.000 |
| `C:\Users\timot\.android\avd\Chevta_2C_AOSP36.avd\snapshots\default_boot\ram.img` | 2.000 | 2.000 |
| `C:\Users\timot\.android\avd\Pixel_8.avd\snapshots\default_boot\ram.img` | 2.000 | 2.000 |
| `C:\Users\timot\AppData\Local\Android\Sdk\system-images\android-36\default\x86_64\system.img` | 1.769 | 1.769 |
| `C:\Users\timot\.android\avd\Chevta_2C_AOSP36.avd\userdata-qemu.img.qcow2` | 1.471 | 1.471 |
| `C:\Users\timot\AppData\Local\Temp\full.txt` | 1.264 | 1.264 |
| `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo2\avd\H02_P0_API36_X64.avd\userdata-qemu.img.qcow2` | 0.769 | 0.769 |

Only the three H02 `ram.img` entries and the other explicitly listed H02 runtime/build paths were retired. Global AVD files, SDK images and `Temp/full.txt` remain UNKNOWN/useful and were not removed merely because they are large.

## WSL research/build storage

Ubuntu's guest filesystem reported 78,785,122,304 used bytes; the dynamically allocated host VHD occupies approximately 76.012 GiB. Guest `du` sizes are not an immediately reclaimable C: amount. Deleting guest files alone does not guarantee VHD shrinkage. No WSL deletion, trim or VHD compaction was attempted.

| Guest path | Measured GiB | Classification |
|---|---:|---|
| `/home/timot` | 68.363 | KEEP ? AUTHORITATIVE EVIDENCE / mixed |
| `/home/timot/.cache/ckb-light-client-v2-target` | 14.122 | UNKNOWN ? DO NOT DELETE; historical build provenance not re-established |
| `/home/timot/ibytes-target` | 6.496 | UNKNOWN ? DO NOT DELETE; protected investigation context |
| `/home/timot/fairbake-target` | 5.072 | UNKNOWN ? DO NOT DELETE; separate work |
| `/home/timot/ckb-lc-target` | 4.786 | UNKNOWN ? DO NOT DELETE |
| `/home/timot/ev1-r5-d2-target` | 2.920 | UNKNOWN ? DO NOT DELETE |
| `/home/timot/ckb-light-client-target` | 2.397 | UNKNOWN ? DO NOT DELETE |
| `/home/timot/ev1-r3-upstream-sqlite` | 2.320 | UNKNOWN ? DO NOT DELETE |
| `/home/timot/d2-phase45-target` | 2.082 | UNKNOWN ? DO NOT DELETE |
| `/home/timot/ev1-r3-target-d2-sqlite` | 2.064 | UNKNOWN ? DO NOT DELETE |
| `/home/timot/d2-target` | 1.893 | UNKNOWN ? DO NOT DELETE |
| `/home/timot/ibytes-recurrence` | 0.025 | KEEP ? AUTHORITATIVE EVIDENCE; explicitly protected |

Other Linux dependency/tool caches are retained. `wsl-metadata.txt` records the wider size ranking. Merely measuring historical directory metadata did not reopen any D2 proof or use it as an H02 input.

## H02 run retention policy

| Run | Before disk GiB | After disk GiB | Retention decision |
|---|---:|---:|---|
| `wo2/` | 3.820 | 0.292 | Keep build logs, exact APK/signature/library metadata, JNI inputs, signing/toolchain prerequisites and compiled helpers. Retire only listed build intermediates and shared completed SOURCE runtime images. Keep original AVD config/registry and diagnostic evidence. |
| `wo3-setup/` | 0.022 | 0.022 | Keep public fixture verification/oracles and Python environment. Private recovery acquisition stays under private/ and was not opened. |
| `wo3b1/` | 0.000 | 0.000 | Keep failed-run compact diagnostics; no completed wallet existed. No deletion. |
| `wo3b1-r1/` | 0.055 | 0.055 | Keep both original/host-GPU boot diagnostics and qualification records. Their AVD was later the completed B1 SOURCE; no separate diagnostic copy needs keeping. |
| `wo3b1-r2/` | 5.325 | 0.045 | Keep immutable H package, original package, oracle, live-cell/app/native captures, acceptance/restart results, events, negative cases, helper jars and source loss/hash record. Retire only completed A/B runtime images. |
| `wo3b2/` | 0.000 | 0.000 | Keep failed startup log/config, preservation hashes and receipts. No userdata was created; deletion would save almost nothing. |

The completed B1 SOURCE, A and B emulator images are **SAFE TO DELETE / REGENERATE as experiment runtimes**, not reusable evidence inputs. Normal source/key recovery can regenerate a new runtime; it cannot recreate the exact old runtime bytes. Exact historical audit uses the retained package, public oracle, frozen native/app captures, restart acceptance and timestamps. Whole-guest memory/sandbox forensics and reopening those old installations are intentionally no longer available. No independent raw database/WAL capture was deleted. The original source seal/hash inventory is retained unchanged as historical provenance; this retirement receipt documents why its image files now do not exist. No sealed source DB was reopened to make this decision.

## Approved APK

Exactly one loose approved APK was found in H02 and retained at:

`C:/Users/timot/Desktop/2026/CKB/H02-P0/runs/wo2/gradle/app/outputs/apk/debug/app-debug.apk`

49,764,015 bytes; SHA-256 **`903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`** before and after deletion. This is the canonical B2 artifact. No new copy or rebuild was made. The APK is inside `outputs/`, which was excluded from cleanup. Existing metadata, signatures, JNI input hashes, compiled helpers, pinned source/toolchains/dependency caches and isolated debug signing material remain. Historical APKs elsewhere were not deleted or deduplicated; the exact-copy count is scoped to H02.

## Executed deletion groups

All five groups were classified and recorded in `cleanup-classification.json` before deletion. `b2r1_safe_cleanup.ps1` accepts only 23 exact targets, verifies containment under H02/runs, refuses reparse/repository metadata, checks no emulator/native build is active, validates the approved APK, and records every group before deleting it. It refuses a second invocation once receipts exist. No `git clean`, blanket target/cache removal or cross-shell destructive command ran.

| Group | Logical GiB | Disk estimate GiB | Observed reclaimed bytes | Observed GiB |
|---|---:|---:|---:|---:|
| B1_SOURCE | 2.865 | 2.806 | 3,012,612,096 | 2.806 |
| B1_CONTROL | 2.702 | 2.642 | 2,837,200,896 | 2.642 |
| B1_CANDIDATE | 2.698 | 2.638 | 2,832,867,328 | 2.638 |
| H02_NATIVE_BUILD | 1.191 | 0.611 | 545,447,936 | 0.508 |
| H02_GRADLE_INTERMEDIATES | 0.183 | 0.111 | 124,866,560 | 0.116 |

Runtime groups: completed B1 results and extracted audit evidence make these disposable; regenerate only a fresh qualified AVD/normal recovery, never restore old guest state. Native target: `build-pocket-native.ps1` explicitly selects this external Cargo target path. Gradle intermediates: `wo2-build.init.gradle` explicitly redirects build outputs here. Regeneration is the retained native/Android build recipe; source, locks, toolchains, JNI inputs and final APK are preserved. Neither directory is a source checkout or result store. No rebuild was run to prove this classification.

Every deleted path:

- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo2\avd\H02_P0_API36_X64.avd\userdata-qemu.img` ? 6,356,992 logical bytes; 6,356,992 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo2\avd\H02_P0_API36_X64.avd\userdata-qemu.img.qcow2` ? 826,015,744 logical bytes; 826,015,744 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo2\avd\H02_P0_API36_X64.avd\cache.img` ? 69,206,016 logical bytes; 5,373,952 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo2\avd\H02_P0_API36_X64.avd\cache.img.qcow2` ? 197,120 logical bytes; 197,120 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo2\avd\H02_P0_API36_X64.avd\encryptionkey.img` ? 18,874,368 logical bytes; 18,874,368 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo2\avd\H02_P0_API36_X64.avd\encryptionkey.img.qcow2` ? 8,257,536 logical bytes; 8,257,536 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo2\avd\H02_P0_API36_X64.avd\snapshots\default_boot\ram.img` ? 2,147,549,184 logical bytes; 2,147,549,184 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\control\avd\H02_P0_API36_X64.avd\userdata-qemu.img` ? 6,356,992 logical bytes; 6,356,992 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\control\avd\H02_P0_API36_X64.avd\userdata-qemu.img.qcow2` ? 651,886,592 logical bytes; 651,886,592 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\control\avd\H02_P0_API36_X64.avd\cache.img` ? 69,206,016 logical bytes; 5,373,952 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\control\avd\H02_P0_API36_X64.avd\cache.img.qcow2` ? 197,120 logical bytes; 197,120 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\control\avd\H02_P0_API36_X64.avd\encryptionkey.img` ? 18,874,368 logical bytes; 18,874,368 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\control\avd\H02_P0_API36_X64.avd\encryptionkey.img.qcow2` ? 6,946,816 logical bytes; 6,946,816 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\control\avd\H02_P0_API36_X64.avd\snapshots\default_boot\ram.img` ? 2,147,549,184 logical bytes; 2,147,549,184 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\candidate\avd\H02_P0_API36_X64.avd\userdata-qemu.img` ? 6,356,992 logical bytes; 6,356,992 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\candidate\avd\H02_P0_API36_X64.avd\userdata-qemu.img.qcow2` ? 647,692,288 logical bytes; 647,692,288 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\candidate\avd\H02_P0_API36_X64.avd\cache.img` ? 69,206,016 logical bytes; 5,373,952 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\candidate\avd\H02_P0_API36_X64.avd\cache.img.qcow2` ? 197,120 logical bytes; 197,120 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\candidate\avd\H02_P0_API36_X64.avd\encryptionkey.img` ? 18,874,368 logical bytes; 18,874,368 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\candidate\avd\H02_P0_API36_X64.avd\encryptionkey.img.qcow2` ? 7,012,352 logical bytes; 7,012,352 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo3b1-r2\candidate\avd\H02_P0_API36_X64.avd\snapshots\default_boot\ram.img` ? 2,147,549,184 logical bytes; 2,147,549,184 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo2\native\target` ? 1,279,213,590 logical bytes; 656,188,726 estimated disk bytes.
- `C:\Users\timot\Desktop\2026\CKB\H02-P0\runs\wo2\gradle\app\intermediates` ? 195,966,406 logical bytes; 119,536,800 estimated disk bytes.

## Verification and remaining candidates

After cleanup, **1,758 hashed retained files matched** their pre-cleanup values; this includes compact B1 evidence, helper binaries and committed docs/scripts. Private storage was checked by metadata only and remains present. Sealed source captures were excluded from content hashing and preserved untouched. All deletion targets are absent. The APK digest matches. No physical phone or Android emulator command was issued during this order.

No further large item is currently classified SAFE without additional provenance work. Remaining H02 generated Gradle subdirectories are small/useful and need not be removed. Large global AVDs, shared Gradle caches, historical targets, WSL builds/VHDs, H03 and Temp/full.txt could contain reclaimable storage, but remain UNKNOWN or protected; they were deliberately not used to meet this request. `/home/timot/ibytes-recurrence`, iBytes modifications, historical `_work`, pre-public-history metadata, PR #297 source/worktrees and grant_find remain intact.

Authoritative evidence deleted: **NO**. Historical repository modified: **NO**. Private fixture preserved: **YES**. Storage is sufficient for the 10 GiB sequential launch target in the companion plan. **STOP; no B2 recovery resumed.**
