def load_existing_receipts(target_dir: str):
    receipts_dir = Path(target_dir) / ".buildout_receipts"

    if not receipts_dir.exists():
        return []

    receipts = []

    for file in receipts_dir.glob("*.json"):
        with file.open(encoding="utf-8") as f:
            data = json.load(f)
            receipts.append(data)

    if not receipts:
        return []

    # 🔥 FIX: group by full timestamp precision (not int)
    receipts.sort(key=lambda x: x.get("timestamp", 0))

    latest_run = []
    run_start = None

    for r in receipts:
        ts = r.get("timestamp")

        if run_start is None:
            run_start = ts
            latest_run.append(r)
            continue

        # allow small delta within same run (~1 second window)
        if abs(ts - run_start) < 1.0:
            latest_run.append(r)
        else:
            # new run detected → reset
            latest_run = [r]
            run_start = ts

    return latest_run
