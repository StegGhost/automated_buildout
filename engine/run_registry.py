import json
from pathlib import Path


REGISTRY_FILE = ".run_registry.json"


def load_registry(target_dir: str):
    path = Path(target_dir) / REGISTRY_FILE

    if not path.exists():
        return {}

    return json.loads(path.read_text())


def save_registry(target_dir: str, registry: dict):
    path = Path(target_dir) / REGISTRY_FILE
    path.write_text(json.dumps(registry, indent=2))


def find_existing_run(target_dir: str, signature: str):
    registry = load_registry(target_dir)
    return registry.get(signature)


def register_run(target_dir: str, signature: str, run_id: str):
    registry = load_registry(target_dir)
    registry[signature] = run_id
    save_registry(target_dir, registry)
