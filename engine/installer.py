import os
import types


def apply_code(target_dir: str, code: str, filename: str):
    path = os.path.join(target_dir, filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)


def install_phase(phase, target_dir: str):
    """
    Supports:
    - consensus phases
    - module phases with run()
    - legacy callable phases
    """

    # Consensus-aware phase
    if hasattr(phase, "generate_candidates"):
        from engine.phase_consensus import execute_consensus_phase

        result = execute_consensus_phase(phase)

        code = result["selected_code"]
        filename = getattr(phase, "output_file", "generated.py")

        apply_code(target_dir, code, filename)

        return {
            "installed": True,
            "mode": "consensus",
            "consensus_receipt": result["consensus_receipt"],
        }

    # Module-based phase
    if isinstance(phase, types.ModuleType) and hasattr(phase, "run"):
        install_result = phase.run(target_dir)

        if isinstance(install_result, dict):
            return {
                "installed": True,
                "mode": "module",
                **install_result,
            }

        return {
            "installed": True,
            "mode": "module",
        }

    # Legacy callable phase
    if callable(phase):
        install_result = phase(target_dir)

        if isinstance(install_result, dict):
            return {
                "installed": True,
                "mode": "function",
                **install_result,
            }

        return {
            "installed": True,
            "mode": "function",
        }

    raise TypeError(
        f"Invalid phase type: {type(phase)}. "
        f"Expected module with run(), consensus phase, or callable."
    )
