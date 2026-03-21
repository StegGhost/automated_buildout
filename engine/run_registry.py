from pathlib import Path
import json


def registry_path(target_dir: str) -> Path:
    return Path(target_dir) / ".buildout_registry.json"


def load_registry(target_dir: str) -> dict:
    path = registry_path(target_dir)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_registry(target_dir: str, data: dict):
    path = registry_path(target_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
