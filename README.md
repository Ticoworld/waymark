# Waymark

**Wallet-state recovery for CKB, first validated on Pocket Node.**

Recovering a wallet seed restores control of the keys, but it does not restore all of the useful local state a light-client wallet may have already built.

Waymark explores a simple recovery model: restore ownership normally, restore selected non-secret wallet/light-client state separately, then let the wallet catch up to the current chain. A waymark is a known point on a journey; here, it is the saved historical checkpoint from which the wallet continues.

The approach was validated end-to-end on Pocket Node 1.8.5 on a real Android phone. Baseline recovery and state-assisted recovery converged to the same canonical CKB state, preserved independent destination-device security, and both signed confirmed testnet transactions. The saved state does not replace the recovery phrase: **source-device signing secrets and Android Keystore material are never transferred**.

## How it works

Keys establish signing authority. A working wallet also needs account relationships, historical coverage, account discovery, indexed transactions and live Cells, chain checkpoints, and consistent sync progress. Rebuilding this state can require substantial network and local work.

The tested recovery model has three steps:

1. Preserve a coherent, selected saved-state package while the source wallet is settled and stopped. Keep its trusted digest separately.
2. Recover keys and accounts normally on a fresh destination, creating its own PIN, authentication and Android Keystore protection.
3. Match the package to the recovered public identities, restore the permitted state, and let the wallet reconcile it with the chain. Compare exact state and verify signing and restart.

The chain remains authoritative. A saved snapshot can be stale: previously live Cells may have been spent and later transactions may be missing.

## What is preserved

The research package contains a manifest, selected public account/discovery/progress/sync metadata, and a logical snapshot of Pocket's embedded light-client store. Together they preserve prior scanning work and the policy needed to continue it. Application balance, transaction, header and DAO caches are rebuilt on the destination.

The package never transfers a mnemonic, seed, private key, PIN, Android device credential, Android Keystore material, source encrypted key rows, raw wallet backup, or raw source wallet database. Destination signing secrets are created by normal key recovery and remain destination-owned.

## Pocket Node proof

An initial emulator proof covered one populated account. A richer proof covered two populated accounts with distinct Scripts, an active DAO deposit, and activity after the saved-state checkpoint. The real Samsung phone proof restored that same unchanged package from x86 to ARM, caught up correctly, signed confirmed transactions through Pocket and genuine Android authentication, and passed cold restart.

The two phone recovery paths matched exact live Cells, balances, covered history, account ownership and canonical DAO position at one common comparison checkpoint. A later state-assisted signing transaction was accounted for explicitly. The observed timings show work avoided in these runs; they are **not a benchmark or a universal speed result**.

## Security model

This is a trusted-self snapshot: integrity checks bind it to a separately trusted digest, but do not independently prove that the source scanned all historical activity. Non-secret account associations still reveal financial privacy. The harness has no encrypted backup or cloud protocol.

## Repository contents and evaluation

- [How it works](docs/how-it-works.md): package, trust boundary, compatibility checks, destination reconstruction and tooling prerequisites.
- [Pocket proof](docs/pocket-proof.md): recovery, signing, restart, equivalence, timings and separate upstream observations.
- [Evidence](docs/evidence.md): exact source pins, artifact and transaction hashes, digest bindings and historical traceability.
- `tools/`: the strict package validator, emulator sandbox transport, standalone Android helper and its build wrapper, plus the BIP39 reference dictionary.
- `tests/`: generated policy fixtures and an optional Android integration driver.

To run the retained offline synthetic policy tests from the repository root with Python 3.13 (the validated version):

```powershell
python -m unittest discover -s tests -p "test_state_package.py" -v
python -m unittest discover -s tests -p "test_single_account_profile.py" -v
```

These commands need no wallet, device, network or private fixture. Inspect the existing tools with `python tools/state_package.py --help` and `python tools/pocket_sandbox.py --help`. Android compilation and optional integration have separate prerequisites in [the tooling guide](docs/how-it-works.md). There is no general end-user recovery CLI or clean-clone replay of the historical phone experiment.

Wallet maintainers can evaluate the idea by identifying their own secret/state boundary and compatibility gates, then comparing normal and state-assisted recovery with a disposable fixture, later chain activity, exact canonical state, signing and restart.

## Status and limitations

Waymark's scoped technical research is complete. Pocket Node is the proven implementation and testbed; this is reference instrumentation and maintainer evidence, **not a finished production wallet feature**. Neuron, iBytes and other CKB wallets have not been validated. No compatibility with other wallets or ecosystem-standard status is claimed. The tested Pocket path required no separate external recovery layer.

The proof covers one pinned version, a disposable testnet fixture, two accounts, one Samsung/API-36 phone, and an active DAO deposit. Cross-version migration, other wallets, hostile-source snapshots, extensive reorg testing, and mature DAO withdrawal/unlock were not demonstrated. The proof documents a pre-existing DAO reward-estimate defect and a separate 16 KB native packaging warning.

## License

Original project contributions are licensed under the [MIT License](LICENSE), copyright 2026 Timothy. The copied BIP39 dictionary retains its required attribution and upstream MIT notice in [third-party notices](tools/THIRD_PARTY_NOTICES.md).
