# WO07-R5A: Neuron Startup Resolution

Date: 31 October 2026

## Verdict

**STARTUP CAUSE IDENTIFIED, CORRECTION BLOCKED.** The launch environment currently sets `ELECTRON_RUN_AS_NODE=1`. Electron documents that this variable starts the process as ordinary Node.js when the executable's `runAsNode` fuse permits it. That behavior is a strong explanation for the prior clean exit without a window, but the exact previous launch was not reproduced with the variable removed, and the executable's fuse state was not decoded. The controlled launch request for the temporary app copy was rejected by the execution environment before it ran.

No unmodified Neuron release was launched, no OS-level isolated runtime was established, and no disposable wallet was created. The installed application and its profile were not opened or changed.

## Startup diagnosis

- At inspection, this PowerShell process had `ELECTRON_RUN_AS_NODE=1`; the user and machine environment-variable stores did not define it. Its source is therefore the parent execution environment, not a persistent Windows setting.
- No Neuron or Electron process was running during inspection. This makes a currently running Neuron instance an unlikely explanation for the earlier exit, but does not rule out an earlier process or a stale single-instance lock. The user's Neuron profile and lock files were not inspected.
- No matching Neuron/Electron Application Error, Windows Error Reporting, or SideBySide event was found in the recent Application log window.
- Electron's official environment-variable documentation says `ELECTRON_RUN_AS_NODE` starts the process as normal Node.js, unless the `runAsNode` fuse is disabled. A plain Node process can exit successfully without loading Neuron's Electron main process. This matches the observed exit shape, but remains conditional on the Neuron executable's fuse.
- The installed executable was not modified. Its SHA-256 remains the previously recorded `74abd9a83cf3a4bfbfb70d6edca49c12d73dc8f272f219ea56dfde9f5f50cc18`.
- The installed `app.asar` SHA-256 is `ef42a37d28bebd729b4703266e1733315e3aa0605e66d8df6d92ee83c4a251bb`; the temporary patched archive is `f589cedbbcb296a93c6f3badb6bec171a1d3197277caa326d787d1a403de817e`. The changed archive is not evidence that ASAR integrity caused the exit. Electron only terminates for embedded ASAR-integrity mismatch when that fuse is enabled. The executable's fuse settings were not verified, and the patched copy was not successfully relaunched to test it.
- The temporary app copy contains all 79 files in the installed release tree. It contains one additional generated file, `resources/app.asar.patched`. Total tree sizes were approximately 0.426 GB installed and 0.506 GB copied. No missing runtime assets were found by the tree comparison.
- Windows Sandbox is not present at `%WINDIR%\System32\WindowsSandbox.exe`. Querying Windows optional-feature state failed because the operation requires elevation. The machine reports a hypervisor and has Docker installed, but no already-available isolated interactive Windows runtime was established. No feature was enabled, system account created, or security setting changed.

The only attempted controlled relaunch in this work order targeted the patched temporary copy with `ELECTRON_RUN_AS_NODE` removed from that child process. The execution environment rejected the process-start request before execution. Thus there is no new app startup trace, ASAR integrity result, window, or Electron main-entry evidence. The previous `--enable-logging` attempt remains inconclusive because the app wrapper rejected the argument.

## Isolation and wallet result

The earlier R5 temp profile remains separate from the existing Neuron profile, but changing Electron `userData` in a patched app is not equivalent to proving OS-level isolation. No wallet was opened or created in R5A. There is no wallet UUID, public Script, TESTNET activity, or restart-persistence result to report.

No user profile directory, wallet file, database, key, mnemonic, password, or xpub was read. No TESTNET sync or transaction occurred. No Neuron, D2, Pocket, or Waymark source was modified in this work order.

## Resource use

C: had `5,990,932,480` bytes free (5.579 GiB as reported by PowerShell) at the final check, above the 4 GB reserve. R5A did not install dependencies, build software, download chain data, or write a new runtime. The rejected process launch created no logs. Existing temp files from R5 were left intact.

## Smallest next action

Run the unmodified Neuron v0.204.1 release in an already enabled, interactive OS isolation environment. First confirm that the environment's effective `ELECTRON_RUN_AS_NODE` is unset and that the app's own `userData` resolves inside that environment. Windows Sandbox is not available in the current non-elevated session; enabling it would require an authorized system-level change. A dedicated test account or virtualization setup likewise requires separate authorization and is not attempted here.

If an isolated runtime becomes available, launch the unmodified release, confirm a window and an isolated TESTNET Light Client profile, create a disposable wallet through Neuron's normal UI, record only its generated UUID and public account-0 Script, and restart the app to verify persistence. Do not resume D2 export or application replay until that boundary passes.

## References

- Electron [environment variables](https://www.electronjs.org/docs/latest/api/environment-variables): `ELECTRON_RUN_AS_NODE` starts a process as ordinary Node; behavior depends on the `runAsNode` fuse.
- Electron [fuses](https://www.electronjs.org/docs/latest/tutorial/fuses): the `runAsNode` fuse controls whether that variable is honored; embedded ASAR validation is a separate fuse.
- Electron [ASAR integrity](https://www.electronjs.org/docs/latest/tutorial/asar-integrity): when enabled, a missing or mismatched archive header hash causes termination.
- Electron [app API](https://www.electronjs.org/docs/latest/api/app): `userData` defaults under the per-user app-data directory and can be overridden before `ready`; a path override alone is not OS isolation.
