import traceback
from engine.variant_memory import record_variant_result, get_variant_bias
from engine.variant_policy import pick_variant
from engine.variant_generator import generate_variants


def execute_variants(variants, target_dir, phase_name, install_phase, validate_phase):
    bias = get_variant_bias(target_dir, phase_name)

    # 🔥 NEW: generate additional variants
    generated = generate_variants(type("P", (), {"variants": lambda: variants}))
    all_variants = variants + generated

    results = []

    for variant in all_variants:
        name = variant.get("name")
        fn = variant.get("callable")

        try:
            install_result = install_phase(fn, target_dir)
            validation = validate_phase(fn, target_dir)

            base_score = 1.0 if validation.get("valid", True) else 0.0
            bias_score = bias.get(name, 0.0)

            final_score = base_score + (0.25 * bias_score)

            result = {
                "variant": name,
                "callable": fn,
                "install_result": install_result,
                "validation": validation,
                "score": final_score,
                "base_score": base_score,
                "bias_score": bias_score,
                "error": None,
            }

            results.append(result)

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

    selected = pick_variant(results)

    return results, selected
