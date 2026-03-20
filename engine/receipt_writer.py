import json
import hashlib
import time
from pathlib import Path
from typing import List


def _hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def load_existing_receipts(target_dir: str) -> List[dict]:
    receipts_dir = Path(target_dir) / ".buildout_receipts"

    if not receipts_dir.exists():
        return []

    receipts = []

    for file in sorted(receipts_dir.glob("*.json")):
        try:
            receipts.append(json.loads(file.read_text()))
        except Exception:
            continue

    return receipts


def write_phase_receipt(
    target_dir: str,
    phase_name: str,
    install_result: dict,
    validation_result: dict,
    parent_hash: str = None,
):
    receipts_dir = Path(target_dir) / ".buildout_receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": "2.0.0",
        "timestamp": time.time(),
        "phase": phase_name,
        "install_result": install_result,
        "validation_result": validation_result,
        "parent_hash": parent_hash,
        "variant_score": install_result.get("score"),
        "consensus_mode": install_result.get("mode"),
    }

    receipt_hash = _hash(payload)
    payload["receipt_hash"] = receipt_hash

    filename = f"{int(payload['timestamp'])}_{phase_name}.json"
    path = receipts_dir / filename

    with path.open("w") as f:
        json.dump(payload, f, indent=2)

    payload["receipt_path"] = str(path)

    return payload
