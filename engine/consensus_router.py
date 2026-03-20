import os


def select_mode():
    """
    Determines which consensus mode to use.
    Priority:
    1. ENV override
    2. CGE availability
    3. fallback
    """
    mode = os.getenv("CONSENSUS_MODE")

    if mode:
        return mode

    try:
        import cge  # noqa
        return "cge"
    except Exception:
        return "fallback"
