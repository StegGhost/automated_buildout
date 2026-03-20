def install_phase(phase, target_dir):
    if hasattr(phase, "install"):
        phase.install(target_dir)
