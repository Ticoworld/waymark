"""Qualify a settled fresh arm after preserving pre-install Android boot ANRs."""
import argparse
import datetime
import json
import shutil
import time

from h02_device import ROOT
from h02_package import require
from r1_qualify import call, shell


def main(role):
    out = ROOT / "runs/wo3b2" / role / "boot/pre-pocket"
    require(not out.exists(), "qualification-already-exists")
    require(not shell("pm", "path", "com.rjnr.pocketnode", check=False).startswith("package:"), "Pocket-already-installed")
    out.mkdir()
    events = call("logcat", "-d", "-b", "events")
    (out / "boot-events.txt").write_text(events, encoding="utf-8")
    anrs = [x for x in events.splitlines() if "am_anr" in x or "am_crash" in x]
    pid = shell("pidof", "system_server").strip()
    start = time.monotonic()
    rows = []
    for i in range(7):
        if i:
            time.sleep(30)
        settings = shell("am", "start", "-W", "-a", "android.settings.SETTINGS")
        time.sleep(1)
        settings_ok = "Status: ok" in settings and "com.android.settings" in shell("dumpsys", "activity", "activities")
        shell("input", "keyevent", "KEYCODE_HOME")
        time.sleep(1)
        home_ok = "com.android.launcher3" in shell("dumpsys", "activity", "activities")
        current = [x for x in call("logcat", "-d", "-b", "events").splitlines() if "am_anr" in x or "am_crash" in x]
        row = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "elapsed": round(time.monotonic()-start, 2), "settings": settings_ok, "home": home_ok,
               "systemServerUnchanged": pid == shell("pidof", "system_server").strip(),
               "newAnrsOrCrashes": len([x for x in current if x not in anrs]),
               "freeBytes": shutil.disk_usage(ROOT).free}
        rows.append(row)
        print(json.dumps(row), flush=True)
        if not settings_ok or not home_ok or not row["systemServerUnchanged"] or row["newAnrsOrCrashes"]:
            break
    result = {"priorBootAnrs": anrs, "observations": rows,
              "PASS": len(rows) == 7 and all(x["settings"] and x["home"] and x["systemServerUnchanged"] and x["newAnrsOrCrashes"] == 0 for x in rows),
              "PocketNotInstalled": True, "role": role}
    with (out / "stability.json").open("x") as stream:
        json.dump(result, stream, indent=2)
    require(result["PASS"], "settled-android-qualification-failed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("role", choices=("control", "candidate"))
    main(parser.parse_args().role)
