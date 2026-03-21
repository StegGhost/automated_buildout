from engine.cge_store import load_root, load_object


def rebuild_state(target_dir: str, global_root: str):
    """
    Rebuild state from a CGE global root.

    Flow:
    1. load global root record
    2. extract canonical root object hash
    3. load canonical root object
    4. load referenced objects
    """

    root_record = load_root(target_dir, global_root)

    if not root_record:
        return {"status": "not_found", "count": 0}

    root_hash = root_record.get("root")
    if not root_hash:
        return {"status": "invalid_root", "count": 0}

    root_obj = load_object(target_dir, root_hash)
    if not root_obj:
        return {"status": "missing_root_object", "count": 0}

    object_hashes = root_obj.get("objects", [])

    objects = []
    for h in object_hashes:
        obj = load_object(target_dir, h)
        if obj:
            objects.append(obj)

    return {
        "status": "ok",
        "global_root": global_root,
        "root": root_hash,
        "objects": objects,
        "count": len(objects),
    }
