import traceback

from engine.variant_memory import record_variant_result, get_variant_bias
from engine.variant_policy import pick_variant
from engine.variant_generator import generate_variants
from engine.constraints import evaluate_constraints
from engine.phase_test_runner import run_unit_tests


def execute_variants(phase, variants, target_dir, phase_name, install_phase, validate_phase):
    bias = get_variant_bias(target_dir, phase_name)

    generated = generate_variants(phase, variants, max_new=2)
    all_variants = variants + generated

    results = []

    for variant in all_variants:
        name = variant.get("name")
        fn = variant.get("callable")

        error = None

        try:
            install_result = install_phase(fn, target_dir)
            validation = validate_phase(fn, target_dir)

            test_result = run_unit_tests(fn, target_dir)

            if not test_result["passed"]:
                error = test_result["error"]

            constraint_eval = evaluate_constraints(validation, error)

            base_score = 1.0 if constraint_eval["passed"] else 0.0
            bias_score = bias.get(name, 0.0)

            final_score = base_score + (0.25 * bias_score)

            result = {
                "variant": name,
                "callable": fn,
                "install_result": install_result,
                "validation": validation,
                "tests": test_result,
                "constraints": constraint_eval,
                "score": final_score,
                "base_score": base_score,
                "bias_score": bias_score,
                "generated": variant.get("generated", False),
                "error": error,
            }

            results.append(result)

            record_variant_result(target_dir, phase_name, name, base_score)

        except Exception:
            results.append({
                "variant": name,
                "callable": fn,
                "install_result": {"status": "error"},
                "validation": {"valid": False},
                "tests": {"passed": False},
                "constraints": {"passed": False, "violations": ["execution_failure"]},
                "score": 0.0,
                "base_score": 0.0,
                "bias_score": 0.0,
                "generated": variant.get("generated", False),
                "error": traceback.format_exc(),
            })

    valid_results = [r for r in results if r["constraints"]["passed"]]

    if not valid_results:
        selected = pick_variant(results)
    else:
        selected = pick_variant(valid_results)

    return results, selected
