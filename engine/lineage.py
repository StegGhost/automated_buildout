import json
from pathlib import Path


def write_lineage(target_dir: str, run_id: str, parent_run_id: str | None):
    run_dir = Path(target_dir) / ".buildout_runs" / run_id

    data = {
        "run_id": run_id,
        "parent_run_id": parent_run_id,
    }

    path = run_dir / "lineage.json"

    with path.open("w") as f:
        json.dump(data, f, indent=2)

    return data
