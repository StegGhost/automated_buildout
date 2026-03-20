import json
from pathlib import Path


def _phase_dir(target_dir: str, phase_name: str) -> Path:
    path = Path(target_dir) / ".buildout_registry" / phase_name
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_best_phase(target_dir: str, phase_name: str, code: str, score: float):
    phase_path = _phase_dir(target_dir, phase_name)

    best_path = phase_path / "best.py"
    meta_path = phase_path / "history.json"

    with best_path.open("w", encoding="utf-8") as f:
        f.write(code)

    history = []
    if meta_path.exists():
        with meta_path.open("r", encoding="utf-8") as f:
            history = json.load(f)

    history.append({"score": score})

    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def load_best_phase(target_dir: str, phase_name: str):
    path = Path(target_dir) / ".buildout_registry" / phase_name / "best.py"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None
