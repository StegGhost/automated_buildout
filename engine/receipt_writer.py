import json
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional


def _hash(data: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode("utf-8")
    ).hexdigest()


def write_phase_receipt(
    target_dir: str,
    phase_name: str,
    install_result: Dict[str, Any],
    validation_result: Dict[str, Any],
    parent_hash: Optional[str] = None,
) -> Dict[str, Any]:
    receipts_dir = Path(target_dir) / ".buildout_receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)

    payload: Dict[str, Any] = {
        "schema_version": "2.0.0",
        "timestamp": time.time(),
        "phase": phase_name,
        "install_result": install_result,
        "validation_result": validation_result,
        "parent_hash": parent_hash,
        "variant_score": install_result.get("score"),
        "consensus_mode": install_result.get("mode"),
    }

    payload["receipt_hash"] = _hash(payload)

    filename = f"{int(payload['timestamp'])}_{phase_name}.json"
    path = receipts_dir / filename

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    payload["receipt_path"] = str(path)
    return payload


def load_existing_receipts(target_dir: str) -> List[Dict[str, Any]]:
    receipts_dir = Path(target_dir) / ".buildout_receipts"

    if not receipts_dir.exists():
        return []

    receipts: List[Dict[str, Any]] = []

    for file in receipts_dir.glob("*.json"):
        try:
            with file.open("r", encoding="utf-8") as f:
                receipts.append(json.load(f))
        except Exception:
            continue

    if not receipts:
        return []

    receipts.sort(key=lambda x: x.get("timestamp", 0))

    latest_run: List[Dict[str, Any]] = []
    run_start: Optional[float] = None

    for receipt in receipts:
        ts = receipt.get("timestamp", 0)

        if run_start is None:
            run_start = ts
            latest_run.append(receipt)
            continue

        if abs(ts - run_start) < 1.0:
            latest_run.append(receipt)
        else:
            latest_run = [receipt]
            run_start = ts

    latest_run.sort(key=lambda x: x.get("timestamp", 0))
    return latest_run
