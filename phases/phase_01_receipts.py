import os
import json
import time

def install(target_dir):
    receipt_file = os.path.join(target_dir, "receipt.json")

    if not os.path.exists(receipt_file):
        with open(receipt_file, "w") as f:
            json.dump({
                "created": time.time(),
                "events": []
            }, f)

def validate(target_dir):
    return {"valid": True}
