import hashlib
from typing import Dict, List, Any


def _fingerprint(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def score_variant(variant: Dict[str, Any]) -> float:
    score = 0.0

    if variant.get("valid", False):
        score += 1.0

    score += float(variant.get("agreement_ratio", 0.0))
    score -= float(variant.get("penalty", 0.0))

    return score


def select_best_variant(variants: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not variants:
        return {
            "selected": None,
            "variants": [],
            "reason": "no_variants",
        }

    enriched = []

    for variant in variants:
        item = dict(variant)
        item["fingerprint"] = _fingerprint(item.get("code", ""))
        item["score"] = score_variant(item)
        enriched.append(item)

    enriched.sort(key=lambda x: (x["score"], x["fingerprint"]), reverse=True)
    selected = enriched[0]

    return {
        "selected": selected,
        "variants": enriched,
        "reason": "highest_score",
    }
