import json
import time
import hashlib
from pathlib import Path


def _hash(data: dict):
    encoded = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def write_phase_receipt(
    target_dir,
    run_id,
    phase_name,
    install_result,
    validation_result,
    parent_hash=None,
):
    ts = time.time()

    receipt = {
        "schema_version": "3.0.0",
        "run_id": run_id,
        "timestamp": ts,
        "phase": phase_name,
        "install_result": install_result,
        "validation_result": validation_result,
        "parent_hash": parent_hash,
    }

    receipt_hash = _hash(receipt)
    receipt["receipt_hash"] = receipt_hash

    run_dir = Path(target_dir) / ".buildout_runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{int(ts)}_{phase_name}.json"
    path = run_dir / filename

    with path.open("w") as f:
        json.dump(receipt, f, indent=2)

    receipt["receipt_path"] = str(path)

    return receipt
