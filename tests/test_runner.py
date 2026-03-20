from engine.runner import run_build

def test_buildout_runs():
    result = run_build("demo_target")
    assert result["status"] == "success"
