def validate_phase(phase, target_dir):
    if hasattr(phase, "validate"):
        result = phase.validate(target_dir)
        if isinstance(result, dict):
            return result
        return {"valid": bool(result)}

    return {"valid": True}
