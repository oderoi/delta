#!/usr/bin/env python3
"""
Delta Phone Installation Script
Fixes installation issues on mobile devices and ensures all dependencies are properly installed.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(cmd, check=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return e

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print("✅ Python version OK")
        return True

def install_dependencies():
    """Install all required dependencies."""
    print("\n🔧 Installing dependencies...")
    
    # Core dependencies that are often missing on phones
    core_deps = [
        "click>=8.1.0",
        "requests>=2.31.0", 
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
        "huggingface_hub>=0.20.0",
        "tqdm>=4.66.0",
        "psutil>=5.9.0"
    ]
    
    # Optional dependencies
    optional_deps = [
        "duckduckgo-search>=3.0.0",
        "wikipedia>=1.4.0", 
        "PyPDF2>=3.0.0"
    ]
    
    # Install core dependencies first
    for dep in core_deps:
        print(f"Installing {dep}...")
        result = run_command(f"pip3 install '{dep}'", check=False)
        if result.returncode != 0:
            print(f"⚠️  Failed to install {dep}, trying without version constraint...")
            dep_name = dep.split('>=')[0]
            run_command(f"pip3 install {dep_name}", check=False)
    
    # Install optional dependencies
    for dep in optional_deps:
        print(f"Installing optional dependency {dep}...")
        run_command(f"pip3 install '{dep}'", check=False)

def install_delta():
    """Install Delta package."""
    print("\n📦 Installing Delta...")
    
    # First, try to uninstall any existing delta installation
    print("Removing any existing delta installation...")
    run_command("pip3 uninstall delta -y", check=False)
    
    # Install delta in development mode from current directory
    current_dir = Path(__file__).parent
    print(f"Installing from: {current_dir}")
    
    result = run_command(f"cd {current_dir} && pip3 install -e .", check=False)
    if result.returncode != 0:
        print("⚠️  Development install failed, trying regular install...")
        result = run_command(f"cd {current_dir} && pip3 install .", check=False)
        if result.returncode != 0:
            print("❌ Failed to install Delta")
            return False
    
    print("✅ Delta installed successfully")
    return True

def verify_installation():
    """Verify that Delta is properly installed."""
    print("\n🔍 Verifying installation...")
    
    # Test import of click
    try:
        import click
        print("✅ Click module imported successfully")
    except ImportError as e:
        print(f"❌ Click import failed: {e}")
        return False
    
    # Test delta CLI
    result = run_command("python3 -c 'from delta.cli import cli; print(\"Delta CLI imported successfully\")'", check=False)
    if result.returncode != 0:
        print("❌ Delta CLI import failed")
        return False
    
    print("✅ Delta CLI imported successfully")
    
    # Test delta command
    result = run_command("python3 -m delta.cli --help", check=False)
    if result.returncode != 0:
        print("❌ Delta CLI command failed")
        return False
    
    print("✅ Delta CLI command works")
    return True

def setup_delta():
    """Run delta setup."""
    print("\n⚙️  Setting up Delta...")
    result = run_command("python3 -m delta.cli setup", check=False)
    if result.returncode != 0:
        print("⚠️  Delta setup failed, but installation may still work")
        return False
    
    print("✅ Delta setup completed")
    return True

def main():
    """Main installation process."""
    print("🚀 Delta Phone Installation Script")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        print("❌ Installation failed: Python version incompatible")
        return False
    
    # Install dependencies
    install_dependencies()
    
    # Install Delta
    if not install_delta():
        print("❌ Installation failed: Could not install Delta")
        return False
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation failed: Verification failed")
        return False
    
    # Setup Delta
    setup_delta()
    
    print("\n🎉 Installation completed successfully!")
    print("\nYou can now use Delta with:")
    print("  python3 -m delta.cli --help")
    print("  python3 -m delta.cli setup")
    print("  python3 -m delta.cli run")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
