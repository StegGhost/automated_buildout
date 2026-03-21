import json
from pathlib import Path
from typing import Any


def _validate_chain(receipts: list):
    if not receipts:
        return {"status": "empty"}

    receipts = sorted(receipts, key=lambda x: x.get("timestamp", 0))

    for i in range(1, len(receipts)):
        prev = receipts[i - 1]
        curr = receipts[i]

        if curr.get("parent_hash") != prev.get("receipt_hash"):
            return {
                "status": "invalid",
                "reason": "chain_break",
                "index": i,
            }

    return {"status": "ok", "total": len(receipts)}


def _load_receipts_from_run_dir(run_dir: Path):
    if not run_dir.exists():
        return []

    receipts = []

    for f in sorted(run_dir.glob("*.json")):
        if f.name in {"canonical_receipt.json", "merkle.json", "diff_report.json", "run_meta.json", "lineage.json"}:
            continue

        try:
            data = json.loads(f.read_text())
        except Exception:
            continue

        if "phase" in data and "receipt_hash" in data:
            receipts.append(data)

    return receipts


def replay_build(source: Any, run_id: str | None = None):
    """
    Supports:
    1. replay_build(receipts_list)
    2. replay_build(target_dir, run_id)
    3. replay_build(run_dir_path)
    """
    if isinstance(source, list):
        return _validate_chain(source)

    path = Path(source)

    if run_id is not None:
        run_dir = path / ".buildout_runs" / run_id
    else:
        run_dir = path

    receipts = _load_receipts_from_run_dir(run_dir)
    return _validate_chain(receipts)
