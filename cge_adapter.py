import json
import hashlib
from pathlib import Path


def _hash(data: dict):
    encoded = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def build_canonical_run_receipt(run_result: dict):
    """
    Convert internal run result → canonical CGE-ready receipt
    """

    canonical = {
        "schema_version": "cge.1.0.0",
        "run_id": run_result.get("run_id"),
        "parent_run_id": run_result.get("parent_run_id"),
        "status": run_result.get("status"),
        "health": run_result.get("health"),
        "replay_result": run_result.get("replay_result"),
        "phases": [
            {
                "phase": r.get("phase"),
                "valid": r.get("valid"),
                "receipt_hash": r.get("receipt_hash"),
            }
            for r in run_result.get("results", [])
        ],
    }

    canonical_hash = _hash(canonical)
    canonical["canonical_hash"] = canonical_hash

    return canonical


def write_canonical_receipt(target_dir: str, run_id: str, canonical: dict):
    path = Path(target_dir) / ".buildout_runs" / run_id / "canonical_receipt.json"

    with path.open("w") as f:
        json.dump(canonical, f, indent=2)

    return str(path)


def compute_merkle_root(receipts: list):
    """
    Simple Merkle root (pairwise hashing)
    """
    if not receipts:
        return None

    hashes = [r["receipt_hash"] for r in receipts]

    while len(hashes) > 1:
        next_level = []

        for i in range(0, len(hashes), 2):
            left = hashes[i]
            right = hashes[i + 1] if i + 1 < len(hashes) else left

            combined = hashlib.sha256((left + right).encode()).hexdigest()
            next_level.append(combined)

        hashes = next_level

    return hashes[0]


def write_merkle_proof(target_dir: str, run_id: str, root_hash: str):
    path = Path(target_dir) / ".buildout_runs" / run_id / "merkle.json"

    data = {
        "merkle_root": root_hash,
    }

    with path.open("w") as f:
        json.dump(data, f, indent=2)

    return str(path)
