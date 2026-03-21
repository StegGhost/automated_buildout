import json
import hashlib
from pathlib import Path


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _store_dir(target_dir: str) -> Path:
    return Path(target_dir) / ".cge_store"


def _objects_dir(target_dir: str) -> Path:
    return _store_dir(target_dir) / "objects"


def _roots_dir(target_dir: str) -> Path:
    return _store_dir(target_dir) / "roots"


def store_object(target_dir: str, obj: dict) -> str:
    data = json.dumps(obj, sort_keys=True).encode("utf-8")
    h = _hash_bytes(data)

    obj_dir = _objects_dir(target_dir)
    obj_dir.mkdir(parents=True, exist_ok=True)

    path = obj_dir / f"{h}.json"

    if not path.exists():
        path.write_bytes(data)

    return h


def load_object(target_dir: str, obj_hash: str) -> dict | None:
    path = _objects_dir(target_dir) / f"{obj_hash}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_root(target_dir: str, root_hash: str, payload: dict):
    roots_dir = _roots_dir(target_dir)
    roots_dir.mkdir(parents=True, exist_ok=True)

    path = roots_dir / f"{root_hash}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return str(path)


def load_root(target_dir: str, root_hash: str):
    path = _roots_dir(target_dir) / f"{root_hash}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
