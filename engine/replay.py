from engine.receipt_loader import load_run_receipts


def replay_build(target_dir: str, run_id: str):
    receipts = load_run_receipts(target_dir, run_id)

    if not receipts:
        return {"status": "empty"}

    for i in range(1, len(receipts)):
        prev = receipts[i - 1]
        curr = receipts[i]

        if curr.get("parent_hash") != prev.get("receipt_hash"):
            return {
                "status": "invalid",
                "reason": "chain_break",
                "index": i,
            }

    return {"status": "ok", "total": len(receipts)}
