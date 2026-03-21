import uuid
from pathlib import Path
import json

from engine.planner import load_phases
from engine.installer import install_phase
from engine.validator import validate_phase
from engine.receipt_writer import write_phase_receipt
from engine.auto_upgrade import ensure_cge
from engine.build_health import compute_health
from engine.replay import replay_build
from engine.merkle import build_merkle_tree
from engine.run_diff import compare_runs


def _get_runs_dir(target_dir):
    return Path(target_dir) / ".buildout_runs"


def _get_latest_run_dir(target_dir):
    runs_dir = _get_runs_dir(target_dir)
    if not runs_dir.exists():
        return None

    runs = sorted(runs_dir.glob("*"), key=lambda p: p.stat().st_mtime)
    return runs[-1] if runs else None


def run_build(target_dir=None, manifest_path: str = "manifests/example_manifest.json"):
    ensure_cge()

    phases, manifest = load_phases(manifest_path)

    if target_dir is None:
        target_dir = manifest["target_dir"]

    runs_dir = _get_runs_dir(target_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)

    previous_run_dir = _get_latest_run_dir(target_dir)

    run_id = str(uuid.uuid4())
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    results = []
    receipts = []

    parent_hash = None
    failed = False

    for phase in phases:
        name = getattr(phase, "__name__", str(phase))

        install_result = install_phase(phase, target_dir)
        validation = validate_phase(phase, target_dir)

        receipt = write_phase_receipt(
            target_dir=run_dir,
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

    # FIXED: replay is now run-scoped
    replay_result = replay_build(target_dir, run_id)

    merkle = build_merkle_tree(receipts, run_dir)

    canonical = {
        "receipt_hash": parent_hash,
        "run_id": run_id,
        "total_phases": len(receipts),
    }

    (run_dir / "canonical_receipt.json").write_text(
        json.dumps(canonical, indent=2)
    )

    diff_result = None
    if previous_run_dir and previous_run_dir.exists():
        diff_result = compare_runs(previous_run_dir, run_dir)

        (run_dir / "diff_report.json").write_text(
            json.dumps(diff_result, indent=2)
        )

    return {
        "status": "failed" if failed else "success",
        "results": results,
        "receipts": receipts,
        "health": health,
        "replay_result": replay_result,
        "merkle": merkle,
        "diff_result": diff_result,
        "run_id": run_id,
    }
