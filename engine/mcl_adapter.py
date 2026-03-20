import json
from typing import List, Dict, Any

from cge.mcl_engine import compare_candidates


def run_mcl_phase(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    candidates = [
        {"source": "gpt", "code": "..."},
        {"source": "claude", "code": "..."}
    ]
    """

    result = compare_candidates(candidates)

    return {
        "selected_code": result["selected"],
        "consensus_receipt": result["receipt"]
    }
