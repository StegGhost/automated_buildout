import importlib
import json
from pathlib import Path
from typing import Any, List, Tuple


DEFAULT_PHASES = [
    "phases.phase_00_seed",
    "phases.phase_01_receipts",
    "phases.phase_02_chain",
]


def load_manifest(manifest_path: str = "manifests/example_manifest.json") -> dict:
    path = Path(manifest_path)
    if not path.exists():
        return {
            "target_dir": "demo_target",
            "phases": DEFAULT_PHASES,
        }

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "target_dir": data.get("target_dir", "demo_target"),
        "phases": data.get("phases", DEFAULT_PHASES),
    }


def normalize_phase_names(phase_names: List[str]) -> List[str]:
    normalized = []
    for name in phase_names:
        if name.startswith("phases."):
            normalized.append(name)
        else:
            normalized.append(f"phases.{name}")
    return normalized


def _is_valid_phase_module(mod: Any) -> bool:
    return (
        hasattr(mod, "run")
        or hasattr(mod, "generate_candidates")
        or hasattr(mod, "mutate")
        or callable(mod)
    )


def load_phases(
    manifest_path: str = "manifests/example_manifest.json",
) -> Tuple[List[Any], dict]:
    manifest = load_manifest(manifest_path)
    phase_names = normalize_phase_names(manifest["phases"])

    loaded = []
    for phase_name in phase_names:
        mod = importlib.import_module(phase_name)

        if not _is_valid_phase_module(mod):
            raise TypeError(
                f"Invalid phase module '{phase_name}'. "
                f"Expected one of: run(), generate_candidates(), mutate(), or callable."
            )

        loaded.append(mod)

    return loaded, manifest
