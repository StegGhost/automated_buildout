import json
import hashlib
from pathlib import Path


def _hash(data) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()


def build_canonical_run_receipt(run_result: dict):
    """
    Canonical representation of a run (state identity)
    """

    canonical = {
        "schema": "cge.canonical.v1",
        "status": run_result["status"],
        "phases": [
            {
                "phase": r["phase"],
                "valid": r["valid"],
                "receipt_hash": r["receipt_hash"],
            }
            for r in run_result["results"]
        ],
    }

    canonical_hash = _hash(canonical)

    canonical["canonical_hash"] = canonical_hash

    return canonical


def write_canonical_receipt(target_dir: str, run_id: str, canonical: dict):
    path = Path(target_dir) / ".buildout_runs" / run_id / "canonical_receipt.json"

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as f:
        json.dump(canonical, f, indent=2)

    return str(path)


def compute_merkle_root(receipts: list):
    """
    Simple merkle root = hash of receipt hashes
    """

    hashes = [r["receipt_hash"] for r in receipts]

    return _hash(hashes)


def write_merkle_proof(target_dir: str, run_id: str, merkle_root: str):
    path = Path(target_dir) / ".buildout_runs" / run_id / "merkle.json"

    data = {
        "schema": "cge.merkle.v1",
        "root": merkle_root,
    }

    with path.open("w") as f:
        json.dump(data, f, indent=2)

    return str(path)
