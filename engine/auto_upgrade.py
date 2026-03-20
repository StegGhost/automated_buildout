def ensure_cge():
    """
    Non-blocking probe.
    Buildout must not fail if CGE is unavailable.
    """
    try:
        import cge  # noqa: F401
        return "present"
    except Exception:
        return "absent"
