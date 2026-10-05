# WO-3B2 SOURCE result ? environmental block before boot

**Not recovered; no source correctness or H2 claim.**

Pocket v1.8.5, commit `b28979de744798ffb75367b031d4871ec3af1a12`; TESTNET intended. Approved APK SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. No production source changes, D2, Samsung access, mnemonic entry or B2 transactions. B1 remains PASS and its evidence is preserved.

## Actual sequence

1. Preserved hashes of existing B1 reports and all preexisting helper source files in `runs/wo3b2/prior-evidence-hashes.json`.
2. Created fresh isolated registry `runs/wo3b2/source/avd`, logical AVD name `H02_P0_API36_X64`. Only this new B2 registry was marked NTFS-compressed.
3. Requested launch at 2026-10-05 22:40:06 UTC using `-datadir <B2 source AVD> -port 5580 -no-window -no-audio -no-snapshot -no-boot-anim -gpu host`.
4. The emulator process exited before userdata creation. Its preserved log says:

```text
FATAL | Not enough space to create userdata partition. Available: 6131.66 MB ... need 7372.80 MB.
```

5. The initial provisioning invocation also exposed a copied helper's CLI choices omission (`source` missing). That test-helper bug was fixed. The next provisioning attempt refused `wrong-live-role` because there was no running emulator. Neither attempt reached APK installation or Pocket launch.
6. Applied lossless NTFS compression only to generated WO-2 native/Gradle/MSVC build outputs under this isolated H02 workspace. No deletion, source edits, B1 artifact compression, old-source DB access or partition resizing. Compression completed successfully; the APK still matches its approved hash.
7. A new boot-space guard refused a retry before launching anything. The original launch/logs remain unchanged. There is no second boot result.

## Qualified configuration retained

API 36/default/x86_64 revision 2, 2048 MiB RAM, 2 vCPUs, WHPX, host Intel Iris Xe graphics, headless, snapshots disabled, 6 GiB userdata. No SwiftShader or configuration downgrade. R1 qualification was not repeated; Android never started in this B2 attempt.

## Disk evidence

Final recorded free space: **7,006,797,824 bytes (about 6.53 GiB)**. Emulator admission requires **7,730,941,133 bytes (7.2 GiB)** for this fresh 6 GiB partition. The recorded shortfall is **724,143,309 bytes**, before allowing for independent A2/B2 environments or subsequent growth. Free space fluctuates with other host activity.

Compression summaries (logical bytes -> stored bytes): native 1,279,216,314 -> 656,191,450; Gradle 272,567,352 -> 178,289,572; MSVC 424,032,683 -> 240,731,299. These are final compact summaries, not a claim that the whole difference was newly reclaimed; some files may already have been compressed. Evidence is in `runs/wo3b2/*-compression.txt`.

`runs/wo3b2/preservation-and-preflight.json` records 63 prior files unchanged, clean pinned Pocket source, matching APK, no SOURCE provisioning result, no recovery events and no userdata file. No secret was entered or logged.

SOURCE account state, history, balance, progress, restart, DAO, H2/hash, package size/export/security gate: **NOT RUN / NOT CREATED**. SOURCE was not declared lost because it was never established.
