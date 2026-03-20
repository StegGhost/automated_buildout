import os

def install(target_dir):
    chain_file = os.path.join(target_dir, "chain.log")

    if not os.path.exists(chain_file):
        with open(chain_file, "w") as f:
            f.write("GENESIS\n")

def validate(target_dir):
    return {"valid": True}
