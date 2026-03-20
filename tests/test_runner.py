import sys
import os

# 🔥 ensure repo root is on path
sys.path.append(os.path.abspath("."))

from engine.runner import run_build


def test_buildout_runs():
    result = run_build("demo_target")

    assert result["status"] == "success"
    assert len(result["results"]) >= 1

    for r in result["results"]:
        assert r["valid"] is True
