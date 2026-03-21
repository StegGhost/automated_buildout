from typing import Dict, Any, List

from engine.variant_selector import select_best_variant


def generate_patch_variants(failure: Dict[str, Any]) -> List[Dict[str, Any]]:
    reason = failure.get("reason", "unknown")
    module = failure.get("module", "")
    missing = failure.get("missing", "")

    variants: List[Dict[str, Any]] = []

    if reason == "missing_contract_function" and module == "engine.receipt_writer" and missing == "write_phase_receipt":
        variants.append({
            "source": "template_primary",
            "valid": True,
            "agreement_ratio": 1.0,
            "penalty": 0.0,
            "target_file": "engine/receipt_writer.py",
            "code": '''import json
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional


def _hash(data: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode("utf-8")
    ).hexdigest()


def write_phase_receipt(
    target_dir: str,
    phase_name: str,
    install_result: Dict[str, Any],
    validation_result: Dict[str, Any],
    parent_hash: Optional[str] = None,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    receipts_dir = Path(target_dir) / ".buildout_receipts"
    if run_id:
        receipts_dir = receipts_dir / run_id
    receipts_dir.mkdir(parents=True, exist_ok=True)

    payload: Dict[str, Any] = {
        "schema_version": "3.0.0",
        "timestamp": time.time(),
        "phase": phase_name,
        "install_result": install_result,
        "validation_result": validation_result,
        "parent_hash": parent_hash,
        "variant_score": install_result.get("score"),
        "consensus_mode": install_result.get("mode"),
    }

    if run_id:
        payload["run_id"] = run_id

    payload["receipt_hash"] = _hash(payload)

    filename = f"{int(payload['timestamp'])}_{phase_name}.json"
    path = receipts_dir / filename

    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)

    payload["receipt_path"] = str(path)
    return payload


def load_existing_receipts(target_dir: str) -> List[Dict[str, Any]]:
    receipts_dir = Path(target_dir) / ".buildout_receipts"

    if not receipts_dir.exists():
        return []

    receipts: List[Dict[str, Any]] = []

    for file in receipts_dir.rglob("*.json"):
        try:
            with file.open("r", encoding="utf-8") as f:
                receipts.append(json.load(f))
        except Exception:
            continue

    receipts.sort(key=lambda x: x.get("timestamp", 0))
    return receipts
''',
        })

    if reason == "missing_contract_function" and module == "engine.replay" and missing == "replay_build":
        variants.append({
            "source": "template_primary",
            "valid": True,
            "agreement_ratio": 1.0,
            "penalty": 0.0,
            "target_file": "engine/replay.py",
            "code": '''import json
from pathlib import Path
from typing import List, Dict, Any


def load_run_receipts(target_dir: str, run_id: str) -> List[Dict[str, Any]]:
    base = Path(target_dir) / ".buildout_receipts" / run_id

    if not base.exists():
        return []

    receipts = []

    for file in base.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            receipts.append(json.load(f))

    receipts.sort(key=lambda x: x.get("timestamp", 0))
    return receipts


def load_previous_run_receipts(target_dir: str, current_run_id: str) -> List[Dict[str, Any]]:
    base = Path(target_dir) / ".buildout_receipts"

    if not base.exists():
        return []

    runs = sorted([p.name for p in base.iterdir() if p.is_dir()])

    if current_run_id not in runs:
        return []

    idx = runs.index(current_run_id)
    if idx == 0:
        return []

    prev_run = runs[idx - 1]
    return load_run_receipts(target_dir, prev_run)


def replay_build(receipts: list):
    if not receipts:
        return {"status": "empty"}

    for i in range(1, len(receipts)):
        prev = receipts[i - 1]
        curr = receipts[i]

        if curr.get("parent_hash") != prev.get("receipt_hash"):
            return {
                "status": "invalid",
                "reason": "chain_break",
                "index": i,
            }

    return {"status": "ok"}
''',
        })

    if reason == "missing_contract_function" and module == "engine.runner" and missing == "run_build":
        variants.append({
            "source": "template_primary",
            "valid": True,
            "agreement_ratio": 1.0,
            "penalty": 0.0,
            "target_file": "engine/runner.py",
            "code": '''from engine.planner import load_phases
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
''',
        })

    return variants


def select_patch_for_failure(failure: Dict[str, Any]) -> Dict[str, Any]:
    variants = generate_patch_variants(failure)
    return select_best_variant(variants)
