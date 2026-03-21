from engine.planner import load_phases
from engine.installer import install_phase
from engine.validator import validate_phase
from engine.receipt_writer import write_phase_receipt
from engine.auto_upgrade import ensure_cge
from engine.build_health import compute_health
from engine.replay import replay_build


def run_build(target_dir=None, manifest_path: str = "manifests/example_manifest.json"):
    ensure_cge()

    phases, manifest = load_phases(manifest_path)

    if target_dir is None:
        target_dir = manifest["target_dir"]

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
    replay_result = replay_build(receipts)

    return {
        "status": "failed" if failed else "success",
        "results": results,
        "receipts": receipts,
        "health": health,
        "replay_result": replay_result,
    }
