import hashlib
import json


def _hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def generate_successor_proof(previous_receipts, current_receipts, run_id):
    prev_hash = previous_receipts[-1]["receipt_hash"] if previous_receipts else None
    curr_hash = current_receipts[-1]["receipt_hash"] if current_receipts else None

    payload = {
        "run_id": run_id,
        "previous_head": prev_hash,
        "current_head": curr_hash,
        "transition_valid": prev_hash != curr_hash,
        "receipt_count": len(current_receipts),
    }

    payload["proof_hash"] = _hash(payload)

    return payload
