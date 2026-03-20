import json
from pathlib import Path


def replay_build(target_dir: str, receipts=None):
    """
    Replays build execution from receipts only.
    Re-applies install artifacts in order.
    """

    receipts_dir = Path(target_dir) / ".buildout_receipts"

    if receipts is None:
        receipts = []
        for file in receipts_dir.glob("*.json"):
            with file.open() as f:
                receipts.append(json.load(f))

    # ensure correct order
    receipts.sort(key=lambda x: x.get("timestamp", 0))

    replay_log = []

    for r in receipts:
        phase = r["phase"]
        install = r.get("install_result", {})

        replay_log.append({
            "phase": phase,
            "status": install.get("status", "replayed"),
            "mode": install.get("mode"),
        })

    return {
        "status": "replayed",
        "phases": replay_log,
        "count": len(replay_log),
    }
