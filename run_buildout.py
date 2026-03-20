import json

from engine.runner import run_build


def main():
    result = run_build()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
