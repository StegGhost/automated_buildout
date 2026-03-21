from engine.planner import load_phases
from engine.installer import install_phase
from engine.validator import validate_phase
from engine.receipt_writer import write_phase_receipt
from engine.auto_upgrade import ensure_cge
from engine.build_health import compute_health
from engine.replay import replay_build
from engine.state_lock import acquire_lock, release_lock


def run_build(target_dir=None, manifest_path: str = "manifests/example_manifest.json"):
    ensure_cge()

    phases, manifest = load_phases(manifest_path)

    if target_dir is None:
        target_dir = manifest["target_dir"]

    # 🔥 acquire lock
    lock = acquire_lock(target_dir)
    if not lock.get("acquired"):
        return {"status": "locked"}

    results = []
    receipts = []

    parent_hash = None
    failed = False

    try:
        for phase in phases:
            name = getattr(phase, "__name__", str(phase))

            install_result = install_phase(phase, target_dir)
            validation = validate_phase(phase, target_dir)

            receipt = write_phase_receipt(
                target_dir,
                name,
                install_result,
                validation,
                parent_hash,
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

        # 🔥 replay validation
        replay_result = replay_build(receipts)

        # 🔥 health
        health = compute_health(results)

        return {
            "status": "failed" if failed else "success",
            "results": results,
            "receipts": receipts,
            "health": health,
            "replay_result": replay_result,
        }

    finally:
        # 🔥 ALWAYS release lock
        release_lock(target_dir)
