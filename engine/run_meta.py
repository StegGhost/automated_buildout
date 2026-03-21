from pathlib import Path
import json
import time


def write_run_meta(run_dir: Path, payload: dict):
    data = {
        "written_at": time.time(),
        **payload,
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_meta.json").write_text(
        json.dumps(data, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return data


def load_run_meta(run_dir: Path):
    path = run_dir / "run_meta.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
