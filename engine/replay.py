import json
from pathlib import Path


def replay_build(target_dir):
    receipts_dir = Path(target_dir) / ".buildout_receipts"

    receipts = sorted(receipts_dir.glob("*.json"))

    return {
        "replayed_steps": len(receipts),
        "status": "ok" if receipts else "empty",
    }
