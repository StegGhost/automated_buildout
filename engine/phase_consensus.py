from typing import Dict, Any
from engine.mcl_adapter import run_mcl_phase


def execute_consensus_phase(phase) -> Dict[str, Any]:
    """
    Phase must define:
    phase.generate_candidates() → list of candidates
    """

    candidates = phase.generate_candidates()

    mcl_result = run_mcl_phase(candidates)

    return {
        "selected_code": mcl_result["selected_code"],
        "consensus_receipt": mcl_result["consensus_receipt"]
    }
