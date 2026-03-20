import subprocess


def ensure_cge():
    try:
        import cge  # noqa
        return "present"
    except Exception:
        try:
            subprocess.run(["pip", "install", "stegcge"], check=False)
            return "installed"
        except Exception:
            return "failed"
