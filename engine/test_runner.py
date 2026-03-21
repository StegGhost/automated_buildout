import traceback


def run_unit_tests(fn, target_dir):
    """
    Minimal test harness:
    - executes function
    - catches errors
    - returns pass/fail
    """

    try:
        fn(target_dir)
        return {
            "passed": True,
            "error": None,
        }

    except Exception:
        return {
            "passed": False,
            "error": traceback.format_exc(),
        }
