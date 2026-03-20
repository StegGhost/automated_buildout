import hashlib
import json
import os
import time
from typing import Any, Dict, Optional, List


def _hash(data: Any) -> str:
    payload = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def ensure_receipt_dir(target_dir: str) -> str:
    receipt_dir = os.path.join(target_dir, ".buildout_receipts")
    os.makedirs(receipt_dir, exist_ok=True)
    return receipt_dir


def load_existing_receipts(target_dir: str) -> List[Dict[str, Any]]:
    receipt_dir = ensure_receipt_dir(target_dir)
    receipts: List[Dict[str, Any]] = []

    for fname in sorted(os.listdir(receipt_dir)):
        if not fname.endswith(".json"):
            continue

        full = os.path.join(receipt_dir, fname)
        with open(full, "r", encoding="utf-8") as f:
            receipts.append(json.load(f))

    return receipts


def get_chain_tip(target_dir: str) -> Optional[str]:
    receipts = load_existing_receipts(target_dir)
    if not receipts:
        return None
    return receipts[-1].get("receipt_hash")


def write_phase_receipt(
    target_dir: str,
    phase_name: str,
    install_result: Dict[str, Any],
    validation_result: Dict[str, Any],
) -> Dict[str, Any]:
    receipt_dir = ensure_receipt_dir(target_dir)
    parent_hash = get_chain_tip(target_dir)

    receipt = {
        "schema_version": "1.1.0",
        "timestamp": time.time(),
        "phase": phase_name,
        "install_result": install_result,
        "validation_result": validation_result,
        "parent_hash": parent_hash,
    }

    receipt["receipt_hash"] = _hash(receipt)

    filename = f"{int(receipt['timestamp'] * 1000000)}_{phase_name.split('.')[-1]}.json"
    path = os.path.join(receipt_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, sort_keys=True)

    receipt["receipt_path"] = path
    return receipt
