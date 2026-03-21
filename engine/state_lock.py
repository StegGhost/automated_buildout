from pathlib import Path
import time


LOCK_FILE = ".build.lock"


def acquire_lock(target_dir: str):
    lock_path = Path(target_dir) / LOCK_FILE

    if lock_path.exists():
        return {
            "acquired": False,
            "reason": "lock_exists",
        }

    lock_path.write_text(str(time.time()))
    return {
        "acquired": True,
        "path": str(lock_path),
    }


def release_lock(target_dir: str):
    lock_path = Path(target_dir) / LOCK_FILE

    if lock_path.exists():
        lock_path.unlink()

    return {"released": True}
