def execute_with_fallback(phase, target_dir):
    try:
        if hasattr(phase, "run"):
            result = phase.run(target_dir)
            if isinstance(result, dict):
                return result
            return {"status": "ok", "mode": "fallback"}

        if callable(phase):
            result = phase(target_dir)
            if isinstance(result, dict):
                return result
            return {"status": "ok", "mode": "fallback"}

        return {"status": "unknown_phase_type", "mode": "fallback"}

    except Exception as e:
        return {
            "status": "failed",
            "mode": "fallback",
            "error": str(e),
        }
