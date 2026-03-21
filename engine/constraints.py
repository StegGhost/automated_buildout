from typing import Dict, Any, List


def default_constraints():
    return {
        "must_be_valid": True,
        "no_exceptions": True,
    }


def evaluate_constraints(validation_result: Dict[str, Any], error: str | None):
    constraints = default_constraints()

    violations: List[str] = []

    if constraints["must_be_valid"]:
        if not validation_result.get("valid", True):
            violations.append("validation_failed")

    if constraints["no_exceptions"]:
        if error is not None:
            violations.append("exception_occurred")

    return {
        "passed": len(violations) == 0,
        "violations": violations,
    }
