def compute_health(results):
    total = len(results)
    passed = sum(1 for r in results if r.get("valid"))

    return {
        "health_score": passed / total if total else 0,
        "total_phases": total,
        "passed": passed,
    }
