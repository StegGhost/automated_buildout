import json
from pathlib import Path


def export_graph(receipts, target_dir):
    graph = []

    for receipt in receipts:
        graph.append(
            {
                "phase": receipt["phase"],
                "hash": receipt["receipt_hash"],
                "parent": receipt.get("parent_hash"),
            }
        )

    path = Path(target_dir) / "build_graph.json"

    with path.open("w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    return str(path)
