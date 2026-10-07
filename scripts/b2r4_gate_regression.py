"""Regression of the revised gate against copied public SOURCE observations."""
import json
from unittest.mock import patch
import h02_package as p
from h02_device import ROOT
from b2r4_acceptance import check
import b2r4_export


def main():
    base = ROOT / "runs/wo3b2"
    obs = base / "source/r4-first-settled"
    oracle = base / "oracle-r4-before-resume.json"
    audit = base / "source/r4-first-dao-audit.json"
    out = ROOT / "runs/wo3b2-r4/gate-regression"
    out.mkdir(exist_ok=False)
    p.require(check(obs, oracle, 22652417, audit)["result"] == "PASS", "known-defect-not-accepted")
    results = [{"case": "canonical-position-with-known-reader-defect", "accepted": True}]
    for case in ("wrong-dao-owner", "cross-account-script", "wrong-dao-stage", "new-compensation",
                 "stale-estimate", "wrong-parent-mapping"):
        folder = out / case
        folder.mkdir()
        summary = p.read_json(obs / "summary.json")
        app = p.read_json(obs / "app.json")
        a = p.read_json(audit)
        if case == "wrong-dao-owner":
            summary["room"]["daoCells"][0]["walletId"] = summary["wallets"][0]["walletId"]
        elif case == "cross-account-script":
            summary["accounts"][1]["script"] = summary["accounts"][0]["script"]
        elif case == "wrong-dao-stage":
            summary["room"]["daoCells"][0]["status"] = "UNLOCKABLE"
        elif case == "new-compensation":
            summary["room"]["daoCells"][0]["compensation"] += 1
            a["observedCompensation"] += 1
        elif case == "stale-estimate":
            a["cacheAgeAtCaptureMs"] = 180001
        elif case == "wrong-parent-mapping":
            app["wallets"][1]["parentWalletId"] = app["wallets"][1]["walletId"]
        (folder / "summary.json").write_bytes(p.encode(summary))
        (folder / "app.json").write_bytes(p.encode(app))
        a["summarySha256"] = p.sha(folder / "summary.json")
        a["observation"] = str(folder.resolve())
        (folder / "audit.json").write_bytes(p.encode(a))
        try:
            check(folder, oracle, 22652417, folder / "audit.json")
        except p.Refused as e:
            results.append({"case": case, "rejected": True, "gate": str(e)})
        else:
            raise AssertionError("gate accepted mutation")
    with patch.object(b2r4_export, "rpc", side_effect=AssertionError("RPC before source gate")), \
         patch.object(b2r4_export.d, "Device", side_effect=AssertionError("ADB before source gate")):
        bad = out / "wrong-dao-owner"
        try:
            b2r4_export.main(bad, oracle, bad / "audit.json")
        except p.Refused:
            results.append({"case": "invalid-source-refused-before-export-side-effects", "rejected": True})
        else:
            raise AssertionError("export gate accepted mutation")
    (out / "result.json").write_bytes(p.encode({"result": "PASS", "cases": results}))
    print(json.dumps({"result": "PASS", "cases": results}, indent=2))


if __name__ == "__main__":
    main()
