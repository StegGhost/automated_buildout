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
from engine.phase_signature import hash_phase_signature
from engine.state_diff import compute_phase_state, should_rebuild


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

    # full replay shortcut
    existing = registry.get(manifest_hash)
    if existing:
        return {
            "status": "replayed",
            "canonical_hash": manifest_hash,
            "results": [],
            "receipts": [],
            "health": {"health_score": 1.0, "total_phases": 0, "passed": 0},
            "replay_result": {"status": "ok"},
            "merkle": None,
            "run_id": existing.get("run_id"),
        }

    run_id = str(uuid.uuid4())
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    results = []
    receipts = []
    parent_hash = None
    failed = False

    dirty = False  # 🔥 propagation flag

    for phase in phases:
        name = getattr(phase, "__name__", str(phase))

        phase_sig = hash_phase_signature(name, manifest)
        prior = phase_registry.get(name)

        # --- simulate execution to compute state ---
        install_result = install_phase(phase, target_dir)
        validation = validate_phase(phase, target_dir)

        state_hash = compute_phase_state(name, install_result, validation)

        rebuild = should_rebuild(name, state_hash, phase_registry, dirty)

        if not rebuild:
            install_result = {
                "installed": True,
                "status": "replayed",
                "mode": "state_match",
            }
            validation = {"valid": True, "replayed": True}
        else:
            dirty = True  # 🔥 once dirty, downstream stays dirty

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
            "replayed": not rebuild,
        })

        if valid:
            phase_registry[name] = {
                "signature": phase_sig,
                "state_hash": state_hash,
                "last_run_id": run_id,
                "receipt_hash": parent_hash,
            }

        if not valid:
            failed = True
            break

    health = compute_health(results)
    replay_result = replay_build(receipts)
    merkle = build_merkle_tree(receipts, run_dir)

    write_run_meta(
        run_dir,
        {
            "run_id": run_id,
            "manifest_path": manifest_path,
            "manifest_hash": manifest_hash,
            "status": "failed" if failed else "success",
            "phase_count": len(results),
            "receipt_count": len(receipts),
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
        "status": "failed" if failed else "success",
        "canonical_hash": manifest_hash,
        "results": results,
        "receipts": receipts,
        "health": health,
        "replay_result": replay_result,
        "merkle": merkle,
        "run_id": run_id,
    }
