import json
import time
import hashlib
from pathlib import Path


def _hash_receipt(data: dict) -> str:
    encoded = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(encoded).hexdigest()


def _atomic_write(path: Path, data: dict):
    tmp_path = path.with_suffix(".tmp")

    # write temp file
    with tmp_path.open("w") as f:
        json.dump(data, f, indent=2)
        f.flush()
        f.close()

    # atomic rename (POSIX safe)
    tmp_path.replace(path)


def write_phase_receipt(
    target_dir: str,
    phase_name: str,
    install_result: dict,
    validation_result: dict,
    parent_hash: str | None,
):
    receipts_dir = Path(target_dir) / ".buildout_receipts"

    # 🔥 ensure directory exists
    receipts_dir.mkdir(parents=True, exist_ok=True)

    timestamp = time.time()

    receipt = {
        "schema_version": "3.0.0",
        "timestamp": timestamp,
        "phase": phase_name,
        "install_result": install_result,
        "validation_result": validation_result,
        "parent_hash": parent_hash,
        "variant_score": None,
        "consensus_mode": "module",
    }

    # hash AFTER structure finalized
    receipt_hash = _hash_receipt(receipt)
    receipt["receipt_hash"] = receipt_hash

    filename = f"{int(timestamp)}_{phase_name.replace('.', '_')}.json"
    receipt_path = receipts_dir / filename

    # 🔥 ATOMIC WRITE
    _atomic_write(receipt_path, receipt)

    # 🔥 WRITE BARRIER (ensure visible + readable)
    with receipt_path.open() as f:
        json.load(f)

    receipt["receipt_path"] = str(receipt_path)

    return receipt
