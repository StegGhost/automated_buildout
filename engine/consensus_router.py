import os


def select_mode() -> str:
    mode = os.getenv("CONSENSUS_MODE")
    if mode:
        return mode

    try:
        import cge  # noqa: F401
        return "cge"
    except Exception:
        return "fallback"
