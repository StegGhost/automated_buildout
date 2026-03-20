def run(target_dir: str):
    import os

    os.makedirs(target_dir, exist_ok=True)

    with open(os.path.join(target_dir, "app.py"), "w", encoding="utf-8") as f:
        f.write("print('hello from seed phase')\n")

    return {
        "status": "ok",
        "files_created": ["app.py"],
    }


def validate(target_dir: str):
    import os

    path = os.path.join(target_dir, "app.py")
    return {"valid": os.path.exists(path)}
