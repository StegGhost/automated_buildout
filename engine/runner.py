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


def _hash_manifest(manifest: dict) -> str:
    payload = json.dumps(manifest, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def _canonical_registry_path(target_dir: str) -> Path:
    return Path(target_dir) / ".buildout_registry.json"


def _load_registry(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_registry(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def run_build(target_dir=None, manifest_path: str = "manifests/example_manifest.json"):
    ensure_cge()

    phases, manifest = load_phases(manifest_path)

    if target_dir is None:
        target_dir = manifest["target_dir"]

    registry_path = _canonical_registry_path(target_dir)
    registry = _load_registry(registry_path)

    manifest_hash = _hash_manifest(manifest)

    # idempotency pre-check
    if manifest_hash in registry:
        return {
            "status": "replayed",
            "canonical_hash": manifest_hash,
            "results": [],
            "health": {"health_score": 1.0, "total_phases": 0, "passed": 0},
            "replay_result": {"status": "ok"},
        }

    # required by receipt_writer
    run_id = str(uuid.uuid4())

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

    if not failed:
        registry[manifest_hash] = {
            "runs": len(registry) + 1,
            "run_id": run_id,
        }
        _save_registry(registry_path, registry)

    merkle = build_merkle_tree(receipts, Path(target_dir) / ".buildout_runs" / run_id)

    return {
        "status": "failed" if failed else "success",
        "canonical_hash": manifest_hash,
        "results": results,
        "receipts": receipts,
        "health": health,
        "replay_result": replay_result,
        "merkle": merkle,
        "run_id": run_id,
    }
