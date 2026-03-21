from engine.runner import run_build
from engine.cge_registry import load_latest_root
from engine.cge_rebuild import rebuild_state


def test_cge_rebuild():
    result = run_build("demo_target", "manifests/example_manifest.json")

    root = result["cge"]["global_root"]

    rebuilt = rebuild_state("demo_target", root)

    assert rebuilt["status"] == "ok"
    assert rebuilt["count"] > 0
