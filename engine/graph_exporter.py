import json
from pathlib import Path


def export_graph(receipts, target_dir):
    graph = []

    for r in receipts:
        graph.append({
            "phase": r["phase"],
            "hash": r["receipt_hash"],
            "parent": r.get("parent_hash"),
        })

    path = Path(target_dir) / "build_graph.json"

    with open(path, "w") as f:
        json.dump(graph, f, indent=2)

    return str(path)
