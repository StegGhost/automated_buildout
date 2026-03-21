import random


def mutate_code(original_code: str):
    """
    Very simple mutation engine (v4.0 baseline).
    Later this becomes LLM-driven.
    """

    mutations = [
        lambda c: c.replace("print(", "print('mutated:', "),
        lambda c: c + "\n# mutation",
        lambda c: c.replace("'", '"'),
    ]

    mutation = random.choice(mutations)
    return mutation(original_code)


def generate_variant_from_callable(fn):
    """
    Extract source → mutate → create new callable
    """
    import inspect

    try:
        source = inspect.getsource(fn)
    except Exception:
        return None

    mutated = mutate_code(source)

    namespace = {}

    try:
        exec(mutated, namespace)
    except Exception:
        return None

    # find function in namespace
    for v in namespace.values():
        if callable(v):
            return v

    return None


def generate_variants(phase, max_new=2):
    if not hasattr(phase, "variants"):
        return []

    base_variants = phase.variants()

    new_variants = []

    for variant in base_variants:
        fn = variant.get("callable")

        for _ in range(max_new):
            new_fn = generate_variant_from_callable(fn)

            if new_fn:
                new_variants.append({
                    "name": f"{variant['name']}_gen",
                    "callable": new_fn,
                })

    return new_variants
