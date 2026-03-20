import os
import sys

sys.path.append(os.path.abspath("."))

from engine.installer import install_phase
from engine.receipt_writer import load_existing_receipts
from engine.runner import run_build


def test_buildout_runs():
    result = run_build("demo_target", "manifests/example_manifest.json")

    assert result["status"] == "success"
    assert result["health"]["health_score"] == 1.0
    assert "replay_result" in result
    assert result["replay_result"]["status"] == "ok"


def test_phase_receipts_written():
    run_build("demo_target", "manifests/example_manifest.json")
    receipts = load_existing_receipts("demo_target")

    assert len(receipts) >= 3
    assert receipts[0]["parent_hash"] is None

    for i in range(1, len(receipts)):
        assert receipts[i]["parent_hash"] == receipts[i - 1]["receipt_hash"]


def test_consensus_phase():
    class MockPhase:
        output_file = "test.py"

        def generate_candidates(self):
            return [
                {"source": "gpt", "code": "print('hello world')"},
                {"source": "claude", "code": "print('hello world')"},
                {"source": "other", "code": "print('hi')"},
            ]

    result = install_phase(MockPhase(), "demo_target")

    assert result["installed"] is True
    assert result["mode"] == "consensus"
    assert "consensus_receipt" in result
