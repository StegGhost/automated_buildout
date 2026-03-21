from engine.cge_registry import load_latest_root
from engine.cge_store import load_root


def get_lineage(target_dir: str, start_root: str):
    lineage = []
    current = start_root

    while current:
        root = load_root(target_dir, current)
        if not root:
            break

        lineage.append({
            "root": current,
            "prev": root.get("prev"),
        })

        current = root.get("prev")

    return lineage


def forward_to_latest(target_dir: str, start_root: str):
    latest = load_latest_root(target_dir)

    if not latest:
        return {"status": "no_latest"}

    lineage = get_lineage(target_dir, latest)

    # reverse for forward direction
    lineage = list(reversed(lineage))

    forward_path = []
    found = False

    for entry in lineage:
        if entry["root"] == start_root:
            found = True
            continue

        if found:
            forward_path.append(entry["root"])

    return {
        "status": "ok",
        "from": start_root,
        "to": latest,
        "path": forward_path,
    }
