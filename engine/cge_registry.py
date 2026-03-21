from pathlib import Path
import json


def path(target_dir: str):
    return Path(target_dir) / ".cge_store" / "latest_root.json"


def load_latest_root(target_dir: str):
    p = path(target_dir)
    if not p.exists():
        return None
    return json.loads(p.read_text()).get("global_root")


def save_latest_root(target_dir: str, root: str):
    p = path(target_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"global_root": root}, indent=2))
