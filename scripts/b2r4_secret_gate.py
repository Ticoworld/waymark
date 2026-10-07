"""Exact local credential exclusion in a package. Emits booleans only.

Private fixture values are consumed in memory, never used as command arguments
or written to diagnostics. Structural/allowlist validation remains mandatory.
"""
import hashlib
import json
from pathlib import Path
from p3_fixture import FIXTURE, derive, verify
from h02_device import ROOT
import h02_package as p


def check_paths(paths):
    paths = list(map(Path, paths))
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    verify(fixture)
    words = fixture["wallets"][0]["mnemonic"]
    p.require(fixture.get("passphrase", "") == "", "unsupported-passphrase")
    keys = [derive(words, "m/44'/309'/%d'/0/0" % i) for i in (0, 1)]
    seed = hashlib.pbkdf2_hmac("sha512", words.encode(), b"mnemonic", 2048)
    pin = json.loads((ROOT / "private/wo3b1-r2/emulator-security.json").read_text())["pin"]
    tokens = [words.encode(), words.encode("utf-16-le"), seed, seed.hex().encode(),
              pin.encode(), pin.encode("utf-16-le")]
    for key in keys:
        tokens.extend((key, key.hex().encode(), key.hex().upper().encode()))
    for path in paths:
        p.require(path.is_file(), "package-file-required")
        raw = path.read_bytes()
        p.require(not any(token in raw for token in tokens), "exact-secret-found")
    return {"result": "PASS", "scope": "Exact mnemonic, BIP39 seed, both derived account keys and local emulator PIN; binary/text encodings; values not emitted",
            "filesChecked": len(paths)}


def check(package):
    result = check_paths(Path(package).iterdir())
    result["requiredStructuralGate"] = "h02_package.validate"
    return result
