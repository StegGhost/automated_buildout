import os
from engine.phase_consensus import execute_consensus_phase
from engine.fitness import score_phase
from engine.registry import save_best_phase


def apply_code(target_dir: str, code: str, filename: str):
    path = os.path.join(target_dir, filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        f.write(code)


def _get_phase_name(phase):
    """
    Universal phase name resolver.
    Works for:
    - instances
    - classes
    - modules
    """
    if hasattr(phase, "name"):
        return phase.name

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

    # 🧬 mutation path
    if hasattr(phase, "mutate"):
        candidates = phase.mutate()
        result = execute_consensus_phase(phase, candidates=candidates)

    elif hasattr(phase, "generate_candidates"):
        result = execute_consensus_phase(phase)

    # 🧱 module path
    elif hasattr(phase, "__name__"):
        _run_module_phase(phase, target_dir)

        return {
            "installed": True,
            "mode": "module",
            "status": "ok",
        }

    else:
        raise TypeError(f"Unsupported phase type: {phase}")

    # ✅ consensus path
    code = result["selected_code"]
    receipt = result["consensus_receipt"]

    filename = getattr(phase, "output_file", "generated.py")

    apply_code(target_dir, code, filename)

    score = score_phase({"valid": True}, receipt)

    save_best_phase(target_dir, phase_name, code, score)

    return {
        "installed": True,
        "mode": "consensus",
        "consensus_receipt": receipt,
        "score": score,
    }
