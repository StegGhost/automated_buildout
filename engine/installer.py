import os


def apply_code(target_dir: str, code: str, filename: str):
    path = os.path.join(target_dir, filename)

    with open(path, "w") as f:
        f.write(code)


def install_phase(phase, target_dir: str):
    # 🔥 NEW: consensus-aware
    if hasattr(phase, "generate_candidates"):
        from engine.phase_consensus import execute_consensus_phase

        result = execute_consensus_phase(phase)

        code = result["selected_code"]

        filename = getattr(phase, "output_file", "generated.py")

        apply_code(target_dir, code, filename)

        return {
            "installed": True,
            "mode": "consensus",
            "consensus_receipt": result["consensus_receipt"]
        }

    # fallback
    phase(target_dir)

    return {"installed": True, "mode": "direct"}
