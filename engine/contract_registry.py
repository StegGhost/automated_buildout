import importlib


REQUIRED_CONTRACTS = {
    "engine.receipt_writer": ["write_phase_receipt"],
    "engine.runner": ["run_build"],
    "engine.replay": ["replay_build"],
}


def validate_contracts():
    failures = []

    for module_path, functions in REQUIRED_CONTRACTS.items():
        try:
            module = importlib.import_module(module_path)
        except Exception as e:
            failures.append({
                "module": module_path,
                "reason": "module_import_error",
                "error": str(e),
            })
            continue

        for fn in functions:
            if not hasattr(module, fn):
                failures.append({
                    "module": module_path,
                    "reason": "missing_contract_function",
                    "missing": fn,
                })

    return {
        "valid": len(failures) == 0,
        "failures": failures,
    }
