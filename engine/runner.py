from pathlib import Path
import json
import hashlib
import uuid

from engine.planner import load_phases
from engine.installer import install_phase
from engine.validator import validate_phase
from engine.receipt_writer import write_phase_receipt
from engine.auto_upgrade import ensure_cge
from engine.build_health import compute_health
from engine.replay import replay_build
from engine.merkle import build_merkle_tree
from engine.run_registry import load_registry, save_registry
from engine.run_meta import write_run_meta
from engine.phase_registry import load_phase_registry, save_phase_registry

# CGE
from engine.cge_adapter import export_run_to_cge
from engine.cge_registry import load_latest_root, save_latest_root


def _hash_manifest(manifest: dict) -> str:
    payload = json.dumps(manifest, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _runs_dir(target_dir: str) -> Path:
    return Path(target_dir) / ".buildout_runs"


def run_build(target_dir=None, manifest_path: str = "manifests/example_manifest.json"):
    ensure_cge()

    phases, manifest = load_phases(manifest_path)

    if target_dir is None:
        target_dir = manifest["target_dir"]

    runs_dir = _runs_dir(target_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)

    registry = load_registry(target_dir)
    phase_registry = load_phase_registry(target_dir)

    manifest_hash = _hash_manifest(manifest)

    # idempotency
    existing = registry.get(manifest_hash)
    if existing:
        return {
            "status": "replayed",
            "canonical_hash": manifest_hash,
            "run_id": existing.get("run_id"),
        }

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
    replay_result = replay_build(receipts)
    merkle = build_merkle_tree(receipts, run_dir)

    run_result = {
        "status": "failed" if failed else "success",
        "run_id": run_id,
        "results": results,
        "receipts": receipts,
        "health": health,
    }

    # 🔥 CGE EXPORT
    previous_root = load_latest_root(target_dir)

    cge_result = export_run_to_cge(target_dir, run_result, previous_root)

    save_latest_root(target_dir, cge_result["global_root"])

    write_run_meta(
        run_dir,
        {
            "run_id": run_id,
            "manifest_hash": manifest_hash,
            "status": run_result["status"],
        },
    )

    if not failed:
        registry[manifest_hash] = {
            "run_id": run_id,
            "runs": len(registry) + 1,
        }
        save_registry(target_dir, registry)
        save_phase_registry(target_dir, phase_registry)

    return {
        **run_result,
        "cge": cge_result,
        "merkle": merkle,
        "replay_result": replay_result,
    }
