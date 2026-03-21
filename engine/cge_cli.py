from engine.cge_rebuild import rebuild_state
from engine.cge_rollback import rollback_to_root
from engine.cge_forward import forward_to_latest
from engine.cge_apply import apply_state


def rebuild(target_dir, root):
    return rebuild_state(target_dir, root)


def rollback(target_dir, root):
    return rollback_to_root(target_dir, root)


def forward(target_dir, root):
    return forward_to_latest(target_dir, root)


def apply(target_dir, root):
    state = rebuild_state(target_dir, root)
    if state.get("status") != "ok":
        return state

    return apply_state(target_dir, state["objects"])
