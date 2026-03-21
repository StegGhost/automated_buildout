import hashlib
import json
import uuid
from pathlib import Path

from engine.planner import load_phases
from engine.installer import install_phase
from engine.validator import validate_phase
from engine.receipt_writer import write_phase_receipt
from engine.auto_upgrade import ensure_cge
from engine.build_health import compute_health
from engine.replay import replay_build
from engine.run_diff import compare_runs
from engine.cge_adapter import (
    build_canonical_run_receipt,
    write_canonical_receipt,
    compute_merkle_root,
    write_merkle_proof,
)


def _get_runs_dir(target_dir):
    return Path(target_dir) / ".buildout_runs"


def _get_latest_run_dir(target_dir):
    runs_dir = _get_runs_dir(target_dir)
    if not runs_dir.exists():
        return None

    runs = sorted(
        [p for p in runs_dir.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
    )
    return runs[-1] if runs else None


def _compute_build_signature(manifest_path: str, phases: list):
    manifest_text = Path(manifest_path).read_text(encoding="utf-8")
    phase_names = [getattr(p, "__name__", str(p)) for p in phases]

    payload = {
        "manifest": manifest_text,
        "phases": phase_names,
    }

    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _write_run_meta(run_dir: Path, run_id: str, build_signature: str):
    payload = {
        "run_id": run_id,
        "build_signature": build_signature,
    }
    (run_dir / "run_meta.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _load_run_meta(run_dir: Path):
    path = run_dir / "run_meta.json"
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_existing_run_result(run_dir: Path):
    receipts = replay_build(run_dir)
    receipt_files = []

    for f in sorted(run_dir.glob("*.json")):
        if f.name in {"canonical_receipt.json", "merkle.json", "diff_report.json", "run_meta.json", "lineage.json"}:
            continue

        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue

        if "phase" in data and "receipt_hash" in data:
            receipt_files.append(data)

    receipt_files.sort(key=lambda x: x.get("timestamp", 0))

    results = [
        {
            "phase": r.get("phase"),
            "valid": r.get("validation_result", {}).get("valid", True),
            "receipt_hash": r.get("receipt_hash"),
        }
        for r in receipt_files
    ]

    health = compute_health(results)

    canonical_path = run_dir / "canonical_receipt.json"
    merkle_path = run_dir / "merkle.json"

    canonical = None
    merkle = None

    if canonical_path.exists():
        try:
            canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
        except Exception:
            canonical = None

    if merkle_path.exists():
        try:
            merkle = json.loads(merkle_path.read_text(encoding="utf-8"))
        except Exception:
            merkle = None

    return {
        "status": "replayed" if receipts.get("status") == "ok" else "failed",
        "results": results,
        "receipts": receipt_files,
        "health": health,
        "replay_result": receipts,
        "run_id": run_dir.name,
        "cge": {
            "canonical_hash": canonical.get("canonical_hash") if canonical else None,
            "canonical_path": str(canonical_path) if canonical_path.exists() else None,
            "merkle_root": merkle.get("root") if merkle else None,
            "merkle_path": str(merkle_path) if merkle_path.exists() else None,
            "is_replay": True,
        },
    }


def run_build(target_dir=None, manifest_path: str = "manifests/example_manifest.json"):
    ensure_cge()

    phases, manifest = load_phases(manifest_path)

    if target_dir is None:
        target_dir = manifest["target_dir"]

    runs_dir = _get_runs_dir(target_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)

    build_signature = _compute_build_signature(manifest_path, phases)

    previous_run_dir = _get_latest_run_dir(target_dir)

    # ✅ PRE-RUN IDEMPOTENCY GATE
    if previous_run_dir is not None:
        prev_meta = _load_run_meta(previous_run_dir)
        prev_replay = replay_build(previous_run_dir)

        if (
            prev_meta
            and prev_meta.get("build_signature") == build_signature
            and prev_replay.get("status") == "ok"
        ):
            return _load_existing_run_result(previous_run_dir)

    run_id = str(uuid.uuid4())
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    _write_run_meta(run_dir, run_id, build_signature)

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

    # ✅ REPLAY CURRENT RUN FROM IN-MEMORY RECEIPTS
    replay_result = replay_build(receipts)

    run_result = {
        "status": "failed" if failed else "success",
        "run_id": run_id,
        "parent_run_id": previous_run_dir.name if previous_run_dir else None,
        "results": results,
        "receipts": receipts,
        "health": health,
        "replay_result": replay_result,
    }

    canonical = build_canonical_run_receipt(run_result)
    canonical_path = write_canonical_receipt(target_dir, run_id, canonical)

    merkle_root = compute_merkle_root(receipts)
    merkle_path = write_merkle_proof(target_dir, run_id, merkle_root)

    diff_result = None
    if previous_run_dir and previous_run_dir.exists():
        diff_result = compare_runs(str(previous_run_dir), str(run_dir))
        (run_dir / "diff_report.json").write_text(
            json.dumps(diff_result, indent=2),
            encoding="utf-8",
        )

    run_result["cge"] = {
        "canonical_hash": canonical.get("canonical_hash"),
        "canonical_path": canonical_path,
        "merkle_root": merkle_root,
        "merkle_path": merkle_path,
        "is_replay": False,
    }

    run_result["diff_result"] = diff_result

    return run_result
