def validate_phase(phase, target_dir):
    if hasattr(phase, "validate"):
        return phase.validate(target_dir)
    return {"valid": True}
