import json
from pathlib import Path


def _load_receipts(path):
    receipts = []

    for file in Path(path).glob("*.json"):
        with file.open() as f:
            receipts.append(json.load(f))

    receipts.sort(key=lambda x: x.get("timestamp", 0))
    return receipts


def diff_builds(dir_a: str, dir_b: str):
    """
    Compare two build receipt chains
    """

    a = _load_receipts(dir_a)
    b = _load_receipts(dir_b)

    diffs = []

    max_len = max(len(a), len(b))

    for i in range(max_len):
        ra = a[i] if i < len(a) else None
        rb = b[i] if i < len(b) else None

        if ra != rb:
            diffs.append({
                "index": i,
                "a": ra,
                "b": rb,
            })

    return {
        "equal": len(diffs) == 0,
        "diff_count": len(diffs),
        "diffs": diffs,
    }
