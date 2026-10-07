"""Continue supported account UI after a verified creation; never inject rows."""
import argparse
import json
import time
import xml.etree.ElementTree as ET

import h02_package as p
from h02_device import ROOT
from p3b1_ui import device, nodes, tap as normal_tap
from r2_public_tap import tap
from b2r2_account import create
from b2r2_coverage import set_floor
from b2_events import mark


def created(role):
    path = ROOT / "runs/wo3b2" / role / "events.jsonl"
    return path.exists() and any(json.loads(x)["event"] == "account1_created_and_identity_verified" for x in path.read_text().splitlines())


def continue_switch(role):
    p.require(created(role), "account1-creation-not-proven")
    d = device()
    # The failed helper leaves Home with the public account selector closed.
    p.require(any(n.attrib.get("content-desc") == "Switch" for n in nodes(d)), "not-on-public-home")
    for label, suffix in (("ckt1qzda0c...7rmyth", "myth"), ("B2 Account 1", "pweu")):
        normal_tap(d, "Switch")
        time.sleep(1)
        tap(public_text=label)
        time.sleep(5)
        p.require(any(n.attrib.get("text") == "ckt1qz..." + suffix for n in nodes(d)), "account-switch-not-refreshed")
    set_floor(1)
    mark(role, "account1_custom_registration_requested")


def receipt(role):
    d = device()
    root = ET.fromstring(d.sandbox("cat", "shared_prefs/ckb_wallet_prefs.xml"))
    values = {e.attrib["name"]: e.text if e.tag == "string" else e.attrib.get("value")
              for e in root if e.attrib.get("name", "").endswith(("_testnet_sync_mode", "_testnet_custom_block_height"))}
    starts = [int(v) for k, v in values.items() if k.endswith("_custom_block_height")]
    modes = [v for k, v in values.items() if k.endswith("_sync_mode")]
    p.require(sorted(starts) == [22369937, 22647000] and modes == ["CUSTOM", "CUSTOM"], "two-account-coverage-policy")
    result = {"result": "PASS", "publicCoveragePreferences": values,
              "scope": "Allowlisted preferences only; exact UUID/account association checked by final canonical gate"}
    with (ROOT / "runs/wo3b2" / role / "r4-coverage-receipt.json").open("xb") as stream:
        stream.write(p.encode(result))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("role", choices=("control", "candidate"))
    parser.add_argument("--receipt-only", action="store_true")
    args = parser.parse_args()
    try:
        if not args.receipt_only:
            if not created(args.role):
                try:
                    create(args.role)
                except Exception:
                    p.require(created(args.role), "account-creation-automation-failed")
                    mark(args.role, "post_creation_switch_automation_refused")
                    continue_switch(args.role)
            else:
                continue_switch(args.role)
        receipt(args.role)
    except Exception as e:
        print("R4_ACCOUNT_REFUSED " + type(e).__name__ + (" " + str(e) if isinstance(e, p.Refused) else ""))
        raise SystemExit(2)
