from engine.planner import load_phases
from engine.installer import install_phase
from engine.validator import validate_phase
from engine.receipt_writer import write_phase_receipt


def run_build(target_dir=None, manifest_path: str = "manifests/example_manifest.json"):
    phases, manifest = load_phases(manifest_path)

    if target_dir is None:
        target_dir = manifest["target_dir"]

    results = []
    receipts = []

    for phase in phases:
        name = phase.__name__

        install_phase(phase, target_dir)
        install_result = {"installed": True}

        validation = validate_phase(phase, target_dir)

        receipt = write_phase_receipt(
            target_dir=target_dir,
            phase_name=name,
            install_result=install_result,
            validation_result=validation,
        )
        receipts.append(receipt)

        phase_result = {
            "phase": name,
            "valid": validation.get("valid", True),
            "details": validation,
            "receipt_hash": receipt["receipt_hash"],
        }
        results.append(phase_result)

        if not validation.get("valid", True):
            return {
                "status": "failed",
                "phase": name,
                "target_dir": target_dir,
                "results": results,
                "receipts": receipts,
            }

    return {
        "status": "success",
        "target_dir": target_dir,
        "results": results,
        "receipts": receipts,
    }
