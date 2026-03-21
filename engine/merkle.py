import hashlib
import json
from pathlib import Path


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _hash_receipt(receipt: dict) -> str:
    return _hash(json.dumps(receipt, sort_keys=True))


def build_merkle_tree(receipts: list, run_dir: Path):
    if not receipts:
        data = {"root": None, "levels": [], "leaf_count": 0}
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "merkle.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data

    leaves = [_hash_receipt(r) for r in receipts]
    tree = [leaves]
    current = leaves

    while len(current) > 1:
        next_level = []
        for i in range(0, len(current), 2):
            left = current[i]
            right = current[i + 1] if i + 1 < len(current) else left
            next_level.append(_hash(left + right))
        tree.append(next_level)
        current = next_level

    data = {
        "root": current[0],
        "levels": tree,
        "leaf_count": len(leaves),
    }

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "merkle.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data
