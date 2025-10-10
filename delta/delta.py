import subprocess
import sys
import os
from pathlib import Path
import platform
import venv
from .models import ensure_llama_binary, init_config

def setup_delta():
    """Set up Delta environment: virtual environment, binary, and PATH."""
    print("Setting up Delta CLI environment...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("Python 3.8+ required.")
        sys.exit(1)
    print(f"Python found: Python {sys.version.split()[0]}")

    # Create virtual environment if needed
    venv_dir = Path.home() / "bin" / "delta_env"
    venv_bin = venv_dir / ("Scripts" if platform.system() == "Windows" else "bin")
    pip_path = venv_bin / ("pip.exe" if platform.system() == "Windows" else "pip")
    
    if not venv_dir.exists():
        print(f"Creating virtual environment at {venv_dir}")
        venv.create(venv_dir, with_pip=True)
    else:
        print(f"Virtual environment at {venv_dir} already exists")

    # Ensure pip is upgraded
    try:
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True, capture_output=True)
        print("pip upgraded in virtual environment")
    except subprocess.CalledProcessError as e:
        print(f"Failed to upgrade pip: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"pip not found at {pip_path}. Creating new virtual environment...")
        venv_dir.rmtree(ignore_errors=True)
        venv.create(venv_dir, with_pip=True)
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True, capture_output=True)

    # Install delta in virtual environment
    try:
        subprocess.run([str(pip_path), "install", "delta"], check=True, capture_output=True)
        print("Delta installed in virtual environment")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install delta: {e}")
        sys.exit(1)

    # Ensure llama.cpp binary
    try:
        binary_path = ensure_llama_binary()
        print(f"llama.cpp binary ready at {binary_path}")
    except Exception as e:
        print(f"Binary setup failed: {e}")
        return

    # Initialize config
    init_config()
    print("Configuration initialized.")

    # Guide PATH setup
    bin_dir = binary_path.parent
    shell = os.environ.get("SHELL", "").lower()
    if "bash" in shell or "zsh" in shell:
        profile = Path.home() / (".zshrc" if "zsh" in shell else ".bashrc")
        export_cmd = f'export PATH="$PATH:{bin_dir}:{venv_bin}"'
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
        print(f"Path: {bin_dir};{venv_bin}")
        print("Run 'setx PATH \"%PATH%;{};{}'\". Restart terminal.".format(bin_dir, venv_bin))
    else:
        print(f"Add {bin_dir} and {venv_bin} to your PATH manually for global 'delta' command access.")

    print("Setup complete! Run 'delta --help' to get started.")

def main():
    """Main entry point for Delta CLI."""
    from .cli import cli
    cli()

if __name__ == "__main__":
    main()