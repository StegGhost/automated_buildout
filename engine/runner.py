from engine.planner import load_phases
from engine.installer import install_phase
from engine.validator import validate_phase

def run_build(target_dir):
    phases = load_phases()

    results = []

    for phase in phases:
        name = phase.__name__

        install_phase(phase, target_dir)
        validation = validate_phase(phase, target_dir)

        results.append({
            "phase": name,
            "valid": validation.get("valid", True),
            "details": validation
        })

        if not validation.get("valid", True):
            return {
                "status": "failed",
                "phase": name,
                "results": results
            }

    return {
        "status": "success",
        "results": results
    }
