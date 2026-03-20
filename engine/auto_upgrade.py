def ensure_cge():
    """
    Non-blocking.
    Never raises.
    Never required for build success.
    """
    try:
        import cge  # noqa
        return "present"
    except Exception:
        return "absent"
