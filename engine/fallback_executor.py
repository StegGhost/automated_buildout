def execute_with_fallback(phase, target_dir):
    """
    Executes a phase with a fallback mechanism.
    """

    try:
        if hasattr(phase, "run"):
            return phase.run(target_dir)

        if callable(phase):
            return phase(target_dir)

        return {"status": "unknown_phase_type"}

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
        }
