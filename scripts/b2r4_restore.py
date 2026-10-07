"""Approved package stage/activation with explicit H2-staleness proof before launch."""
import argparse
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import h02_device as d
import h02_package as p
from b2_events import mark
from b2r2_observe import APK, GENESIS, capture
from b2r4_resume import resume


def main(package, trust):
    root = d.ROOT / "runs/wo3b2"
    role = "candidate"
    p.require((root / "source/LOST.json").exists(), "source-not-lost")
    launch = json.loads((root / role / "boot/launch.json").read_text(encoding="utf-8-sig"))
    p.require(launch["role"] == role, "wrong-role-record")
    query = "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'qemu-system*' } | Select-Object -ExpandProperty CommandLine"
    raw = subprocess.run(["powershell", "-NoProfile", "-Command", query], capture_output=True, text=True, check=True).stdout.replace("\\", "/").lower()
    p.require(str((root / role / "avd").resolve()).replace("\\", "/").lower() in raw and "-gpu host" in raw, "wrong-running-role")
    a = SimpleNamespace(package=str(package), trust=trust, apk_sha256=APK, genesis=GENESIS, serial="emulator-5580")
    d.HELPER = d.ROOT / "runs/wo3b2-r2/state-helper/helper.jar"
    event = lambda name: mark(role, name)
    event("package_restore_begin")
    token = d.stage(a, event)
    a.token, a.action = token, "commit"
    event("activation_begin")
    d.activate(a)
    event("activation_complete")
    device = d.Device(a.serial, APK)
    manifest = p.read_json(package / "manifest.json")
    digest = device.sandbox("sha256sum", d.REMOTE_ROOT + "/files/data/testnet/store.db").decode().split()[0]
    p.require(digest == manifest["files"]["native.sqlite"]["sha256"], "activated-native-digest-mismatch")
    receipt = {"packageManifest": trust, "activatedNativeDigest": digest, "stageToken": token,
               "normalDestinationKeysPreservedByHelper": True}
    with (root / role / "activation-receipt.json").open("xb") as stream:
        stream.write(p.encode(receipt))
    capture("candidate/r4-restored-H2")
    observation = p.read_json(root / role / "r4-restored-H2/summary.json")
    boundary = p.read_json(root / "final-boundary.json")
    u = boundary["events"][0]["U"]
    p.require(any(c["txHash"] == u["tx_hash"] and c["index"] == int(u["index"], 16)
                  for c in observation["accounts"][0]["liveCells"]), "U-not-restored-live")
    for i, e in enumerate(boundary["events"]):
        p.require(e["transactionHash"] not in observation["accounts"][i]["transactions"], "post-H2-event-already-in-restored-state")
    p.require(p.sha(root / role / "r4-restored-H2/native.sqlite") == digest, "prelaunch-native-capture-changed")
    proof = {"result": "PASS", "U": u, "UObservedLiveAfterActivation": True,
             "postH2TransactionsAbsentBeforeLaunch": True, "manifestSha256": trust,
             "nativeSha256": digest, "summarySha256": p.sha(root / role / "r4-restored-H2/summary.json"),
             "cacheRowsBeforeLaunch": {"dao": observation["room"]["daoCount"],
                                       "balances": len(observation["room"]["balances"]),
                                       "transactions": len(observation["room"]["transactions"])} }
    with (root / role / "restored-stale-proof.json").open("xb") as stream:
        stream.write(p.encode(proof))
    event("package_restore_complete")
    event("light_client_launch_requested")
    resume()
    event("restored_app_unlocked")
    print("CANDIDATE_H2_STALENESS_PROVED_AND_NORMAL_CATCHUP_STARTED", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--trust", required=True)
    args = parser.parse_args()
    try:
        main(args.package, args.trust)
    except Exception as e:
        print("R4_RESTORE_REFUSED " + type(e).__name__ + (" " + str(e) if isinstance(e, p.Refused) else ""), flush=True)
        raise SystemExit(2)
