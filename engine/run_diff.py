import json
from pathlib import Path


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _load_run(run_dir: Path):
    """
    Load canonical + merkle + receipts for a run.
    """
    canonical = _load_json(run_dir / "canonical_receipt.json")
    merkle = _load_json(run_dir / "merkle.json")

    receipts = []
    receipts_dir = run_dir

    for f in sorted(receipts_dir.glob("*phase*.json")):
        data = _load_json(f)
        if data:
            receipts.append(data)

    return {
        "canonical": canonical,
        "merkle": merkle,
        "receipts": receipts,
    }


def _index_phases(receipts):
    """
    Index receipts by phase name.
    """
    out = {}
    for r in receipts:
        phase = r.get("phase")
        if phase:
            out[phase] = r
    return out


def compare_runs(run_a_path: str, run_b_path: str):
    """
    Compare two run directories.
    """

    run_a = Path(run_a_path)
    run_b = Path(run_b_path)

    data_a = _load_run(run_a)
    data_b = _load_run(run_b)

    phases_a = _index_phases(data_a["receipts"])
    phases_b = _index_phases(data_b["receipts"])

    all_phases = sorted(set(phases_a.keys()) | set(phases_b.keys()))

    phase_diffs = []

    for p in all_phases:
        ra = phases_a.get(p)
        rb = phases_b.get(p)

        if ra and not rb:
            phase_diffs.append({
                "phase": p,
                "type": "removed",
            })
            continue

        if rb and not ra:
            phase_diffs.append({
                "phase": p,
                "type": "added",
            })
            continue

        # compare hashes
        if ra.get("receipt_hash") != rb.get("receipt_hash"):
            phase_diffs.append({
                "phase": p,
                "type": "modified",
                "hash_a": ra.get("receipt_hash"),
                "hash_b": rb.get("receipt_hash"),
            })

    # canonical diff
    canonical_diff = None
    if data_a["canonical"] and data_b["canonical"]:
        if data_a["canonical"].get("receipt_hash") != data_b["canonical"].get("receipt_hash"):
            canonical_diff = {
                "changed": True,
                "hash_a": data_a["canonical"].get("receipt_hash"),
                "hash_b": data_b["canonical"].get("receipt_hash"),
            }

    # merkle diff
    merkle_diff = None
    if data_a["merkle"] and data_b["merkle"]:
        if data_a["merkle"].get("root") != data_b["merkle"].get("root"):
            merkle_diff = {
                "changed": True,
                "root_a": data_a["merkle"].get("root"),
                "root_b": data_b["merkle"].get("root"),
            }

    return {
        "status": "ok",
        "run_a": str(run_a),
        "run_b": str(run_b),
        "phase_diffs": phase_diffs,
        "canonical_diff": canonical_diff,
        "merkle_diff": merkle_diff,
        "summary": {
            "total_phases": len(all_phases),
            "changed_phases": len(phase_diffs),
        }
    }
