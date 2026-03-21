existing = registry.get(manifest_hash)
if existing:
    previous_root = load_latest_root(target_dir)

    return {
        "status": "replayed",
        "canonical_hash": manifest_hash,
        "run_id": existing.get("run_id"),
        "results": [],
        "receipts": [],
        "health": {
            "health_score": 1.0,
            "total_phases": 0,
            "passed": 0,
        },
        "replay_result": {
            "status": "ok",
            "total": 0,
        },
        "merkle": {
            "root": None,
            "leaf_count": 0,
        },
        "cge": {
            "global_root": previous_root,
            "object_count": 0,
        },
    }
