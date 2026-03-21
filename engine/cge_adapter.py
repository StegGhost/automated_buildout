from engine.cge_store import store_object, write_root
from engine.cge_chain import link_roots


def export_run_to_cge(target_dir: str, run_result: dict, previous_root: str | None):
    """
    Convert run_result → CGE canonical objects
    """

    objects = []

    # store each receipt
    for r in run_result.get("receipts", []):
        h = store_object(target_dir, r)
        objects.append(h)

    # build root payload
    root_payload = {
        "run_id": run_result.get("run_id"),
        "status": run_result.get("status"),
        "objects": objects,
        "health": run_result.get("health"),
    }

    root_hash = store_object(target_dir, root_payload)

    # link chain
    global_root = link_roots(previous_root, root_hash)

    write_root(
        target_dir,
        global_root,
        {
            "root": root_hash,
            "prev": previous_root,
            "global_root": global_root,
        },
    )

    return {
        "root_hash": root_hash,
        "global_root": global_root,
        "object_count": len(objects),
    }
