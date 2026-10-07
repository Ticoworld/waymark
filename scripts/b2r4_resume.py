"""Ordinary Pocket restart/authentication with a bounded public startup wait."""
import time
from types import SimpleNamespace

from h02_device import Device, APP, enable
from h02_package import Refused
from p3b1_ui import nodes
from r2_public_tap import APK, tap
from r2_pin import main as pin


def resume():
    d = Device("emulator-5580", APK)
    d.freeze()
    enable(SimpleNamespace(serial=d.serial, apk_sha256=APK))
    d.shell("am", "start", "-n", APP + "/.MainActivity")
    print("POCKET_PUBLIC_START_REQUESTED", flush=True)
    start = time.monotonic()
    while time.monotonic() - start < 60:
        # This precedes PIN entry and observes only the public locked/start UI.
        try:
            if any(n.attrib.get("resource-id") == "auth-use-pin" for n in nodes(d)):
                break
        except Refused as e:
            if str(e) != "adb-operation-refused":
                raise
        print("Waiting for Pocket public authentication UI", flush=True)
        time.sleep(2)
    else:
        raise RuntimeError("PUBLIC_AUTH_START_TIMEOUT")
    tap(public_id="auth-use-pin")
    pin()
    # No hierarchy observation during PIN entry or its transition.
    time.sleep(6)
    print("B2_NORMAL_RESUME_COMPLETE", flush=True)


if __name__ == "__main__":
    try:
        resume()
    except Exception as e:
        print("R4_NORMAL_RESUME_REFUSED " + type(e).__name__ + (" " + str(e) if isinstance(e, Refused) else ""))
        raise SystemExit(2)
