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
