import json
from pathlib import Path


MEMORY_FILE = ".buildout_memory/variants.json"


def _load_memory(target_dir):
    path = Path(target_dir) / MEMORY_FILE
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_memory(target_dir, data):
    path = Path(target_dir) / MEMORY_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def record_variant_result(target_dir, phase_name, variant_name, score):
    memory = _load_memory(target_dir)

    phase_mem = memory.setdefault(phase_name, {})
    variant_mem = phase_mem.setdefault(variant_name, {
        "wins": 0,
        "attempts": 0,
        "score_total": 0.0,
        "generated": "_gen" in variant_name,
    })

    variant_mem["attempts"] += 1
    variant_mem["score_total"] += score

    if score >= 1.0:
        variant_mem["wins"] += 1

    _save_memory(target_dir, memory)


def get_variant_bias(target_dir, phase_name):
    memory = _load_memory(target_dir)
    phase_mem = memory.get(phase_name, {})

    scores = {}
    for variant, stats in phase_mem.items():
        attempts = stats.get("attempts", 1)
        total = stats.get("score_total", 0.0)
        scores[variant] = total / attempts

    return scores
