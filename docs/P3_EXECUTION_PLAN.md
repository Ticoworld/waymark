# WO-3 execution plan for PM review

Date: 2026-10-05. **Not executed.** Exactly two performance arms: normal recovery A and same-version state recovery B. D2 is excluded. The question remains whether a sanitized, wallet-owned, same-version backup already solves the recovery job.

## Fixed decisions

Use the recovered existing mnemonic family on **TESTNET**, with its existing three-transaction history. No new primary wallet or external funding is needed. Add only the missing account-1/DAO/stale-backup fixture events after approval; the current one-account/no-DAO state is not an acceptable substitute.

All experiment roles run the existing debug APK from Pocket v1.8.5, commit `b28979de744798ffb75367b031d4871ec3af1a12`, SHA-256 `903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f`. Embedded LC 0.5.4, tree `3ac3e0ce1f4e46897d188b76c5b841b9097fa506`, Room 17. Do not import the phone's v1.8.3/Room-15 store or reuse its D2-transplanted chain state as the H02 source.

```
Samsung / v1.8.3 ----- public historical reference only
       |
       +-- private recovery fixture (retained before loss)
                 |
        fresh v1.8.5 SOURCE emulator
        normal recovery + fixture preparation + sync through H
                 |
                 +-- WO-2 sanitized non-secret package + trusted digest
                 +-- public fixture ledger / canonical oracle facts
                 |
           stop and seal source; phone also unavailable to arms

    fresh v1.8.5 CONTROL A          fresh v1.8.5 CANDIDATE B
    normal key/account recovery    normal key/account recovery
    normal historical scan         sanitized state restore + catch-up
                  \                /
              identical full acceptance at F; restart check
```

Use **three separate userdata directories**, one emulator at a time on port 5580. Source reuses the still-empty WO-2 AVD at `runs/wo2/avd`. Create A and B from the installed system image under `runs/wo3/control/avd` and `runs/wo3/candidate/avd`; never copy a source userdata image. Each isolated registry uses the same logical AVD name `H02_P0_API36_X64`, so the existing exact-name/device/version guard remains unchanged. Record the absolute registry/data path and role with every run; serial/name alone cannot distinguish these profiles.

Keep API 36/default/x86_64, image revision 2, 2 CPUs, 2048 MiB RAM, requested 4G data partition, pixel_6 hardware, WHPX, SwiftShader and `-no-snapshot` identical. Only one process may own port 5580. Boot A/B once for OS/APK provisioning, before timing, with Pocket unlaunched; collect the same empty-sandbox check. Distinct fresh Keystore state and app UUIDs are required. Installation/OS provisioning are reported separately. No physical phone wipe or simulated destructive loss is necessary.

## Execution gates and sequence

1. **Untimed source automation preflight.** Boot source, select TESTNET through supported UI, navigate to normal phrase recovery, run the private phrase-entry helper, then submit through normal UI. Use the same emulator lock/PIN policy planned for A/B. No screenshots, hierarchy dumps or logcat capture during secret entry; runner text is captured/suppressed. The helper fills only, so recovery submission, sync choice and account setup remain observable steps. Refuse/fix selectors if necessary before any timed run; do not inject key_material or edit production code. Verify the resulting account-0 Script and normal signing readiness without broadcasting solely to test keys. If runtime UI automation fails, stop at setup and resolve it rather than asking the user to retype the phrase for each arm.

2. **Complete the bounded fixture.** Recreate account 1 normally at `m/44'/309'/1'/0/0`. Use ALL_WALLETS, preserve actual discovery candidate state, and explicitly select correct historical coverage on both accounts. Account 0 starts at **22,369,937**, immediately before first known funding; predecessor transaction resolution needed for fees/input accounting must also succeed. Account 1 starts before its first future funding. If an older relevant event is discovered, revise coverage before timing. Never copy the phone's NEW_WALLET mode or current lightStartBlockNumber as the recovery birthday.

   Preserve original live outpoint `0x2017462e567ea3ad2e24407859fe1164c126af4a0f385d45316e45e7de004d66:0` as U through backup H. Use another existing Cell for setup. A proposed budget is 2,500 CKB to a separately controlled disposable relay actor, then a distinct relay transaction funding account 1 with 2,000 CKB, followed by a 1,000 CKB account-1 DAO deposit. Fees/change are calculated exactly at execution; these are budgets, not signed transactions. Keep relay credentials in private storage, outside the fixture's owned-account discovery range and outside every state package. A new auxiliary relay key may be generated later; it is not a replacement primary recovery wallet and needs no external funding. Separate funding transactions avoid P1's known Room txHash-only/shared-wallet cache ambiguity. Stop with no pending broadcasts or unresolved DAO actions. Record the exact DAO deposit and original header/epoch facts.

3. **Prepare exact observation/acceptance tooling before timing.** Capture exhaustive native owned-Script live outpoints, capacities, covered history/transaction closure, Room account/progress/DAO views, all registration/candidate changes, verified tip and signing readiness. Public RPC/indexer data supplies an independently saved oracle ledger, not acceleration input to either arm. Validate complete pagination and canonical transaction/header facts. The existing package validator alone is not this observer. Preserve coverage and distinguish RPC claims from local verification. Freeze one explicit settled H/hash with both owned Scripts covered and internally consistent native/Room progress.

4. **Create package, then declare loss.** Use WO-2 `h02_device.py export` against the fresh v1.8.5 source. Validate the strict package and separately retain its trusted manifest digest. Retain only its approved non-secret members for B. Record capture time, size and cost separately. Shut down source and seal its directory. From loss time onward neither arm, post-H actor nor acceptance observer may consult the source phone, source emulator, or their private acquisition copies. Already retained keys, package and public ledger are sufficient.

5. **Generate post-H fixture events, then freeze F.** Using the independent actor's pre-retained keys, spend U, create a new incoming Cell on account 1, and perform DAO phase-1 withdrawal of the deposit. Do not create a transaction shared by both owned Script histories. Record all consumed/new outpoints and deposit/withdrawal headers. Wait for confirmed canonical F > H; freeze further fixture activity. Re-baseline on relevant reorganization. Full DAO phase-2 unlock is outside this first experiment.

6. **Run A, then B on their separate fresh profiles.** Start the monotonic timer before first Pocket launch on each prepared clean installation. Recover keys/account 1 with identical normal UI/security/coverage policy. A performs only ordinary local reconstruction. For B, complete normal key/account recovery, freeze/disable, preflight hashes/version/network/genesis/Script mapping, stage approved state into fresh UUID associations, commit, enable and launch. Include ALL transfer, validation, mapping, staging, initial import work, replay and cache reconstruction time. Observe omitted DAO/history caches rebuilding normally. Record peer/network/tip differences between runs; this first pair is feasibility evidence, not a stable speed estimate.

7. **Apply full acceptance and restart.** Both arms must match the two account identities, exact live outpoints and shannons, covered history, DAO withdrawal state, post-H incoming Cell, disappearance of spent U, all native/Room progress through F, and signing readiness. Force-stop/reopen and recheck. Stop the main clock only at persistent acceptance. Record first-correct native state and app state separately. For B, check corrupt/truncated/missing package, wrong genesis/network, unsupported version/schema and interruption refusal without damaging fresh keys. These are safety checks, not additional speed arms. A fast incomplete recovery is FAIL; no speed threshold is invented.

## Ready commands and future inputs

Commands executable now without launching a wallet:

```powershell
Set-Location 'C:/Users/timot/Desktop/2026/CKB/H02-P0'
& runs/wo3-setup/venv/Scripts/python.exe scripts/p3_fixture.py verify
& runs/wo3-setup/venv/Scripts/python.exe scripts/test_p3_fixture.py
python scripts/p3_public_chain.py
```

After PM approval, bootstrap source using the exact boot/enable commands in P2_EMULATOR_READINESS.md. Once its normal phrase-import screen is ready, this command reads the private fixture itself; no phrase/PIN goes into arguments:

```powershell
& runs/wo3-setup/venv/Scripts/python.exe scripts/p3_fill_phrase.py --serial emulator-5580 --apk-sha256 903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f
```

Create each destination AVD independently after stopping the previous role. Example for A, repeated with `candidate` for B, with JAVA_HOME set to the existing Android Studio JBR:

```powershell
$env:JAVA_HOME = 'C:/Program Files/Android/Android Studio/jbr'
$env:ANDROID_AVD_HOME = "$PWD/runs/wo3/control/avd"
if (Test-Path $env:ANDROID_AVD_HOME) { throw 'Role directory already exists; inspect rather than overwrite' }
New-Item -ItemType Directory -Path $env:ANDROID_AVD_HOME | Out-Null
'no' | & "$env:LOCALAPPDATA/Android/Sdk/cmdline-tools/cmdline-tools/bin/avdmanager.bat" create avd --name H02_P0_API36_X64 --package 'system-images;android-36;default;x86_64' --path "$env:ANDROID_AVD_HOME/H02_P0_API36_X64.avd" --device pixel_6
```

Before boot, set/check the same four hardware properties as `scripts/create-avd.ps1`: dataPartition 4G, RAM 2048, cores 2, keyboard yes. Verify actual runtime storage/API/ABI, role path and pristine Pocket sandbox; install only the pinned APK with explicit emulator serial. No snapshots or existing wallet userdata copy.

The future exporter uses trusted TESTNET genesis `0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606`, actual H/hash and per-wallet coverage JSON. Stage/commit use the recorded manifest digest and actual stage token. Follow P2_TOOLING_DESIGN.md commands; do not fill these fields with the historical D2 H or today's arbitrary tip.

## Current decision boundary

Recovery material and deterministic public reproduction: **ready**. Physical fixture acquisition: **complete**, with wallet source bytes unchanged. Secret-entry helper: **compiled, runtime preflight pending**. Second populated account, DAO position, controlled same-version source, post-H events, complete observer, H/F/package: **not yet created**. These are approved-plan prerequisites for the next session, not results or reasons to weaken acceptance.

**GO for PM review of setup. Do not start the timed A/B until PM authorizes this plan and the untimed fixture/automation gates pass.** If UI automation cannot be qualified, exact-state observation is unavailable, or the settled two-account/DAO fixture cannot be established, report BLOCKED before timing. The phone remains an untouched historical reference after its authorized read-only acquisition.
