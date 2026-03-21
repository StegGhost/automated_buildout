from engine.cge_store import load_root, load_object


def rebuild_state(target_dir: str, root_hash: str):
    root = load_root(target_dir, root_hash)
    if not root:
        return {"status": "not_found"}

    objects = []
    for h in root.get("objects", []):
        obj = load_object(target_dir, h)
        if obj:
            objects.append(obj)

    return {
        "status": "ok",
        "root": root_hash,
        "objects": objects,
    }
