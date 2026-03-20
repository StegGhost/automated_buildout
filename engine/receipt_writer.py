def load_existing_receipts(target_dir: str):
    receipts_dir = Path(target_dir) / ".buildout_receipts"

    if not receipts_dir.exists():
        return []

    receipts = []

    for file in receipts_dir.glob("*.json"):
        with file.open() as f:
            data = json.load(f)
            receipts.append(data)

    # sort by timestamp
    receipts.sort(key=lambda x: x.get("timestamp", 0))

    # 🔥 CRITICAL FIX — keep ONLY latest run
    filtered = []
    last_ts = None

    for r in receipts:
        ts = int(r.get("timestamp", 0))

        # group by second-level timestamp (same build run)
        if last_ts is None or ts == last_ts:
            filtered.append(r)
            last_ts = ts
        elif ts > last_ts:
            # new run detected → reset
            filtered = [r]
            last_ts = ts

    return filtered
