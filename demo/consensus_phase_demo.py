from engine.installer import install_phase


class DemoPhase:
    output_file = "demo_output.py"

    def generate_candidates(self):
        return [
            {"source": "gpt", "code": "print('hello world')"},
            {"source": "claude", "code": "print('hello world')"},
            {"source": "alt", "code": "print('HELLO WORLD')"},
        ]


install_phase(DemoPhase(), "demo_target")
