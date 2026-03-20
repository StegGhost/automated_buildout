from engine.auto_upgrade import ensure_cge
from engine.build_health import compute_health
from engine.graph_exporter import export_graph
from engine.installer import install_phase
from engine.planner import load_phases
from engine.receipt_writer import write_phase_receipt
from engine.replay import replay_build
from engine.validator import validate_phase


def run_build(target_dir=None, manifest_path: str = "manifests/example_manifest.json"):
    ensure_cge()

    phases, manifest = load_phases(manifest_path)

    if target_dir is None:
        target_dir = manifest["target_dir"]

    results = []
    receipts = []
    parent_hash = None

    for phase in phases:
        name = getattr(phase, "__name__", str(phase))

        install_result = install_phase(phase, target_dir)
        validation = validate_phase(phase, target_dir)

        receipt = write_phase_receipt(
            target_dir=target_dir,
            phase_name=name,
            install_result=install_result,
            validation_result=validation,
            parent_hash=parent_hash,
        )

        parent_hash = receipt["receipt_hash"]
        receipts.append(receipt)

        results.append(
            {
                "phase": name,
                "valid": validation.get("valid", True),
                "receipt_hash": parent_hash,
                "install_result": install_result,
            }
        )

        if not validation.get("valid", True):
            return {
                "status": "failed",
                "results": results,
                "receipts": receipts,
                "health": compute_health(results),
            }

    graph_path = export_graph(receipts, target_dir)
    replay_result = replay_build(target_dir)
    health = compute_health(results)

    return {
        "status": "success",
        "results": results,
        "receipts": receipts,
        "graph_path": graph_path,
        "replay_result": replay_result,
        "health": health,
    }
