import hashlib
import json


def _hash(data: dict) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode("utf-8")
    ).hexdigest()


def link_roots(previous_root: str | None, current_root: str) -> str:
    payload = {
        "prev": previous_root,
        "current": current_root,
    }
    return _hash(payload)
