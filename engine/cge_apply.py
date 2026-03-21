from pathlib import Path
import json


def apply_state(target_dir: str, objects: list):
    """
    Controlled apply:
    writes reconstructed state into /restored_state/
    """

    out_dir = Path(target_dir) / "restored_state"
    out_dir.mkdir(parents=True, exist_ok=True)

    for i, obj in enumerate(objects):
        path = out_dir / f"{i}.json"
        path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

    return {
        "status": "applied",
        "object_count": len(objects),
        "output_dir": str(out_dir),
    }
