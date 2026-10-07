"""Read-only Samsung/APK preflight; no app launch, auth, install, or wallet writes."""
import datetime
import hashlib
import json
import os
import re
import subprocess
import zipfile
from pathlib import Path

import h02_package as p
from h02_device import ROOT, run_dir
from p3_fixture import FIXTURE, verify

SERIAL = "R5CW6127VPR"
APP = "com.rjnr.pocketnode"
APPROVED = "903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f"
SDK = Path(os.environ["LOCALAPPDATA"]) / "Android/Sdk"


def adb(*args):
    return subprocess.check_output([str(SDK / "platform-tools/adb.exe"), "-s", SERIAL, *args], text=True, timeout=60)


def certificate(apk):
    env = dict(os.environ, JAVA_HOME="C:/Program Files/Android/Android Studio/jbr")
    # Use the apksigner Java entry directly; no shell command interpolation.
    cmd = [str(Path(env["JAVA_HOME"]) / "bin/java.exe"), "-jar",
           str(SDK / "build-tools/36.0.0/lib/apksigner.jar"), "verify", "--verbose", "--print-certs", str(apk)]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
    p.require(result.returncode == 0, "apk-signature-verification-failed")
    raw = result.stdout
    digests = re.findall(r"Signer #\d+ certificate SHA-256 digest: ([0-9a-fA-F]+)", raw)
    p.require(len(digests) == 1, "unsupported-signer-profile")
    return {"signatureVerified": True, "certificateSha256": digests[0].lower(),
            "subject": re.findall(r"Signer #\d+ certificate DN: (.+)", raw),
            "verifiedSchemes": [line for line in raw.splitlines() if line.startswith("Verified using")],
            "sourceStampPresent": "Verified for SourceStamp: true" in raw}


def main():
    out = run_dir(ROOT / "runs/wo3c/preflight")
    model = adb("shell", "getprop", "ro.product.model").strip()
    p.require(model == "SM-S9180", "wrong-phone")
    abi = adb("shell", "getprop", "ro.product.cpu.abilist").strip().split(",")
    current = adb("shell", "dumpsys", "package", APP)
    path = adb("shell", "pm", "path", APP).strip().splitlines()
    p.require(len(path) == 1 and path[0].startswith("package:/data/app/"), "installed-apk-path")
    apk_path = path[0][8:]
    installed_hash = adb("shell", "sha256sum", apk_path).split()[0]
    captured = out / "installed-pocket-1.8.3.apk"
    adb("pull", apk_path, str(captured))
    p.require(p.sha(captured) == installed_hash, "installed-apk-capture-hash")
    approved = ROOT / "runs/wo2/gradle/app/outputs/apk/debug/app-debug.apk"
    p.require(p.sha(approved) == APPROVED, "approved-apk-hash-mismatch")
    installed_cert, approved_cert = certificate(captured), certificate(approved)
    with zipfile.ZipFile(approved) as archive:
        libraries = sorted(n for n in archive.namelist() if n.startswith("lib/") and n.endswith(".so"))
    approved_abis = sorted({n.split("/")[1] for n in libraries})
    compatible = bool(set(abi) & set(approved_abis))
    features = adb("shell", "pm", "list", "features")
    df = adb("shell", "df", "-k", "/data").splitlines()[-1].split()
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    verify(fixture)
    receipt = p.read_json(ROOT / "runs/wo3b2/source/package-receipt.json")
    p.validate(ROOT / "runs/wo3b2/package-H2-immutable", receipt["manifestSha256"], APPROVED,
               "10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606")
    historical = p.read_json(ROOT / "runs/wo3-setup/phone-public.json")
    result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "serial": SERIAL,
              "model": model, "android": adb("shell", "getprop", "ro.build.version.release").strip(),
              "api": int(adb("shell", "getprop", "ro.build.version.sdk").strip()),
              "deviceAbis": abi, "dataAvailableBytes": int(df[3]) * 1024,
              "currentPocket": {"versionName": re.search(r"versionName=(\S+)", current)[1],
                                "versionCode": int(re.search(r"versionCode=(\d+)", current)[1]),
                                "apkSha256": installed_hash, "certificate": installed_cert},
              "approvedPocket": {"versionName": "1.8.5", "versionCode": 27, "apkSha256": APPROVED,
                                 "certificate": approved_cert, "nativeAbis": approved_abis, "libraries": libraries},
              "signatureCompatible": installed_cert["certificateSha256"] == approved_cert["certificateSha256"],
              "abiCompatible": compatible, "installAttempted": False, "appResetOrUninstallAttempted": False,
              "biometricHardwareFeatures": sorted(line.removeprefix("feature:") for line in features.splitlines()
                                                   if line in ("feature:android.hardware.fingerprint", "feature:android.hardware.biometrics.face")),
              "secureDeviceLockCurrentlyVerified": False, "secureDeviceLockStatus": "NOT_ESTABLISHED",
              "biometricEnrollmentOrCanAuthenticate": "NOT_TESTED",
              "historicalSetupKeyKdfVersions": sorted({r["kdfVersion"] for r in historical.get("key_material", [])}),
              "historicalSecurityScope": "Previously captured setup metadata only; not a fresh phone-control key/auth proof",
              "privateFixtureVerified": True, "immutableH2PackageValidation": "PASS",
              "H2ManifestSha256": receipt["manifestSha256"], "H2": receipt["H2"],
              "H2F2OraclesPresent": all((ROOT / ("runs/wo3b2/" + n)).is_file() for n in ("oracle-H2.json", "oracle-F2.json", "final-boundary.json")),
              "authenticationPromptPresented": False, "credentialsRequestedOrExtracted": False,
              "D2Used": False, "productionSourceModified": False, "phoneAppDataModified": False,
              "gate": "BLOCKED_APPROVED_APK_ABI" if not compatible else "INPUT_ABI_PASS"}
    (out / "result.json").write_bytes(p.encode(result))
    files = [{"path": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": path.stat().st_size,
              "sha256": p.sha(path)} for path in sorted(out.iterdir()) if path.is_file()]
    (out / "evidence-manifest.json").write_bytes(p.encode({"utc": result["utc"], "files": files}))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("PHONE_PREFLIGHT_REFUSED " + type(e).__name__ + (" " + str(e) if isinstance(e, p.Refused) else ""))
        raise SystemExit(2)
