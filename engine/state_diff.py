import hashlib
import json


def _hash(data) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def compute_phase_state(phase_name, install_result, validation_result):
    payload = {
        "phase": phase_name,
        "install": install_result,
        "validation": validation_result,
    }
    return _hash(payload)


def should_rebuild(phase_name, new_state, phase_registry, dirty_upstream):
    if dirty_upstream:
        return True

    prev = phase_registry.get(phase_name)
    if not prev:
        return True

    return prev.get("state_hash") != new_state
