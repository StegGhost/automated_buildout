import json
import hashlib
from pathlib import Path


def _hash(data) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode("utf-8")
    ).hexdigest()


def build_canonical_run_receipt(run_result: dict):
    """
    Canonical run receipt with TWO identities:

    1. state_hash
       - stable across equivalent runs
       - used for idempotency / replay detection

    2. canonical_hash
       - includes run metadata
       - used for full CGE-style canonical receipt identity
    """

    state_payload = {
        "schema": "cge.state.v1",
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

    state_hash = _hash(state_payload)

    canonical = {
        "schema": "cge.canonical.v1",
        "run_id": run_result.get("run_id"),
        "parent_run_id": run_result.get("parent_run_id"),
        "state_hash": state_hash,
        "state": state_payload,
    }

    canonical["canonical_hash"] = _hash(canonical)

    return canonical


def write_canonical_receipt(target_dir: str, run_id: str, canonical: dict):
    path = Path(target_dir) / ".buildout_runs" / run_id / "canonical_receipt.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(canonical, f, indent=2, sort_keys=True)

    return str(path)


def compute_merkle_root(receipts: list):
    hashes = [r["receipt_hash"] for r in receipts if "receipt_hash" in r]

    if not hashes:
        return None

    while len(hashes) > 1:
        next_level = []

        for i in range(0, len(hashes), 2):
            left = hashes[i]
            right = hashes[i + 1] if i + 1 < len(hashes) else left
            next_level.append(
                hashlib.sha256((left + right).encode("utf-8")).hexdigest()
            )

        hashes = next_level

    return hashes[0]


def write_merkle_proof(target_dir: str, run_id: str, merkle_root: str):
    path = Path(target_dir) / ".buildout_runs" / run_id / "merkle.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema": "cge.merkle.v1",
        "run_id": run_id,
        "root": merkle_root,
    }

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    return str(path)
