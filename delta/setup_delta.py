import platform
import os
from pathlib import Path
from .models import ensure_llama_binary, init_config

def setup_environment():
    """Set up Delta environment: binary, config, and PATH."""
    print("Setting up Delta CLI environment...")
    
    # Ensure config
    init_config()
    print("Configuration initialized.")

    # Ensure llama.cpp binary
    try:
        binary_path = ensure_llama_binary()
        print(f"llama.cpp binary ready at {binary_path}")
    except Exception as e:
        print(f"Binary setup failed: {e}")
        return

    # Guide PATH setup
    bin_dir = binary_path.parent
    shell = os.environ.get("SHELL", "").lower()
    if "bash" in shell or "zsh" in shell:
        profile = Path.home() / (".zshrc" if "zsh" in shell else ".bashrc")
        export_cmd = f'export PATH="$PATH:{bin_dir}"'
        if profile.exists() and export_cmd not in profile.read_text():
            print(f"Add to {profile} for global access:")
            print(export_cmd)
            if input("Add to profile now? (y/n): ").lower() == 'y':
                with profile.open('a') as f:
                    f.write(f"\n# Delta CLI\n{export_cmd}\n")
                print(f"Added to {profile}. Run 'source {profile}' or restart terminal.")
        else:
            print(f"PATH already includes {bin_dir} or profile not found.")
    elif platform.system() == "Windows":
        print("For global access, add to PATH in System Settings:")
        print(f"Path: {bin_dir}")
        print("Run 'setx PATH \"%PATH%;{}\"'. Restart terminal.".format(bin_dir))
    else:
        print(f"Add {bin_dir} to your PATH manually for global 'delta' command access.")

    print("Setup complete! Run 'delta --help' to get started.")