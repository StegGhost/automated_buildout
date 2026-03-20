def replay_build(receipts: list):
    """
    Minimal replay validator:
    Confirms receipt chain integrity.
    """

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

    return {"status": "ok"}
