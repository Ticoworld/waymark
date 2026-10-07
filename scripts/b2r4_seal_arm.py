"""Seal a fully accepted arm and stop its emulator; do not delete runtime files."""
import argparse
import datetime
import json
import subprocess
import time

import h02_device as d
import h02_package as p
from b2r2_observe import APK
from b2r4_acceptance import check


def main(role):
    base = d.ROOT / "runs/wo3b2"
    folder = base / role
    p.require((base / "source/LOST.json").exists(), "source-not-lost")
    p.require(not (folder / "evidence-seal-r4.json").exists(), "already-sealed")
    result = p.read_json(folder / "result.json")
    p.require(result["result"] == result["restart"] == result["signingReadiness"] == "PASS", "arm-incomplete")
    f = p.read_json(base / "final-boundary.json")["F2"]
    for label in (result["firstObservation"], result["restartObservation"]):
        accepted = check(folder / label, base / "oracle-F2.json", f, folder / (label + "-dao-audit.json"))
        p.require(accepted["semanticSha256"] == result["canonicalSemanticSha256"], "semantic-result-mismatch")
        p.require(p.read_json(folder / (label + "-signing.json"))["result"] == "PASS", "signing-incomplete")
    query = "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'qemu-system*' } | Select-Object -ExpandProperty CommandLine"
    expected = str((folder / "avd").resolve()).replace("\\", "/").lower()
    raw = subprocess.run(["powershell", "-NoProfile", "-Command", query], capture_output=True, text=True, check=True).stdout.replace("\\", "/").lower()
    p.require(expected in raw and "-gpu host" in raw, "wrong-running-arm")
    device = d.Device("emulator-5580", APK)
    device.freeze()
    device.call("emu", "kill")
    for _ in range(30):
        raw = subprocess.run(["powershell", "-NoProfile", "-Command", query], capture_output=True, text=True, check=True).stdout.replace("\\", "/").lower()
        if expected not in raw:
            break
        time.sleep(1)
    else:
        raise p.Refused("arm-process-still-live")
    files = []
    for path in sorted(folder.rglob("*")):
        if path.is_file() and "avd" not in path.relative_to(folder).parts:
            files.append({"path": str(path.relative_to(d.ROOT)).replace("\\", "/"),
                          "bytes": path.stat().st_size, "sha256": p.sha(path)})
    for path in (base / "oracle-F2.json", base / "final-boundary.json"):
        files.append({"path": str(path.relative_to(d.ROOT)).replace("\\", "/"),
                      "bytes": path.stat().st_size, "sha256": p.sha(path)})
    seal = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "role": role,
            "accepted": True, "restartPassed": True, "emulatorStopped": True,
            "F2": f, "semanticSha256": result["canonicalSemanticSha256"], "files": files}
    with (folder / "evidence-seal-r4.json").open("xb") as stream:
        stream.write(p.encode(seal))
    print(json.dumps({"role": role, "accepted": True, "emulatorStopped": True, "filesSealed": len(files),
                      "semanticSha256": seal["semanticSha256"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("role", choices=("control", "candidate"))
    try:
        main(parser.parse_args().role)
    except Exception as e:
        print("R4_ARM_SEAL_REFUSED " + type(e).__name__ + (" " + str(e) if isinstance(e, p.Refused) else ""))
        raise SystemExit(2)
