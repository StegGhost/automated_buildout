import time
import uuid
from pathlib import Path


def create_run_id():
    return f"{int(time.time())}_{uuid.uuid4().hex[:6]}"


def ensure_run_dir(target_dir: str, run_id: str):
    path = Path(target_dir) / ".buildout_receipts" / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_latest_run_id(target_dir: str):
    base = Path(target_dir) / ".buildout_receipts"

    if not base.exists():
        return None

    runs = sorted([p.name for p in base.iterdir() if p.is_dir()])

    return runs[-1] if runs else None
