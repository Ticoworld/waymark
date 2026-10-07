"""Read-only DAO diagnosis. No key access, ADB, signing, or wallet mutations.

Capture immutable public inputs with `capture`, recompute with `calculate`,
cross-check the public node with `crosscheck`, and check preserved SOURCE/evidence
with `verify`. Existing captures are never
overwritten. All amounts are integer shannons; no floating-point DAO math.
"""
import argparse
import concurrent.futures
import hashlib
import json
import shutil
import struct
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs/wo3b2-r3"
POCKET = ROOT / "repos/pocket-node"
PIN = "b28979de744798ffb75367b031d4871ec3af1a12"
APK = "runs/wo2/gradle/app/outputs/apk/debug/app-debug.apk"
APK_HASH = "903e1e641cd3bac70d32cab04c06152decc60b25203c60dc802fa3f65fa7865f"
TX = "0x96845bb24d55c2d506d76d425da76d41beb39c9157b16c2a2b1a500b9f3933e2"
GENESIS = "0x10639e0895502b5688a6be8cf69460d76541bfa4821629d86d62ba0aae3f9606"
HEIGHTS = (22647433, 22647449, 22647450, 22647478, 22647479)
RPC = "https://testnet.ckb.dev"
CKB_REF = "52c2be1a104edbf0ee1b6e261ada7d0db10af740"  # v0.200.0
RFC_REF = "62a6e08e16a995ab94562581978ceac3726c31e6"
SHANNONS = 100_000_000


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(name, value):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def git(*args, cwd=POCKET):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def runtime_metadata():
    runtime = ROOT / "runs/wo3b2/source/avd"
    assert runtime.is_dir()
    return [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
             "mtimeNs": p.stat().st_mtime_ns}
            for p in sorted(runtime.rglob("*")) if p.is_file()]


def preservation():
    seal = read(ROOT / "runs/wo3b2/source/evidence-seal.json")
    assert not seal["runtimeRetirementAllowed"]
    for item in seal["files"]:
        p = ROOT / item["path"]
        assert p.stat().st_size == item["bytes"] and sha(p) == item["sha256"], item["path"]
    assert git("rev-parse", "HEAD") == PIN
    assert git("status", "--porcelain") == ""
    assert sha(ROOT / APK) == APK_HASH
    return {"utc": datetime.now(timezone.utc).isoformat(),
            "freeBytes": shutil.disk_usage(ROOT).free,
            "sourceEvidenceSealSha256": sha(ROOT / "runs/wo3b2/source/evidence-seal.json"),
            "sourceEvidenceFilesVerified": len(seal["files"]),
            "runtimeMetadata": runtime_metadata(), "pocketCommit": PIN,
            "pocketWorktreeClean": True, "apkSha256": APK_HASH,
            "privateFixtureExists": (ROOT / "private/pocket-disposable-fixture.json").is_file(),
            "trackedFiles": {p: sha(ROOT / p) for p in git("ls-files", cwd=ROOT).splitlines()}}


def request(url, data=None):
    req = urllib.request.Request(url, data=data,
        headers={"User-Agent": "H02-read-only-DAO-diagnosis", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read()


def rpc(method, params):
    assert method in {"get_transaction", "get_header_by_number", "get_block_hash",
                      "get_live_cell", "get_tip_header", "calculate_dao_maximum_withdraw"}
    value = json.loads(request(RPC, json.dumps(
        {"id": 1, "jsonrpc": "2.0", "method": method, "params": params}).encode()))
    assert "error" not in value, value.get("error")
    return value["result"]


def capture():
    save("preservation-before.json", preservation())
    refs = [("ckb", CKB_REF, p) for p in (
        "util/gen-types/src/extension/capacity.rs", "util/occupied-capacity/core/src/units.rs",
        "util/dao/src/lib.rs", "util/dao/utils/src/lib.rs", "rpc/src/module/chain.rs",
        "rpc/src/module/experiment.rs",
        "util/gen-types/schemas/blockchain.mol")]
    refs.append(("rfcs", RFC_REF, "rfcs/0023-dao-deposit-withdraw/0023-dao-deposit-withdraw.md"))
    def fetch(ref):
        repo, commit, path = ref
        url = f"https://raw.githubusercontent.com/nervosnetwork/{repo}/{commit}/{path}"
        content = request(url)
        local = OUT / "references" / repo / path
        local.parent.mkdir(parents=True, exist_ok=True)
        with local.open("xb") as f:
            f.write(content)
        return {"url": url, "path": local.relative_to(ROOT).as_posix(), "sha256": sha(local)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        save("references.json", list(pool.map(fetch, refs)))
    headers = {str(n): rpc("get_header_by_number", [hex(n)]) for n in HEIGHTS}
    canonical = {str(n): rpc("get_block_hash", [hex(n)]) for n in HEIGHTS}
    save("chain.json", {"utc": datetime.now(timezone.utc).isoformat(), "rpc": RPC,
        "genesis": rpc("get_block_hash", ["0x0"]),
        "transaction": rpc("get_transaction", [TX]), "headers": headers,
        "canonicalHashes": canonical, "currentTip": rpc("get_tip_header", []),
        "liveCell": rpc("get_live_cell", [{"tx_hash": TX, "index": "0x0"}, True])})
    print("Captured public chain/reference inputs; preserved SOURCE evidence verified.")


def unhex(value):
    return bytes.fromhex(value.removeprefix("0x"))


def molecule_table(fields):
    offset = 4 * (len(fields) + 1)
    offsets = []
    for field in fields:
        offsets.append(offset)
        offset += len(field)
    return struct.pack("<" + "I" * (len(fields) + 1), offset, *offsets) + b"".join(fields)


def script_bytes(script):
    args = unhex(script["args"])
    return molecule_table([unhex(script["code_hash"]), bytes([{"data": 0, "type": 1,
        "data1": 2, "data2": 4}[script["hash_type"]]]), struct.pack("<I", len(args)) + args])


def values(capacity, occupied, ar_start, ar_end):
    counted = capacity - occupied
    product = counted * ar_end
    quotient, remainder = divmod(product, ar_start)
    maximum = quotient + occupied
    return {"occupiedShannons": occupied, "countedShannons": counted, "product": product,
            "divisor": ar_start, "quotient": quotient, "remainder": remainder,
            "maximumWithdrawShannons": maximum, "compensationShannons": maximum - capacity}


def calculate():
    # Published RFC-0023 worked example, independent of the Pocket fixture.
    assert values(200_000_000_000, 10_200_000_000, 10_000_435_847_357_921,
                  10_008_616_347_796_555)["maximumWithdrawShannons"] == 200_155_259_131
    chain = read(OUT / "chain.json")
    assert chain["genesis"] == GENESIS
    tx = chain["transaction"]["transaction"]
    assert tx["hash"] == TX and chain["transaction"]["tx_status"]["status"] == "committed"
    cell, data = tx["outputs"][0], tx["outputs_data"][0]
    capacity = int(cell["capacity"], 16)  # Only canonical chain is an arithmetic input.
    lock, typ = cell["lock"], cell["type"]
    assert data == "0x0000000000000000" and typ["args"] == "0x"
    assert typ["code_hash"] == "0x82d76d1b75fe2fd9a27dfbaa65a039221a380d76c926f378d3f81cf3e7e13f2e"
    assert typ["hash_type"] == lock["hash_type"] == "type"
    assert lock["args"] == "0x2da024570462b0e2421d87abcbfebd4567d52ad5"
    assert lock["code_hash"] == "0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8"
    assert chain["liveCell"]["status"] == "live"
    assert chain["liveCell"]["cell"]["output"] == cell
    assert chain["liveCell"]["cell"]["data"]["content"] == data
    parts = {"capacity": 8, "lockCodeHash": len(unhex(lock["code_hash"])), "lockHashType": 1,
             "lockArgs": len(unhex(lock["args"])), "typeCodeHash": len(unhex(typ["code_hash"])),
             "typeHashType": 1, "typeArgs": len(unhex(typ["args"])), "data": len(unhex(data))}
    occupied = sum(parts.values()) * SHANNONS
    assert occupied == 102 * SHANNONS
    serialized = molecule_table([capacity.to_bytes(8, "little"), script_bytes(lock), script_bytes(typ)])
    start = chain["headers"][str(HEIGHTS[0])]
    assert chain["transaction"]["tx_status"]["block_hash"] == start["hash"]
    old = read(ROOT / "runs/wo3b2/chain-events/dao-deposit/confirmation.json")
    assert old["transaction"]["transaction"] == tx and old["header"] == start
    ar = lambda h: int.from_bytes(unhex(h["dao"])[8:16], "little")
    computed = []
    for height in HEIGHTS:
        h = chain["headers"][str(height)]
        assert int(h["number"], 16) == height and h["hash"] == chain["canonicalHashes"][str(height)]
        computed.append({"height": height, "hash": h["hash"], "dao": h["dao"], "ar": ar(h),
            "canonical": values(capacity, occupied, ar(start), ar(h)),
            "pocketReader61": values(capacity, 61 * SHANNONS, ar(start), ar(h))})
    # Cache is loaded only after independent computation. Never used as an oracle input.
    comparisons = []
    for label, boundary in (("dao-settled", 22647449), ("preH2-restart", 22647478)):
        public = read(ROOT / "runs/wo3b2/source" / label / "public.json")
        row = next(r for r in public["daoCells"] if r["txHash"] == TX and int(r["index"], 16) == 0)
        fixed = next(r for r in computed if r["height"] == boundary)
        comparisons.append({"observation": label, "fixedBoundary": boundary, "row": row,
            "canonicalAtBoundary": fixed["canonical"]["compensationShannons"],
            "reader61AtBoundary": fixed["pocketReader61"]["compensationShannons"],
            "cacheMatchesReader61": row["compensation"] == fixed["pocketReader61"]["compensationShannons"]})
    result = {"network": "TESTNET", "outPoint": {"tx_hash": TX, "index": "0x0"},
        "cell": cell, "data": data, "capacityShannons": capacity, "occupiedFieldBytes": parts,
        "occupiedShannons": occupied, "serializedCellOutputHex": "0x" + serialized.hex(),
        "serializedCellOutputBytes": len(serialized), "rawDataBytes": len(unhex(data)),
        "moleculeBytesWrapperLength": len(unhex(data)) + 4,
        "depositAR": ar(start), "computed": computed, "cacheComparisons": comparisons,
        "currentLiveStatus": chain["liveCell"]["status"],
        "boundaryLimitation": "Fixed historical headers are independently queried. Cache as-of headers are inferred from integer matches, not recorded nativeGetTipHeader calls. Current public tip is not substituted for a historical cache boundary."}
    if (OUT / "calculation.json").exists():
        assert read(OUT / "calculation.json") == result
        print("PASS: offline deterministic replay matches saved calculation.")
    else:
        save("calculation.json", result)
    print(json.dumps({"occupiedCKB": occupied // SHANNONS, "comparisons": [
        {k: v for k, v in x.items() if k != "row"} for x in comparisons],
        "currentLiveStatus": result["currentLiveStatus"]}, indent=2))


def crosscheck():
    calculation = read(OUT / "calculation.json")
    rows = []
    for row in calculation["computed"][1:]:
        params = [calculation["outPoint"], row["hash"]]
        result = rpc("calculate_dao_maximum_withdraw", params)
        amount = int(result, 16)
        rows.append({"height": row["height"], "method": "calculate_dao_maximum_withdraw",
            "params": params, "rpcResult": result, "maximumShannons": amount,
            "compensationShannons": amount - calculation["capacityShannons"],
            "matchesIndependentCalculation": amount == row["canonical"]["maximumWithdrawShannons"]})
    if (OUT / "rpc-crosscheck.json").exists():
        assert read(OUT / "rpc-crosscheck.json") == rows
    else:
        save("rpc-crosscheck.json", rows)
    assert all(r["matchesIndependentCalculation"] for r in rows)
    print("PASS: public node maximum-withdraw calculation agrees at all four fixed headers.")


def verify():
    before = read(OUT / "preservation-before.json")
    after = preservation()
    assert before["runtimeMetadata"] == after["runtimeMetadata"]
    assert before["sourceEvidenceSealSha256"] == after["sourceEvidenceSealSha256"]
    assert before["trackedFiles"] == {p: sha(ROOT / p) for p in before["trackedFiles"]}
    after["sourceRuntimeMetadataUnchanged"] = True
    after["existingTrackedFilesUnchanged"] = True
    save("preservation-after.json", after)
    print(json.dumps({k: after[k] for k in ("freeBytes", "sourceEvidenceFilesVerified",
        "sourceRuntimeMetadataUnchanged", "existingTrackedFilesUnchanged", "pocketWorktreeClean",
        "privateFixtureExists", "apkSha256")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("capture", "calculate", "crosscheck", "verify"))
    globals()[parser.parse_args().action]()
