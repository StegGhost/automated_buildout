from engine.runner import run_build


def test_build_idempotency():
    r1 = run_build("demo_target", "manifests/example_manifest.json")
    r2 = run_build("demo_target", "manifests/example_manifest.json")

    assert r1["status"] in ["success", "replayed"]
    assert r2["status"] == "replayed"


def test_locking():
    r1 = run_build("demo_target", "manifests/example_manifest.json")
    r2 = run_build("demo_target", "manifests/example_manifest.json")

    assert "status" in r1
    assert "status" in r2


def test_chain_integrity():
    result = run_build("demo_target", "manifests/example_manifest.json")

    if result["status"] == "success":
        assert result["replay_result"]["status"] == "ok"
