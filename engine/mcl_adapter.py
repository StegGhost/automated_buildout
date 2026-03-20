import hashlib
from typing import List, Dict, Any


def _simple_consensus(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Fallback consensus:
    - groups identical code
    - selects most common
    """
    counts = {}

    for c in candidates:
        code = c["code"]
        counts.setdefault(code, []).append(c["source"])

    # pick most frequent
    best_code = max(counts.items(), key=lambda x: len(x[1]))[0]
    selected_sources = counts[best_code]

    fingerprint = hashlib.sha256(best_code.encode()).hexdigest()

    return {
        "selected_code": best_code,
        "consensus_receipt": {
            "consensus_size": len(selected_sources),
            "agreement_ratio": len(selected_sources) / len(candidates),
            "selected_sources": selected_sources,
            "consensus_fingerprint": fingerprint,
            "mode": "fallback",
        },
    }


def run_mcl_phase(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Attempts CGE MCL consensus.
    Falls back if unavailable.
    """
    try:
        from cge.mcl_engine import compare_candidates

        result = compare_candidates(candidates)

        return {
            "selected_code": result["selected_code"],
            "consensus_receipt": {
                **result,
                "mode": "cge",
            },
        }

    except Exception:
        # 🔥 critical: NEVER fail buildout due to missing CGE
        return _simple_consensus(candidates)
