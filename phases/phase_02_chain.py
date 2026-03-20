def run(target_dir: str):
    import os

    chain_path = os.path.join(target_dir, "chain.log")

    with open(chain_path, "w", encoding="utf-8") as f:
        f.write("chain initialized\n")

    return {
        "status": "ok",
        "files_created": ["chain.log"],
    }


def validate(target_dir: str):
    import os

    path = os.path.join(target_dir, "chain.log")
    return {"valid": os.path.exists(path)}
