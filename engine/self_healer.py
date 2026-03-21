from pathlib import Path

from engine.contract_registry import validate_contracts
from engine.auto_patcher import select_patch_for_failure


def _write_patch(target_file: str, code: str):
    path = Path(target_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")


def attempt_contract_repair():
    result = validate_contracts()

    if result["valid"]:
        return {
            "repaired": False,
            "status": "ok",
            "actions": [],
        }

    actions = []

    for failure in result["failures"]:
        selection = select_patch_for_failure(failure)
        selected = selection.get("selected")

        if not selected:
            actions.append({
                "status": "skipped",
                "failure": failure,
                "reason": selection.get("reason", "no_selection"),
            })
            continue

        target_file = selected.get("target_file")
        code = selected.get("code", "")

        if not target_file or not code:
            actions.append({
                "status": "skipped",
                "failure": failure,
                "reason": "incomplete_patch",
            })
            continue

        _write_patch(target_file, code)

        actions.append({
            "status": "patched",
            "failure": failure,
            "target_file": target_file,
            "fingerprint": selected.get("fingerprint"),
            "score": selected.get("score"),
            "source": selected.get("source"),
        })

    post_check = validate_contracts()

    return {
        "repaired": post_check["valid"],
        "status": "ok" if post_check["valid"] else "failed",
        "actions": actions,
        "post_check": post_check,
    }
