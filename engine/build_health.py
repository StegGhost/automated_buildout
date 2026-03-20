def compute_health(results):
    total = len(results)
    passed = sum(1 for result in results if result.get("valid"))

    return {
        "health_score": passed / total if total else 0.0,
        "total_phases": total,
        "passed": passed,
    }
