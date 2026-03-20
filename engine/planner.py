import importlib

PHASES = [
    "phases.phase_00_seed",
    "phases.phase_01_receipts",
    "phases.phase_02_chain",
]

def load_phases():
    loaded = []
    for p in PHASES:
        mod = importlib.import_module(p)
        loaded.append(mod)
    return loaded
