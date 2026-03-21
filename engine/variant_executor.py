import traceback
from engine.variant_memory import record_variant_result, get_variant_bias


def execute_variants(variants, target_dir, phase_name, install_phase, validate_phase):
    bias = get_variant_bias(target_dir, phase_name)

    results = []

    for variant in variants:
        name = variant.get("name")
        fn = variant.get("callable")

        try:
            install_result = install_phase(fn, target_dir)
            validation = validate_phase(fn, target_dir)

            base_score = 1.0 if validation.get("valid", True) else 0.0

            # 🔥 APPLY LEARNING BIAS
            bias_score = bias.get(name, 0.0)
            final_score = base_score + (0.25 * bias_score)

            results.append({
                "variant": name,
                "callable": fn,
                "install_result": install_result,
                "validation": validation,
                "score": final_score,
                "base_score": base_score,
                "bias_score": bias_score,
                "error": None,
            })

            # 🔥 record outcome
            record_variant_result(target_dir, phase_name, name, base_score)

        except Exception:
            results.append({
                "variant": name,
                "callable": fn,
                "install_result": {"status": "error"},
                "validation": {"valid": False},
                "score": 0.0,
                "base_score": 0.0,
                "bias_score": 0.0,
                "error": traceback.format_exc(),
            })

    return results


def select_best_variant(results):
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[0]
