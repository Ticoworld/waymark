"""Canonical F2 acceptance, two-account signing readiness and ordinary restart.

Uses only this arm, retained public oracle and public chain observations. Never
opens SOURCE or CONTROL databases. A failure leaves the current arm retained.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import h02_package as p
from h02_device import ROOT
from b2r2_observe import capture
from b2r2_reconcile import capture as reconcile
from b2r2_signing import check as signing
from b2r4_resume import resume
from b2r4_acceptance import audit, check
from b2_events import mark

BASE = ROOT / "runs/wo3b2"


def verify_role(role):
    p.require((BASE / "source/LOST.json").exists(), "source-not-lost")
    query = "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'qemu-system*' } | Select-Object -ExpandProperty CommandLine"
    raw = subprocess.run(["powershell", "-NoProfile", "-Command", query], capture_output=True,
                         text=True, check=True).stdout.replace("\\", "/").lower()
    p.require(str((BASE / role / "avd").resolve()).replace("\\", "/").lower() in raw
              and "-gpu host" in raw, "wrong-running-role")


def frozen_accept(role, label, boundary):
    reconcile(role + "/" + label + "-ui.json")
    signing(role + "/" + label + "-signing.json")
    mark(role, label + "_freeze_begin")
    observation = BASE / role / label
    capture(role + "/" + label)
    auditfile = BASE / role / (label + "-dao-audit.json")
    audit(observation, BASE / "oracle-F2.json", auditfile)
    result = check(observation, BASE / "oracle-F2.json", boundary, auditfile)
    target = BASE / role / (label + "-acceptance.json")
    with target.open("xb") as f:
        f.write(p.encode(result))
    mark(role, label + "_exact_acceptance_pass")
    print("EXACT_F2_ACCEPTANCE_PASS " + result["semanticSha256"], flush=True)
    return result


def run(role, attempt="r4"):
    import re
    p.require(re.fullmatch(r"r4(?:-[a-z0-9]+)?", attempt) is not None, "invalid-attempt-label")
    verify_role(role)
    f = p.read_json(BASE / "final-boundary.json")["F2"]
    first_label, restart_label = attempt + "-first", attempt + "-restart"
    first = frozen_accept(role, first_label, f)
    mark(role, "restart_begin")
    resume()
    mark(role, "restart_unlocked")
    label = role + "/" + attempt + "-restart-watch.jsonl"
    subprocess.run([sys.executable, "-u", str(ROOT / "scripts/b2r2_watch.py"),
                    "--label", label, "--seconds", "1800", "--until-synced", "--minimum", str(f)],
                   cwd=ROOT, check=True)
    rows = [json.loads(x) for x in (BASE / label).read_text().splitlines()]
    p.require(len(rows) >= 2 and all("\u2713 Synced" in row["publicStatus"]
              and (row.get("nativeLastLoggedMinimum") or 0) >= f for row in rows[-2:]), "restart-not-settled")
    second = frozen_accept(role, restart_label, f)
    p.require(first["semanticSha256"] == second["semanticSha256"], "restart-semantic-divergence")
    end = mark(role, "full_acceptance_complete")
    events = [json.loads(x) for x in (BASE / role / "events.jsonl").read_text().splitlines()]
    start = next(x for x in events if x["event"] == "first_launch_begin")
    result = {"role": role, "result": "PASS", "restart": "PASS", "signingReadiness": "PASS",
              "canonicalSemanticSha256": second["semanticSha256"], "F2": f,
              "knownCompensationDefectOnly": True, "recoverySpecificDaoDivergence": False,
              "totalSeconds": end["monotonic"] - start["monotonic"], "end": end,
              "pocketLeftDisabled": True, "contract": second["contract"],
              "firstObservation": first_label, "restartObservation": restart_label}
    with (BASE / role / "result.json").open("xb") as stream:
        stream.write(p.encode(result))
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("role", choices=("control", "candidate"))
    parser.add_argument("--attempt", default="r4")
    args = parser.parse_args()
    try:
        run(args.role, args.attempt)
    except Exception as e:
        print("R4_ARM_REFUSED " + type(e).__name__ + (" " + str(e) if isinstance(e, p.Refused) else ""), flush=True)
        raise SystemExit(2)
