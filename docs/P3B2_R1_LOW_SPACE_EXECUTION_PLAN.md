# WO-3B2-R1 sequential low-space execution plan

2026-10-06. **GO on storage readiness for a PM-approved B2 resume; no Android recovery was run in this order.** The experiment now retains at most **one live emulator userdata/Keystore state** at a time. SOURCE, A2 and B2 remain logically independent. The previous approximate 15 GiB allowance for retaining three images is superseded by a **10 GiB pre-launch free-space target** for this sequential lifecycle.

## One runtime at a time, shared qualified setup

Reuse the same installed API-36 default x86_64 system image and logical `H02_P0_API36_X64` hardware profile: 2048 MiB RAM, 2 vCPUs, WHPX, Intel Iris Xe host GPU, 6 GiB userdata, headless, no audio, `-no-snapshot -no-boot-anim -gpu host`, explicit emulator serial `emulator-5580`. Never SwiftShader. Use the exact retained APK; no rebuilding or different version. No physical phone.

Keep tiny **role-specific registry/config directories** because the existing helpers use their absolute paths to prove role ownership. These are provenance labels around one reused emulator/profile/system-image setup, not three permanent disk images. Only the current role has runtime image files. Recreating a clean runtime for each role is simpler to audit than repointing a shared mutable role marker and changing the qualified role guards. No copies of system images, old userdata, guest Keystore, full app sandbox or emulator memory are made.

```text
Installed API-36 system image + one qualified profile + one pinned APK
                         |
SOURCE: fresh userdata -> normal keys/accounts -> real fixture -> H2 package
                         -> real post-H2 events -> F2 public oracle
                         -> extract + verify evidence -> LOST -> retire runtime
                         |
A2:     fresh userdata -> normal keys/accounts -> reconstruct -> full acceptance
                         -> restart -> extract + verify evidence -> retire runtime
                         |
B2:     fresh userdata -> normal keys/accounts -> sanitized H2 restore
                         -> F2 catch-up -> acceptance + restart -> compare
                         |
              retain compact evidence; retire final runtime after review
```

Physical layout: `runs/wo3b2/source/avd`, then `control/avd`, then `candidate/avd`; preserve each role's `boot/`, timing/results and extracted public state separately. Source already has a pristine definition, but **no userdata was ever created** in the failed B2 attempt. Do not overwrite its failed `boot/`; the first retry uses `boot-retry1`. A2/B2 runtime creation is forbidden until the prior role's retirement receipt confirms removal. The old B1 AVDs are retired and must never be used to bootstrap B2.

This changes lifetime and retention, not recovery semantics. If PM requires one identical physical registry path, that would require a small helper/role-guard refactor; it saves only config bytes and is unnecessary to achieve one-runtime disk use. The plan deliberately retains the existing absolute-path guards.

## Freshness proof before every role

1. Confirm no H02 emulator/qemu process or port 5580 listener remains. All commands explicitly select the emulator; never use an implicit ADB target.
2. Before creation, verify that this role has no userdata/cache/encryption-key/runtime-memory images. Keep a metadata inventory and creation timestamp. For A2/B2, require a completed predecessor retirement receipt and no predecessor runtime image, plus SOURCE `LOST.json`. Create from the installed system image, never from another role's disk.
3. Cold boot with snapshots disabled. Record absolute registry/datadir, launch flags, guest boot ID, API/ABI and responsive Android checks. A fresh boot ID alone is **not** proof of a fresh installation.
4. Before install, require `pm path com.rjnr.pocketnode` to be absent. Install the one approved APK; verify installed version/code, debuggability and exact installed hash. Before first Pocket launch, `run-as` must show no Room database, native testnet store, Pocket preferences or key-backup directory. The normal key-material table cannot already exist because the Room DB does not exist. Record only absence booleans, not secret-bearing contents.
5. The destination Android Keystore is fresh because the entire userdata **and its encryption-key backing** were recreated, not because `pm clear` was run. Do not read/export Keystore internals. Record normal creation of destination wallet UUIDs and public Scripts afterward; compare account identities while allowing fresh local UUIDs. Repeated package UID or Android system-image identity is not evidence of state reuse or independence.
6. Start the recovery timer before first Pocket launch. Use supported phrase import/account creation with the private helper; no credential arguments, logs or screenshots. Verify expected account-0/account-1 Scripts, parent relationship and correct historical coverage through supported UI. No Room/key-row injection.

The current B2 provisioner already checks the exact runtime role, API/ABI, Android health, fresh package installation, APK hash and absent Room DB. At the approved resume, extend its empty-sandbox observation to the additional **absence-only** native/preferences/backup checks above and record prior-role retirement before A2/B2 creation. This is a test-harness freshness guard, not a production Pocket change. No such new Android check was executed during this storage order.

## Evidence checkpoint before retiring SOURCE

SOURCE must first satisfy the full B2 contract: two genuinely populated Scripts with correct account mappings/history/live Cells/balances, actual DAO state, per-Script and Room progress/discovery, app reconciliation and restart. No fixture acceptance was established by this storage audit.

Export H2 with the approved sanitized two-account policy after quiescence. Retain immutable package + independently retained trusted manifest digest, source version/schema/network/genesis, H2/hash, exact per-account coverage/progress and required public DAO observations. Verify hashes and known-secret exclusion. Preserve canonical H2 oracle and all export/security receipts.

Create the required real post-H2 account-0 spend and account-1 activity; perform only a legitimately available DAO transition. Establish F2 and its public headers/outpoints/transaction facts, including old-Cell liveness proof. Freeze further fixture activity. Save the complete oracle and all claims needed by A2/B2 **before** declaring loss.

Force-stop/disable Pocket, stop the emulator and confirm process exit. Seal the extracted evidence with hashes; record `LOST.json`. Retain only the already approved private recovery fixture, sanitized H2 package and public/canonical records as arm inputs. Then classify and record the exact SOURCE runtime paths for retirement and remove them. Do not reopen/query SOURCE DBs after loss. Retiring its disposable guest keys is not deleting `H02-P0/private`.

If source correctness/evidence extraction is incomplete, stop and retain the runtime for diagnosis. Do not destroy it to force the next arm to fit.

## A2 and B2 checkpoints

**A2:** create independent empty userdata, normal key/account recovery, correct history coverage, no state package. Run complete F2 acceptance, signing-readiness and restart checks. Export allowlisted public app/DAO/account rows and native logical observations; retain exact live Cells, histories, capacities, per-Script registrations/progress, cache reconciliation, timing events and semantic result/hash. Re-read and validate these host-side artifacts and their hashes. Stop the emulator, write a retirement receipt and remove its exact runtime images. A PASS boolean alone is insufficient grounds for retirement.

**B2:** create independent empty userdata; normally recover keys/accounts, validate exact mapping/network/version/schema, restore only the sanitized H2 package, include package operations in timing, and catch up to F2. Require stale-Cell removal, new activity on both Scripts, correct DAO/native/app state, no cross-mapping, coherent progress, signing readiness and restart. Compare against the retained canonical oracle and A2 result without consulting either prior guest. Preserve final captures/timing/result and package-negative evidence. Do not preemptively delete B2 on failure; retain it for diagnosis.

The one-off R1 cleanup script is tied to historical B1 paths and already consumed; **do not repurpose or rerun it for B2**. Future retirement must generate its own exact-path inventory/receipt and verify all completion/evidence/containment gates. Keep configs, boot logs, original manifests/hashes, result JSON and independent raw observation captures. Never delete a whole role results directory. No emulator snapshot is a recovery input; old `snapshots/default_boot/ram.img` names were runtime storage artifacts, not a required replay mechanism.

## Space calculation

The fresh 6 GiB userdata check is an observed **7.2 GiB free-space admission floor**, not the total project requirement. Existing SDK image/APK/dependencies are already on disk and are not downloaded/copied per arm.

The largest retired B1 runtime image set was 3,076,456,960 logical bytes (**2.865 GiB**), including approximately 2 GiB `ram.img` plus under 0.8 GiB userdata overlay. H02's B1 package was 1,895,341 bytes. Its entire R2 run excluding the two destination runtime image sets was about 46 MiB; R1 diagnostics were about 57 MiB. These are measured reference sizes, not an assertion that B2 DAO/two-account state will be identical.

| Budget item | GiB | Basis |
|---|---:|---|
| Single-role guest userdata allowance | 6.00 | Full configured logical partition; conservative versus measured <0.8 GiB overlay |
| Runtime RAM/backing image | 2.00 | Measured 2,147,549,184-byte files, rounded |
| Cache, encryption backing, qcow metadata / small runtime overhead | 0.20 | Covers measured sidecars with headroom |
| Retained B2 package, oracles, exact captures, receipts | 0.25 | Explicit cap/budget, several times B1 compact evidence; not a performance prediction |
| Temporary transaction / bounded log outputs | 0.05 | Keep logs bounded; no private sandbox dumps |
| Additional free-space safety reserve | 1.50 | Host writes and variable growth |
| **Pre-launch target, rounded** | **10.00** | At most one runtime; no three-image multiplier |

The expected normal occupied increment is nearer the measured **2.9 GiB runtime + 0.3 GiB evidence/log allowance**. The 10 GiB target also covers a much fuller single guest, rather than treating sparse initial allocation as guaranteed. It exceeds the 7.2 GiB admission floor. The 0.25 GiB allowance covers cumulative compact evidence across all three roles; runtime storage is reclaimed between them. Current measured free space is **15.336 GiB**, exceeding target by **5.336 GiB**.

Recheck free space before each role, not just today. Bound diagnostic capture duration/size, do not leave continuous logcat recording, and sample host free space during long reconstruction. Pause new workload if free space falls below 1.5 GiB; preserve evidence and investigate rather than letting the drive fill. If B2 evidence exceeds its budget, measure and revise it before the next role; never silently drop required observations. No full-history-from-genesis scan is added for storage qualification.

## Exact next step after PM review

Storage is ready. No launch/recovery/transfers/transactions ran here. PM's next approved order should resume the existing B2 contract with this lifecycle and the absence/retirement guards above. Keep failed B2 evidence and the B1 PASS record.

From H02-P0, first measure free space and retain the **10 GiB** pre-launch threshold. Use existing source definition and a new boot label:

```powershell
Set-Location 'C:/Users/timot/Desktop/2026/CKB/H02-P0'
if ([IO.DriveInfo]::new('C:/').AvailableFreeSpace -lt 10GB) { throw 'Below B2 sequential storage target' }
powershell -NoProfile -File scripts/b2_boot_role.ps1 -Role source -Attempt boot-retry1
# Proceed only after a successful launch; provision and complete the absence-only gates.
python scripts/b2_provision.py source --attempt boot-retry1
# Only after all freshness/health gates pass:
& runs/wo3-setup/venv/Scripts/python.exe scripts/b2_recover.py source --attempt boot-retry1
```

These are **future commands, not executed in R1**. SOURCE recovery restores account 0 first; account 1 and DAO preparation must still use the PM-approved normal flows. There is no new B2 result and no demonstrated D2 responsibility. **STOP for PM review.**
