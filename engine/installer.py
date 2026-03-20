import os
from engine.phase_consensus import execute_consensus_phase
from engine.fitness import score_phase
from engine.registry import save_best_phase


def apply_code(target_dir: str, code: str, filename: str):
    path = os.path.join(target_dir, filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        f.write(code)


def _run_module_phase(phase_module, target_dir):
    """
    Supports module-based phases.
    """
    if hasattr(phase_module, "run"):
        return phase_module.run(target_dir)

    raise TypeError(f"Invalid phase module: {phase_module.__name__}")


def install_phase(phase, target_dir: str):
    # 🧬 MUTATION PATH
    if hasattr(phase, "mutate"):
        candidates = phase.mutate()
        result = execute_consensus_phase(phase, candidates=candidates)

    elif hasattr(phase, "generate_candidates"):
        result = execute_consensus_phase(phase)

    # 🧱 MODULE PHASE
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
    save_best_phase(target_dir, phase.__name__, code, score)

    return {
        "installed": True,
        "mode": "consensus",
        "consensus_receipt": receipt,
        "score": score,
    }
