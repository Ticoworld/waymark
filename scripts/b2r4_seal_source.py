"""Bind the final public oracle, stop SOURCE, and seal compact R4 evidence.

No new transaction, credential access, DB export, or runtime deletion. The
separate exact-path retirement wrapper consumes this verified evidence seal.
"""
import datetime
import json
import subprocess
import time

import h02_device as d
import h02_package as p
from b2r2_chain import URL, GENESIS, SCRIPTS, rpc
from b2r2_observe import APK, native


def main():
    root = d.ROOT / "runs/wo3b2"
    source = root / "source"
    p.require(not (source / "LOST.json").exists(), "already-lost")
    p.require(not (root / "final-boundary.json").exists(), "final-boundary-already-recorded")
    receipt = p.read_json(source / "package-receipt.json")
    package = root / "package-H2-immutable"
    p.validate(package, receipt["manifestSha256"], APK, GENESIS[2:])
    h = receipt["H2"]
    p.require(rpc(URL, "get_block_hash", [hex(h)]) == receipt["H2Hash"], "H2-no-longer-canonical")
    before = p.read_json(root / "oracle-H2.json")
    final = p.read_json(root / "oracle-F2.json")
    f = int(final["tip"]["number"], 16)
    p.require(rpc(URL, "get_block_hash", [hex(f)]) == final["tip"]["hash"], "F2-no-longer-canonical")
    p.require(int(final["indexerTip"]["block_number"], 16) >= f, "indexer-behind-F2")
    events = []
    for i in (0, 1):
        event_dir = root / "chain-events" / ("post-H2-account" + str(i))
        event = p.read_json(event_dir / "broadcast.json")
        txhash = event["expectedTxHash"]
        a = final["accounts"][i]
        old = before["accounts"][i]
        p.require(a["index"] == old["index"] == i and a["script"] == old["script"] == SCRIPTS[i], "oracle-account-map")
        tx = a["transactionDetails"][txhash]
        public = rpc(URL, "get_transaction", [txhash])
        p.require(tx == public and public["tx_status"]["status"] == "committed", "event-not-canonical")
        block = int(tx["tx_status"]["block_number"], 16)
        p.require(h < block <= f, "event-outside-H2-F2")
        p.require(rpc(URL, "get_block_hash", [hex(block)]) == tx["tx_status"]["block_hash"], "event-reorg")
        p.require(a["transactions"] == sorted(old["transactions"] + [txhash]), "unexpected-final-history")
        p.require(txhash not in final["accounts"][1-i]["transactions"], "cross-account-event")
        if i == 0:
            u = event["U"]
            at_h = native(package / "native.sqlite")
            p.require(any(c["txHash"] == u["tx_hash"] and c["index"] == int(u["index"], 16) for c in at_h["liveCells"]), "U-not-in-package")
            p.require([x["previous_output"] for x in tx["transaction"]["inputs"]] == [u], "wrong-U-spend")
            spent = rpc(URL, "get_live_cell", [u, True])
            # This node returns `unknown` for a consumed outpoint. Its canonical
            # confirmed spend, indexer absence, and non-live RPC result jointly
            # establish consumption; `unknown` alone would not suffice.
            p.require(spent["status"] in ("dead", "unknown") and spent["cell"] is None, "U-still-live")
            p.require(all(o["lock"] == SCRIPTS[0] and o["type"] is None for o in tx["transaction"]["outputs"]), "wrong-owned-replacement")
            p.require(a["capacity"] == old["capacity"] - event["fee"], "account0-capacity")
            p.require(not any(c["out_point"] == u for c in a["liveCells"]), "U-in-final-oracle")
        else:
            p.require(a["capacity"] == old["capacity"] + event["amount"], "account1-capacity")
        new = [c for c in a["liveCells"] if c["out_point"]["tx_hash"] == txhash]
        p.require(len(new) == (2 if i == 0 else 1), "new-live-output-count")
        for cell in new:
            p.require(rpc(URL, "get_live_cell", [cell["out_point"], True])["status"] == "live", "new-output-not-live")
        confirmed = {"accountIndex": i, "transactionHash": txhash, "confirmationHeight": block,
                     "confirmationHash": tx["tx_status"]["block_hash"], "newOwnedLiveCells": new}
        if i == 0:
            confirmed.update({"U": u, "spentU": spent, "UWasLiveInImmutableH2": True,
                              "consumptionProof": "Canonical confirmed transaction consumes U; U absent from final live index; get_live_cell is non-live"})
        with (event_dir / "confirmation.json").open("xb") as stream:
            stream.write(p.encode(confirmed))
        events.append(confirmed)
    dao_before = [c for c in before["accounts"][1]["liveCells"] if c["output"]["type"] is not None]
    dao_final = [c for c in final["accounts"][1]["liveCells"] if c["output"]["type"] is not None]
    p.require(dao_before == dao_final and len(dao_final) == 1, "DAO-position-changed")
    boundary = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "H2": h,
                "H2Hash": receipt["H2Hash"], "F2": f, "F2Hash": final["tip"]["hash"],
                "oracleSha256": p.sha(root / "oracle-F2.json"), "events": events,
                "daoPostH2Transition": "NOT_TESTED", "fixtureActivityFrozen": True}
    with (root / "final-boundary.json").open("xb") as stream:
        stream.write(p.encode(boundary))

    # Verify the currently running emulator belongs to the retained SOURCE.
    query = "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'qemu-system*' } | Select-Object -ExpandProperty CommandLine"
    raw = subprocess.run(["powershell", "-NoProfile", "-Command", query], capture_output=True, text=True, check=True).stdout.replace("\\", "/").lower()
    expected = str((source / "avd").resolve()).replace("\\", "/").lower()
    p.require(expected in raw and "-gpu host" in raw, "wrong-running-source")
    device = d.Device("emulator-5580", APK)
    device.freeze()
    device.call("emu", "kill")
    for _ in range(30):
        raw = subprocess.run(["powershell", "-NoProfile", "-Command", query], capture_output=True, text=True, check=True).stdout.replace("\\", "/").lower()
        if expected not in raw:
            break
        time.sleep(1)
    else:
        raise p.Refused("source-process-still-live")
    accepted = p.read_json(source / "r4-H2-canonical-acceptance.json")
    restart = [json.loads(x) for x in (source / "r4-restart-watch.jsonl").read_text().splitlines()]
    p.require(accepted["result"] == "PASS" and len(restart) >= 2, "source-acceptance-incomplete")
    p.require(all("\u2713 Synced" in r["publicStatus"] for r in restart[-2:]), "source-restart-not-settled")
    files = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if not path.is_file() or "avd" in rel.parts:
            continue
        files.append({"path": str(path.relative_to(d.ROOT)).replace("\\", "/"), "bytes": path.stat().st_size, "sha256": p.sha(path)})
    seal = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "role": "source",
            "accepted": True, "restartPassed": True, "sourceStopped": True,
            "H2": h, "F2": f, "manifestSha256": receipt["manifestSha256"], "files": files,
            "knownDaoDefect": "61 CKB reader estimate; canonical occupied capacity 102 CKB; PM-approved R3 contract"}
    with (source / "evidence-seal-r4.json").open("xb") as stream:
        stream.write(p.encode(seal))
    lost = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "sourceStopped": True,
            "sourceRuntime": "runs/wo3b2/source/avd/H02_P0_API36_X64.avd", "H2": h, "F2": f,
            "evidenceSealSha256": p.sha(source / "evidence-seal-r4.json"),
            "allowedInputsAfterLoss": ["private fixture", "immutable sanitized H2 package", "previously recorded public oracle", "public chain observations"],
            "sourceGuestQueriesForbidden": True}
    with (source / "LOST.json").open("xb") as stream:
        stream.write(p.encode(lost))
    print(json.dumps({"SOURCE_LOST": True, "H2": h, "F2": f, "F2Hash": boundary["F2Hash"],
                      "spentU": "confirmed-consumed/non-live", "events": [e["transactionHash"] for e in events], "sealedFiles": len(files)}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("R4_SOURCE_SEAL_REFUSED " + type(e).__name__ + (" " + str(e) if isinstance(e, p.Refused) else ""))
        raise SystemExit(2)
