"""PM-approved canonical-position gate with separately checked v1.8.5 estimates.

No ADB, key access, source mutation, or transactions. Audits only frozen public
observations and public chain data. A known 61-CKB estimate is accepted only at
a recent canonical header; other state/mapping/coverage requirements are intact.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path

import h02_package as p
from b2r2_acceptance import check as canonical_check
from b2r2_chain import ROOT, URL, DAO, rpc

CONTRACT = "WO-3B2-R4-canonical-position-known-reader-defect-v1"


def audit(observation, oracle, output):
    observation, oracle, output = map(Path, (observation, oracle, output))
    p.require(not output.exists(), "audit-output-exists")
    n = p.read_json(observation / "summary.json")
    o = p.read_json(oracle)
    p.require(len(n["room"]["daoCells"]) == 1, "dao-row-count")
    row = n["room"]["daoCells"][0]
    cells = [(a, c) for a in o["accounts"] for c in a["liveCells"]
             if c["out_point"]["tx_hash"] == row["txHash"] and
             int(c["out_point"]["index"], 16) == int(row["index"], 16)]
    p.require(len(cells) == 1, "oracle-dao-identity")
    owner, cell = cells[0]
    value = cell["output"]
    p.require(value["type"] == {"code_hash": DAO, "hash_type": "type", "args": "0x"}
              and cell["output_data"] == "0x0000000000000000", "active-dao-profile")
    capacity = int(value["capacity"], 16)
    occupied = (8 + 32 + 1 + len(bytes.fromhex(value["lock"]["args"][2:]))
                + 32 + 1 + len(bytes.fromhex(value["type"]["args"][2:]))
                + len(bytes.fromhex(cell["output_data"][2:]))) * 10**8
    p.require(occupied == 102 * 10**8, "occupied-profile")
    deposit_hash = owner["transactionDetails"][row["txHash"]]["tx_status"]["block_hash"]
    deposit = owner["headers"][deposit_hash]
    end = n["accounts"][0]["verifiedTip"]
    start = max(int(deposit["number"], 16), end - 64)
    captured_ms = int(datetime.datetime.fromisoformat(n["utc"]).timestamp() * 1000)
    age_ms = captured_ms - row["lastUpdatedAt"]
    p.require(0 <= age_ms <= 180_000, "dao-cache-not-fresh-at-capture")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        headers = list(pool.map(lambda h: rpc(URL, "get_header_by_number", [hex(h)]), range(start, end + 1)))
    p.require(headers[-1]["hash"] == n["accounts"][0]["verifiedTipHash"], "audit-tip-anchor")
    p.require(all(h["parent_hash"] == prev["hash"] for prev, h in zip(headers, headers[1:])), "audit-header-chain")
    p.require(rpc(URL, "get_block_hash", [deposit["number"]]) == deposit_hash, "deposit-not-canonical")
    ar = lambda h: int.from_bytes(bytes.fromhex(h["dao"][2:])[8:16], "little")
    rate = ar(deposit)
    computed = []
    for h in headers:
        def reward(occ):
            return (capacity - occ) * ar(h) // rate + occ - capacity
        computed.append({"height": int(h["number"], 16), "hash": h["hash"],
                         "canonicalCompensation": reward(occupied),
                         "knownReaderCompensation": reward(61 * 10**8)})
    matches = [x for x in computed if x["knownReaderCompensation"] == row["compensation"]]
    # A small tip interval plus fresh write time excludes an unchanged old H2 cache.
    result = {"contract": CONTRACT, "observation": str(observation.resolve()),
              "oracleSha256": p.sha(oracle), "summarySha256": p.sha(observation / "summary.json"),
              "outPoint": cell["out_point"], "ownerAccountIndex": owner["index"],
              "capacity": capacity, "canonicalOccupied": occupied, "readerOccupied": 61 * 10**8,
              "cacheAgeAtCaptureMs": age_ms, "observedCompensation": row["compensation"],
              "lastUpdatedAt": row["lastUpdatedAt"], "capturedNativeTip": end,
              "matchingKnownReaderHeaders": matches,
              "verdict": "KNOWN_READER_DEFECT_ONLY" if len(matches) == 1 else "UNEXPLAINED_ESTIMATE",
              "asOfHeaderIsInferred": True, "depositHeader": deposit, "headers": headers,
              "computed": computed}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(p.encode(result))
    print(json.dumps({k: result[k] for k in ("verdict", "capturedNativeTip", "observedCompensation",
                     "matchingKnownReaderHeaders", "cacheAgeAtCaptureMs")}, indent=2))
    p.require(result["verdict"] == "KNOWN_READER_DEFECT_ONLY", "new-dao-estimate-divergence")


def check(observation, oracle, boundary, dao_audit):
    observation, oracle = Path(observation), Path(oracle)
    result = canonical_check(observation, oracle, boundary, position_only=True)
    n = p.read_json(observation / "summary.json")
    a = p.read_json(Path(dao_audit))
    row = n["room"]["daoCells"][0]
    p.require(all(row[k] is None for k in ("withdrawBlockNumber", "withdrawBlockHash",
              "withdrawEpochHex", "unlockEpochHex")), "unexpected-dao-lifecycle-metadata")
    p.require(a["contract"] == CONTRACT and a["verdict"] == "KNOWN_READER_DEFECT_ONLY", "dao-audit-contract")
    p.require(Path(a["observation"]).resolve() == observation.resolve()
              and a["summarySha256"] == p.sha(observation / "summary.json")
              and a["oracleSha256"] == p.sha(oracle), "dao-audit-observation-binding")
    p.require(a["observedCompensation"] == row["compensation"]
              and a["lastUpdatedAt"] == row["lastUpdatedAt"]
              and len(a["matchingKnownReaderHeaders"]) == 1, "dao-estimate-binding")
    p.require(a["matchingKnownReaderHeaders"][0]["knownReaderCompensation"] == row["compensation"]
              and a["canonicalOccupied"] == 102 * 10**8 and a["readerOccupied"] == 61 * 10**8
              and 0 <= a["cacheAgeAtCaptureMs"] <= 180_000, "dao-estimate-policy")
    result.update({"result": "PASS", "contract": CONTRACT,
                   "scope": "Canonical two-account/active-DAO continuity; known reader defect separately recorded",
                   "daoEstimate": {k: a[k] for k in ("observedCompensation", "lastUpdatedAt",
                       "matchingKnownReaderHeaders", "canonicalOccupied", "readerOccupied", "asOfHeaderIsInferred")},
                   "daoAuditSha256": p.sha(Path(dao_audit))})
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("audit", "check"):
        q = sub.add_parser(action)
        q.add_argument("observation", type=Path)
        q.add_argument("oracle", type=Path)
        q.add_argument("--out", type=Path, required=True)
        if action == "check":
            q.add_argument("--boundary", type=int, required=True)
            q.add_argument("--dao-audit", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == "audit":
            audit(args.observation, args.oracle, args.out)
        else:
            p.require(not args.out.exists(), "acceptance-output-exists")
            result = check(args.observation, args.oracle, args.boundary, args.dao_audit)
            args.out.write_bytes(p.encode(result))
            print(json.dumps(result, indent=2))
    except p.Refused as e:
        print("R4_ACCEPTANCE_REFUSED " + str(e))
        raise SystemExit(2)
