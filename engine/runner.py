from engine.planner import load_phases
from engine.installer import install_phase
from engine.validator import validate_phase
from engine.receipt_writer import write_phase_receipt
from engine.auto_upgrade import ensure_cge
from engine.build_health import compute_health
from engine.replay import replay_build, load_previous_run_receipts
from engine.run_context import create_run_id, ensure_run_dir
from engine.migration_validator import validate_migration
from engine.successor_proof import generate_successor_proof
from engine.self_healer import attempt_contract_repair
from engine.fallback_executor import execute_with_fallback


def run_build(target_dir=None, manifest_path: str = "manifests/example_manifest.json"):
    ensure_cge()

    repair_attempt = attempt_contract_repair()
    migration = validate_migration()

    if not migration["valid"]:
        return {
            "status": "failed",
            "reason": "migration_invalid",
            "repair_attempt": repair_attempt,
            "details": migration,
        }

    phases, manifest = load_phases(manifest_path)

    if target_dir is None:
        target_dir = manifest["target_dir"]

    run_id = create_run_id()
    ensure_run_dir(target_dir, run_id)

    results = []
    receipts = []

    parent_hash = None
    failed = False

    for phase in phases:
        name = getattr(phase, "__name__", str(phase))

        try:
            install_result = install_phase(phase, target_dir)
        except Exception:
            install_result = execute_with_fallback(phase, target_dir)

        validation = validate_phase(phase, target_dir)

        receipt = write_phase_receipt(
            target_dir=target_dir,
            phase_name=name,
            install_result=install_result,
            validation_result=validation,
            parent_hash=parent_hash,
            run_id=run_id,
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
    previous_receipts = load_previous_run_receipts(target_dir, run_id)

    successor_proof = generate_successor_proof(
        previous_receipts,
        receipts,
        run_id,
    )

    return {
        "status": "failed" if failed else "success",
        "results": results,
        "receipts": receipts,
        "health": health,
        "replay_result": replay_result,
        "run_id": run_id,
        "migration": migration,
        "repair_attempt": repair_attempt,
        "successor_proof": successor_proof,
    }
