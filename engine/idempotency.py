import hashlib
import json


def compute_build_signature(manifest: dict, phases: list) -> str:
    payload = {
        "manifest": manifest,
        "phases": [getattr(p, "__name__", str(p)) for p in phases],
    }

    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()
