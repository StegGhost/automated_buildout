def run(target_dir: str):
    import json
    import os

    receipt_path = os.path.join(target_dir, "receipt.json")

    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump({"phase": "receipts", "status": "ok"}, f)

    return {
        "status": "ok",
        "files_created": ["receipt.json"],
    }


def validate(target_dir: str):
    import os

    path = os.path.join(target_dir, "receipt.json")
    return {"valid": os.path.exists(path)}
