# CKB Wallet State Recovery

**End-to-end wallet-state recovery research, implemented and validated on Pocket Node.**

Recovering a wallet seed restores control of the keys, but it does not necessarily restore the useful local state a light-client wallet has already built.

This project investigates whether selected non-secret wallet and light-client state can be preserved separately, restored after normal key recovery, and then safely brought forward to the current chain state.

The first end-to-end implementation was tested with Pocket Node 1.8.5 on a real Android phone. Baseline recovery and state-assisted recovery converged to the same canonical CKB state, preserved independent destination-device security, and both successfully signed confirmed testnet transactions.

## The problem and recovery model

Keys establish signing authority. A working wallet also needs account relationships, historical coverage, account discovery, indexed transactions and live Cells, chain checkpoints, and consistent sync progress. Rebuilding this state can require substantial network and local work.

The tested recovery model has three steps:

1. Preserve a coherent, selected saved-state package while the source wallet is settled and stopped. Keep its trusted digest separately.
2. Recover keys and accounts normally on a fresh destination, creating its own PIN, authentication and Android Keystore protection.
3. Match the package to the recovered public identities, restore the permitted state, and let the wallet reconcile it with the chain. Compare exact state and verify signing and restart.

The chain remains authoritative. A saved snapshot can be stale: previously live Cells may have been spent and later transactions may be missing.

## What is preserved

The research package contains a manifest, selected public account/discovery/progress/sync metadata, and a logical snapshot of Pocket's embedded light-client store. Together they preserve prior scanning work and the policy needed to continue it. Application balance, transaction, header and DAO caches are rebuilt on the destination.

The package never transfers a mnemonic, seed, private key, PIN, Android device credential, Android Keystore material, source encrypted key rows, raw wallet backup, or raw source wallet database. Destination signing secrets are created by normal key recovery and remain destination-owned.

## What Pocket proved

An initial emulator proof covered one populated account. A richer proof covered two populated accounts with distinct Scripts, an active DAO deposit, and activity after the saved-state checkpoint. The real Samsung phone proof restored that same unchanged package from x86 to ARM, caught up correctly, signed confirmed transactions through Pocket and genuine Android authentication, and passed cold restart.

The two phone recovery paths matched exact live Cells, balances, covered history, account ownership and canonical DAO position at one common comparison checkpoint. A later state-assisted signing transaction was accounted for explicitly. The observed timings show work avoided in these runs; they are **not a benchmark or a universal speed result**.

## Security boundary and limitations

This is a trusted-self snapshot: integrity checks bind it to a separately trusted digest, but do not independently prove that the source scanned all historical activity. Non-secret account associations still reveal financial privacy. The harness has no encrypted backup or cloud protocol.

The proof covers one pinned Pocket version, a disposable testnet fixture, one Samsung/API-36 phone, and an active DAO deposit. Cross-version migration, other wallets, hostile-source snapshots, extensive reorg testing, and mature DAO withdrawal/unlock were not demonstrated. A pre-existing DAO reward-estimate defect and a separate 16 KB native packaging warning are documented in the proof.

## Status and evaluation

The scoped technical research is complete. This is reference instrumentation and maintainer evidence, **not a finished production wallet feature**. Pocket Node is the proven implementation and testbed. No compatibility with other wallets or ecosystem-standard status is claimed. The tested Pocket recovery path required no separate external recovery layer.

Wallet maintainers can evaluate the idea by identifying their own secret/state boundary, selecting coherent state and compatibility gates, then comparing normal recovery with state-assisted recovery using their own disposable fixture. The [recovery model and tooling guide](docs/how-it-works.md) explains the requirements and what would need integration in a wallet.

To run the retained offline synthetic policy tests from the repository root with Python 3.13 (the validated version):

```powershell
python -m unittest discover -s tests -p "test_state_package.py" -v
python -m unittest discover -s tests -p "test_single_account_profile.py" -v
```

These tests use generated data and require no wallet, device, network or private fixture. The optional Android integration test has separate prerequisites; it is not part of these commands. There is no general end-user recovery CLI or clean-clone replay of the historical phone experiment.

- [How recovery works](docs/how-it-works.md): package, trust, compatibility, reconstruction and retained tools.
- [Pocket proof](docs/pocket-proof.md): experiments, signing, equivalence, timings and limitations.
- [Evidence and provenance](docs/evidence.md): exact pins, digest bindings, historical records and licensing review.
- [Third-party notices](tools/THIRD_PARTY_NOTICES.md): dictionary attribution and upstream license notices.

No repository-wide license has been selected. The provenance review recommends MIT for the original research contributions, subject to the rights holder's approval; third-party notices do not license those contributions.
