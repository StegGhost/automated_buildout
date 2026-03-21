import traceback


def execute_variants(variants, target_dir, install_phase, validate_phase):
    results = []

    for variant in variants:
        name = variant.get("name")
        fn = variant.get("callable")

        try:
            install_result = install_phase(fn, target_dir)
            validation = validate_phase(fn, target_dir)

            score = 1.0 if validation.get("valid", True) else 0.0

            results.append({
                "variant": name,
                "callable": fn,
                "install_result": install_result,
                "validation": validation,
                "score": score,
                "error": None,
            })

        except Exception as e:
            results.append({
                "variant": name,
                "callable": fn,
                "install_result": {"status": "error"},
                "validation": {"valid": False},
                "score": 0.0,
                "error": traceback.format_exc(),
            })

    return results


def select_best_variant(results):
    # highest score wins
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[0]
