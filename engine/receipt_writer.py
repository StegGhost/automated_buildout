import json
import os
import time
import hashlib


def hash_data(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def write_phase_receipt(target_dir, phase_name, install_result, validation):
    receipt_dir = os.path.join(target_dir, ".buildout_receipts")
    os.makedirs(receipt_dir, exist_ok=True)

    receipts = sorted(os.listdir(receipt_dir))
    parent_hash = None

    if receipts:
        last = receipts[-1]
        with open(os.path.join(receipt_dir, last)) as f:
            parent_hash = json.load(f)["receipt_hash"]

    receipt = {
        "timestamp": time.time(),
        "phase": phase_name,
        "install": install_result,
        "validation": validation,
        "parent_hash": parent_hash
    }

    # 🔥 include consensus receipt if present
    if "consensus_receipt" in install_result:
        receipt["consensus"] = install_result["consensus_receipt"]

    receipt_hash = hash_data(receipt)
    receipt["receipt_hash"] = receipt_hash

    filename = f"{len(receipts):03d}_{phase_name}.json"

    with open(os.path.join(receipt_dir, filename), "w") as f:
        json.dump(receipt, f, indent=2)

    return receipt
