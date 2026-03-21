from engine.variant_generator import generate_variants


def dummy_fn(target_dir):
    with open(f"{target_dir}/x.txt", "w") as f:
        f.write("ok")


class Phase:
    @staticmethod
    def variants():
        return [{"name": "base", "callable": dummy_fn}]


def test_llm_generation_offline():
    phase = Phase()
    gens = generate_variants(phase, phase.variants(), max_new=1)
    assert isinstance(gens, list)
