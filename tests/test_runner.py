from engine.runner import run_build
from engine.replay import load_run_receipts


def test_buildout_runs():
    result = run_build("demo_target", "manifests/example_manifest.json")

    assert result["status"] == "success"
    assert result["health"]["health_score"] == 1.0
    assert "replay_result" in result
    assert result["replay_result"]["status"] == "ok"
    assert "run_id" in result


def test_phase_receipts_written():
    result = run_build("demo_target", "manifests/example_manifest.json")

    run_id = result["run_id"]

    receipts = load_run_receipts("demo_target", run_id)

    assert len(receipts) >= 3
    assert receipts[0]["parent_hash"] is None

    for i in range(1, len(receipts)):
        assert receipts[i]["parent_hash"] == receipts[i - 1]["receipt_hash"]
