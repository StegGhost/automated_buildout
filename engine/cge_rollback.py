from engine.cge_store import load_root, load_object


def rollback_to_root(target_dir: str, global_root: str):
    root = load_root(target_dir, global_root)

    if not root:
        return {"status": "not_found", "root": global_root}

    object_hashes = root.get("objects", [])

    objects = []
    for h in object_hashes:
        obj = load_object(target_dir, h)
        if obj:
            objects.append(obj)

    return {
        "status": "ok",
        "global_root": global_root,
        "objects": objects,
    }
