import json
from pathlib import Path


def load_canonical(target_dir: str, run_id: str):
    path = Path(target_dir) / ".buildout_runs" / run_id / "canonical_receipt.json"

    if not path.exists():
        return None

    with path.open() as f:
        return json.load(f)


def detect_replay(target_dir: str, current_run_id: str, prev_run_id: str | None):
    if not prev_run_id:
        return False

    current = load_canonical(target_dir, current_run_id)
    previous = load_canonical(target_dir, prev_run_id)

    if not current or not previous:
        return False

    return current.get("canonical_hash") == previous.get("canonical_hash")
