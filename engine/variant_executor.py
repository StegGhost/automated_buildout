import traceback
from typing import List, Dict, Any

from engine.variant_memory import record_variant_result, get_variant_bias
from engine.variant_policy import pick_variant
from engine.variant_generator import generate_variants


def execute_variants(phase, variants: List[Dict[str, Any]], target_dir, phase_name, install_phase, validate_phase):
    bias = get_variant_bias(target_dir, phase_name)

    # 🔥 LLM-guided generation
    generated = generate_variants(phase, variants, max_new=2)
    all_variants = variants + generated

    results: List[Dict[str, Any]] = []

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
                "generated": variant.get("generated", False),
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
                "generated": variant.get("generated", False),
                "error": traceback.format_exc(),
            })

    selected = pick_variant(results)

    return results, selected
