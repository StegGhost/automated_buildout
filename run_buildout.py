import json
from engine.runner import run_build

TARGET = "demo_target"

def main():
    result = run_build(TARGET)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
