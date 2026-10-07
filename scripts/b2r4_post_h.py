"""One authorized TESTNET account-0 self-transfer after the sealed H2 package.

Consumes exactly one H2-live ordinary Cell. Credentials stay in local process
memory; output is public transaction evidence or a fixed refusal. No Pocket DB
or account metadata is changed. The existing relay handles account-1 activity.
"""
import json
import datetime
from coincurve import PrivateKey, PublicKey
from b2r2_chain import ROOT, URL, GENESIS, SCRIPTS, ARGS, rpc, unhex, raw_tx, ckb_hash, table, blob, u64
from b2r2_observe import native, APK
from b2r2_relay import DEP
from p3_fixture import FIXTURE, derive, verify
import h02_package as p


def main():
    root = ROOT / "runs/wo3b2"
    output = root / "chain-events/post-H2-account0"
    p.require(not output.exists(), "event-already-attempted-reconcile-before-retry")
    p.require(not (root / "source/LOST.json").exists(), "source-already-lost")
    receipt = p.read_json(root / "source/package-receipt.json")
    package = root / "package-H2-immutable"
    manifest, _ = p.validate(package, receipt["manifestSha256"], APK, GENESIS[2:])
    p.require(rpc(URL, "get_block_hash", ["0x0"]) == GENESIS, "wrong-network")
    p.require(int(rpc(URL, "get_tip_header", [])["number"], 16) > manifest["boundary"], "not-after-H2")
    at_h = native(package / "native.sqlite", ARGS[0])
    cells = [c for c in at_h["liveCells"] if c["type"] is None and c["data"] == "0x"]
    cell = min(cells, key=lambda c: (c["blockNumber"], c["txHash"], c["index"]))
    u = {"tx_hash": cell["txHash"], "index": hex(cell["index"])}
    public = rpc(URL, "get_live_cell", [u, True])
    p.require(public["status"] == "live" and public["cell"]["output"]["lock"] == SCRIPTS[0]
              and int(public["cell"]["output"]["capacity"], 16) == cell["capacity"], "U-not-live-as-at-H2")
    amount, fee = 100 * 10**8, 1000
    change = cell["capacity"] - amount - fee
    p.require(change >= 61 * 10**8, "insufficient-change")
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    verify(fixture)
    key = PrivateKey(derive(fixture["wallets"][0]["mnemonic"], "m/44'/309'/0'/0/0"))
    pub = key.public_key.format(compressed=True)
    p.require(ckb_hash(pub)[:20].hex() == ARGS[0], "signer-identity")
    tx = {"version": "0x0", "cell_deps": [{"out_point": {"tx_hash": DEP, "index": "0x0"}, "dep_type": "dep_group"}],
          "header_deps": [], "inputs": [{"since": "0x0", "previous_output": u}],
          "outputs": [{"capacity": hex(n), "lock": SCRIPTS[0], "type": None} for n in (amount, change)],
          "outputs_data": ["0x", "0x"], "witnesses": []}
    tx_hash = ckb_hash(raw_tx(tx))
    empty = table([blob(bytes(65)), b"", b""])
    message = ckb_hash(tx_hash + u64(len(empty)) + empty)
    signature = key.sign_recoverable(message, hasher=None)
    p.require(PublicKey.from_signature_and_message(signature, message, hasher=None).format(compressed=True) == pub, "signature")
    tx["witnesses"] = ["0x" + table([blob(signature), b"", b""]).hex()]
    p.require(sum(int(x["capacity"], 16) for x in tx["outputs"]) + fee == cell["capacity"], "capacity-conservation")
    output.mkdir(parents=True)
    (output / "signed-transaction.json").write_bytes(p.encode(tx))
    attempt = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "network": "TESTNET",
               "H2": manifest["boundary"], "manifestSha256": receipt["manifestSha256"], "U": u,
               "expectedTxHash": "0x" + tx_hash.hex(), "fee": fee, "outputs": tx["outputs"],
               "method": "Local disposable account-0 signer; public-chain self-transfer; no app metadata injection",
               "broadcastAttempted": True}
    (output / "attempt.json").write_bytes(p.encode(attempt))
    returned = rpc(URL, "send_transaction", [tx, "passthrough"])
    p.require(returned == attempt["expectedTxHash"], "broadcast-hash")
    attempt["returnedTxHash"] = returned
    (output / "broadcast.json").write_bytes(p.encode(attempt))
    print(json.dumps(attempt, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("POST_H_ACCOUNT0_REFUSED " + type(e).__name__ + "; inspect retained public attempt before retry")
        raise SystemExit(2)
