from engine.planner import load_phases
from engine.installer import install_phase
from engine.validator import validate_phase
from engine.receipt_writer import write_phase_receipt
from engine.build_health import compute_health
from engine.run_manager import create_run, get_latest_run
from engine.replay import replay_build
from engine.lineage import write_lineage

from engine.cge_adapter import (
    build_canonical_run_receipt,
    write_canonical_receipt,
    compute_merkle_root,
    write_merkle_proof,
)

# 🔥 NEW
from engine.idempotency import detect_replay


def run_build(target_dir=None, manifest_path: str = "manifests/example_manifest.json"):
    phases, manifest = load_phases(manifest_path)

    if target_dir is None:
        target_dir = manifest["target_dir"]

    prev_run_id = get_latest_run(target_dir)

    run = create_run(target_dir)
    run_id = run["run_id"]

    write_lineage(target_dir, run_id, prev_run_id)

    results = []
    receipts = []

    parent_hash = None
    failed = False

    for phase in phases:
        name = getattr(phase, "__name__", str(phase))

        install_result = install_phase(phase, target_dir)
        validation = validate_phase(phase, target_dir)

        receipt = write_phase_receipt(
            target_dir=target_dir,
            run_id=run_id,
            phase_name=name,
            install_result=install_result,
            validation_result=validation,
            parent_hash=parent_hash,
        )

        parent_hash = receipt["receipt_hash"]
        receipts.append(receipt)

        valid = validation.get("valid", True)

        results.append({
            "phase": name,
            "valid": valid,
            "receipt_hash": parent_hash,
        })

        if not valid:
            failed = True
            break

    health = compute_health(results)

    replay_result = replay_build(target_dir, run_id)

    run_result = {
        "status": "failed" if failed else "success",
        "run_id": run_id,
        "parent_run_id": prev_run_id,
        "results": results,
        "receipts": receipts,
        "health": health,
        "replay_result": replay_result,
    }

    # 🔹 CGE layer
    canonical = build_canonical_run_receipt(run_result)
    canonical_path = write_canonical_receipt(target_dir, run_id, canonical)

    merkle_root = compute_merkle_root(receipts)
    merkle_path = write_merkle_proof(target_dir, run_id, merkle_root)

    # 🔥 IDENTITY CHECK (NEW)
    is_replay = detect_replay(target_dir, run_id, prev_run_id)

    if is_replay:
        run_result["status"] = "replayed"

    run_result["cge"] = {
        "canonical_hash": canonical["canonical_hash"],
        "canonical_path": canonical_path,
        "merkle_root": merkle_root,
        "merkle_path": merkle_path,
        "is_replay": is_replay,
    }

    return run_result
