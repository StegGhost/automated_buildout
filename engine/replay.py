import json
from pathlib import Path


def replay_build(target_dir):
    receipts_dir = Path(target_dir) / ".buildout_receipts"

    if not receipts_dir.exists():
        return {"status": "empty", "steps": 0, "trace": []}

    receipts = sorted(receipts_dir.glob("*.json"))
    replay_trace = []

    for receipt_file in receipts:
        data = json.loads(receipt_file.read_text(encoding="utf-8"))
        replay_trace.append(
            {
                "phase": data["phase"],
                "hash": data["receipt_hash"],
                "parent": data.get("parent_hash"),
                "score": data.get("variant_score"),
            }
        )

    return {
        "status": "ok",
        "steps": len(replay_trace),
        "trace": replay_trace,
    }
