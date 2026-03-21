from engine.planner import load_phases
from engine.installer import install_phase
from engine.validator import validate_phase
from engine.receipt_writer import write_phase_receipt
from engine.auto_upgrade import ensure_cge
from engine.build_health import compute_health
from engine.replay import replay_build
from engine.state_lock import acquire_lock, release_lock
from engine.receipt_loader import load_existing_receipts
from engine.variant_executor import execute_variants


def run_build(target_dir=None, manifest_path: str = "manifests/example_manifest.json"):
    ensure_cge()

    phases, manifest = load_phases(manifest_path)

    if target_dir is None:
        target_dir = manifest["target_dir"]

    # idempotency
    existing_receipts = load_existing_receipts(target_dir)

    if existing_receipts:
        replay_result = replay_build(existing_receipts)

        if replay_result.get("status") == "ok":
            return {
                "status": "replayed",
                "receipts": existing_receipts,
                "health": {
                    "health_score": 1.0,
                    "total_phases": len(existing_receipts),
                    "passed": len(existing_receipts),
                },
                "replay_result": replay_result,
            }

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

            if hasattr(phase, "variants"):
                variant_results, selected = execute_variants(
                    phase,
                    phase.variants(),
                    target_dir,
                    name,
                    install_phase,
                    validate_phase,
                )

                install_result = selected["install_result"]
                validation = selected["validation"]
                selected_variant = selected["variant"]
                variant_score = selected["score"]

            else:
                install_result = install_phase(phase, target_dir)
                validation = validate_phase(phase, target_dir)
                selected_variant = None
                variant_score = None

            receipt = write_phase_receipt(
                target_dir,
                name,
                install_result,
                validation,
                parent_hash,
            )

            receipt["selected_variant"] = selected_variant
            receipt["variant_score"] = variant_score

            parent_hash = receipt["receipt_hash"]
            receipts.append(receipt)

            valid = validation.get("valid", True)

            results.append({
                "phase": name,
                "valid": valid,
                "receipt_hash": parent_hash,
                "variant": selected_variant,
                "score": variant_score,
            })

            if not valid:
                failed = True
                break

        replay_result = replay_build(receipts)
        health = compute_health(results)

        return {
            "status": "failed" if failed else "success",
            "results": results,
            "receipts": receipts,
            "health": health,
            "replay_result": replay_result,
        }

    finally:
        release_lock(target_dir)
