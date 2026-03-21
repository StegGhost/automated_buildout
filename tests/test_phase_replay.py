from engine.runner import run_build


def test_phase_level_replay():
    first = run_build("demo_target", "manifests/example_manifest.json")
    second = run_build("demo_target", "manifests/example_manifest.json")

    assert first["status"] in ["success", "replayed"]
    assert second["status"] == "replayed" or all(
        r.get("replayed", False) for r in second.get("results", [])
    )
