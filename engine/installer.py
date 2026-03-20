import os
import types

from engine.fitness import score_phase
from engine.phase_consensus import execute_consensus_phase
from engine.registry import save_best_phase


def apply_code(target_dir: str, code: str, filename: str):
    path = os.path.join(target_dir, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)


def _get_phase_name(phase):
    if hasattr(phase, "name"):
        return phase.name

    if isinstance(phase, types.ModuleType) and hasattr(phase, "__name__"):
        return phase.__name__

    if hasattr(phase, "__class__"):
        return phase.__class__.__name__

    if hasattr(phase, "__name__"):
        return phase.__name__

    return str(phase)


def _run_module_phase(phase_module, target_dir):
    if hasattr(phase_module, "run"):
        return phase_module.run(target_dir)

    raise TypeError(f"Invalid phase module: {phase_module}")


def install_phase(phase, target_dir: str):
    phase_name = _get_phase_name(phase)

    if hasattr(phase, "mutate"):
        candidates = phase.mutate()
        result = execute_consensus_phase(phase, candidates=candidates)

        code = result["selected_code"]
        receipt = result["consensus_receipt"]
        filename = getattr(phase, "output_file", "generated.py")

        apply_code(target_dir, code, filename)

        score = score_phase({"valid": True}, receipt)
        save_best_phase(target_dir, phase_name, code, score)

        return {
            "installed": True,
            "mode": "consensus",
            "status": "ok",
            "consensus_receipt": receipt,
            "score": score,
            "files_created": [filename],
        }

    if hasattr(phase, "generate_candidates"):
        result = execute_consensus_phase(phase)

        code = result["selected_code"]
        receipt = result["consensus_receipt"]
        filename = getattr(phase, "output_file", "generated.py")

        apply_code(target_dir, code, filename)

        score = score_phase({"valid": True}, receipt)
        save_best_phase(target_dir, phase_name, code, score)

        return {
            "installed": True,
            "mode": "consensus",
            "status": "ok",
            "consensus_receipt": receipt,
            "score": score,
            "files_created": [filename],
        }

    if isinstance(phase, types.ModuleType):
        result = _run_module_phase(phase, target_dir)

        if isinstance(result, dict):
            return {
                "installed": True,
                "mode": "module",
                **result,
            }

        return {
            "installed": True,
            "mode": "module",
            "status": "ok",
        }

    if callable(phase):
        result = phase(target_dir)

        if isinstance(result, dict):
            return {
                "installed": True,
                "mode": "function",
                **result,
            }

        return {
            "installed": True,
            "mode": "function",
            "status": "ok",
        }

    raise TypeError(f"Unsupported phase type: {phase}")
