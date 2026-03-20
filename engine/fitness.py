def score_phase(validation_result: dict, consensus_receipt: dict = None) -> float:
    score = 0.0

    if validation_result.get("valid"):
        score += 0.5

    if consensus_receipt:
        score += consensus_receipt.get("agreement_ratio", 0.0) * 0.5

    return score
