import hashlib
from typing import Any, Dict, List

from engine.consensus_router import select_mode


def _simple_consensus(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts = {}

    for candidate in candidates:
        code = candidate["code"]
        counts.setdefault(code, []).append(candidate["source"])

    best_code = max(counts.items(), key=lambda item: len(item[1]))[0]
    selected_sources = counts[best_code]

    fingerprint = hashlib.sha256(best_code.encode("utf-8")).hexdigest()

    return {
        "selected_code": best_code,
        "consensus_receipt": {
            "mode": "fallback",
            "consensus_size": len(selected_sources),
            "agreement_ratio": len(selected_sources) / len(candidates),
            "selected_sources": selected_sources,
            "consensus_fingerprint": fingerprint,
        },
    }


def run_mcl_phase(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    mode = select_mode()

    if mode == "cge":
        try:
            from cge.mcl_engine import compare_candidates

            result = compare_candidates(candidates)

            selected_code = result.get("selected_code") or result.get("selected")
            if selected_code is None:
                raise ValueError("CGE compare_candidates returned no selected code")

            return {
                "selected_code": selected_code,
                "consensus_receipt": {
                    **result,
                    "mode": "cge",
                },
            }
        except Exception:
            pass

    return _simple_consensus(candidates)
