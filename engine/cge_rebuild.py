from engine.cge_store import load_root, load_object


def rebuild_state(target_dir: str, global_root: str):
    root = load_root(target_dir, global_root)

    if not root:
        return {"status": "not_found"}

    object_hashes = root.get("objects", [])

    objects = []
    for h in object_hashes:
        obj = load_object(target_dir, h)
        if obj:
            objects.append(obj)

    return {
        "status": "ok",
        "root": global_root,
        "objects": objects,
        "count": len(objects),
    }
