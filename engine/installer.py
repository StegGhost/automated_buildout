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
    - module phases (with run function inside)
    - callable phases
    """

    # 🔥 CONSENSUS MODE
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

    # 🔥 MODULE MODE (FIXED)
    if isinstance(phase, types.ModuleType):
        if hasattr(phase, "run"):
            phase.run(target_dir)
            return {"installed": True, "mode": "module"}

        # 🔥 HANDLE nested module import case
        for attr in dir(phase):
            obj = getattr(phase, attr)
            if callable(obj) and attr == "run":
                obj(target_dir)
                return {"installed": True, "mode": "module"}

    # 🔥 FUNCTION MODE
    if callable(phase):
        phase(target_dir)
        return {"installed": True, "mode": "function"}

    raise TypeError(f"Invalid phase type: {type(phase)}")
