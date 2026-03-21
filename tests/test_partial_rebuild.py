from engine.runner import run_build


def test_partial_rebuild_behavior():
    first = run_build("demo_target", "manifests/example_manifest.json")
    second = run_build("demo_target", "manifests/example_manifest.json")

    # second run should either fully replay or skip most phases
    assert second["status"] in ["replayed", "success"]

    if second["status"] == "success":
        assert any(r.get("replayed") for r in second["results"])
