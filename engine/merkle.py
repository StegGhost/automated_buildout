import hashlib
import json
from pathlib import Path


def _hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def _hash_receipt(receipt: dict) -> str:
    return _hash(json.dumps(receipt, sort_keys=True))


def build_merkle_tree(receipts: list, run_dir: Path):
    """
    Builds a simple merkle tree from receipts.
    """

    if not receipts:
        return {
            "root": None,
            "nodes": []
        }

    # Step 1: leaf hashes
    leaves = [_hash_receipt(r) for r in receipts]

    tree = [leaves]

    # Step 2: build tree upward
    current = leaves

    while len(current) > 1:
        next_level = []

        for i in range(0, len(current), 2):
            left = current[i]
            right = current[i + 1] if i + 1 < len(current) else left

            combined = _hash(left + right)
            next_level.append(combined)

        tree.append(next_level)
        current = next_level

    root = current[0]

    merkle_data = {
        "root": root,
        "levels": tree,
        "leaf_count": len(leaves),
    }

    # write to disk
    (run_dir / "merkle.json").write_text(
        json.dumps(merkle_data, indent=2)
    )

    return merkle_data
