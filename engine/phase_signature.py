import hashlib
import json


def hash_phase_signature(phase_name: str, manifest: dict) -> str:
    payload = {
        "phase": phase_name,
        "manifest": manifest,
    }
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
