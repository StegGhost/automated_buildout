import os
import sys

sys.path.append(os.path.abspath("."))

from engine.runner import run_build
from engine.receipt_writer import load_existing_receipts


def test_buildout_runs():
    result = run_build("demo_target", "manifests/example_manifest.json")

    assert result["status"] == "success"
    assert len(result["results"]) >= 1

    for r in result["results"]:
        assert r["valid"] is True
        assert "receipt_hash" in r


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

    from engine.installer import install_phase

    result = install_phase(MockPhase(), "demo_target")

    assert result["installed"] is True
    assert result["mode"] == "consensus"
    assert "consensus_receipt" in result
