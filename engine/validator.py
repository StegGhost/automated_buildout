def validate_phase(phase, target_dir):
    """
    Supports:
    - optional phase.validate(target_dir)
    - otherwise defaults to valid
    """
    if hasattr(phase, "validate"):
        result = phase.validate(target_dir)
        if isinstance(result, dict):
            return result
        return {"valid": bool(result)}

    return {"valid": True}
