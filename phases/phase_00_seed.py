import os

def install(target_dir):
    os.makedirs(target_dir, exist_ok=True)

    path = os.path.join(target_dir, "app.py")

    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("print('hello world')\n")

def validate(target_dir):
    return {"valid": True}
