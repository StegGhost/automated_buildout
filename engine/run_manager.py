import uuid
import time
from pathlib import Path


def create_run(target_dir: str):
    run_id = str(uuid.uuid4())
    started_at = time.time()

    run_dir = Path(target_dir) / ".buildout_runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    return {
        "run_id": run_id,
        "started_at": started_at,
        "run_dir": run_dir,
    }


def get_latest_run(target_dir: str):
    base = Path(target_dir) / ".buildout_runs"

    if not base.exists():
        return None

    runs = sorted(base.iterdir(), key=lambda p: p.stat().st_mtime)

    if not runs:
        return None

    return runs[-1].name
