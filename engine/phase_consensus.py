from typing import Any, Dict, List, Optional

from engine.mcl_adapter import run_mcl_phase


def execute_consensus_phase(phase: Any, candidates: Optional[List[Dict]] = None) -> Dict:
    if candidates is None:
        candidates = phase.generate_candidates()

    result = run_mcl_phase(candidates)

    return {
        "selected_code": result["selected_code"],
        "consensus_receipt": result["consensus_receipt"],
    }
