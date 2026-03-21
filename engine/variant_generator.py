import inspect
from typing import List, Dict, Any

from engine.llm_adapter import llm_mutate_code


def _extract_function_name(src: str) -> str:
    for line in src.splitlines():
        line = line.strip()
        if line.startswith("def ") and "(" in line:
            return line.split("def ", 1)[1].split("(", 1)[0]
    return "fn"


def _rename_function(src: str, new_name: str) -> str:
    lines = src.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().startswith("def "):
            prefix = ln[: ln.find("def ")]
            rest = ln.strip()[4:]  # after 'def '
            old = rest.split("(", 1)[0]
            lines[i] = f"{prefix}def {new_name}{rest[len(old):]}"
            break
    return "\n".join(lines)


def _compile_callable(src: str, fn_name: str):
    ns: Dict[str, Any] = {}
    try:
        exec(src, ns)
    except Exception:
        return None
    return ns.get(fn_name)


def generate_variant_from_callable(fn, suffix: str, context: Dict[str, Any]):
    try:
        src = inspect.getsource(fn)
    except Exception:
        return None

    base_name = _extract_function_name(src)
    new_name = f"{base_name}_{suffix}"

    mutated = llm_mutate_code(src, context=context)
    mutated = _rename_function(mutated, new_name)

    compiled = _compile_callable(mutated, new_name)
    return compiled


def generate_variants(phase, base_variants: List[Dict[str, Any]], max_new: int = 2):
    """
    For each base variant, generate up to `max_new` LLM-guided variants.
    """
    new_variants: List[Dict[str, Any]] = []

    for v in base_variants:
        name = v.get("name")
        fn = v.get("callable")

        for i in range(max_new):
            new_fn = generate_variant_from_callable(
                fn,
                suffix=f"gen{i}",
                context={"phase": getattr(phase, "__name__", str(phase)), "base_variant": name},
            )
            if new_fn:
                new_variants.append({
                    "name": f"{name}_gen{i}",
                    "callable": new_fn,
                    "generated": True,
                })

    return new_variants
