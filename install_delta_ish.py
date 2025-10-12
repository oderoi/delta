#!/usr/bin/env python3
"""
Delta iSH-Shell Installation Script
Specifically designed for iPhone iSH-shell environment
Handles missing development packages and compatibility issues
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(cmd, check=True, capture_output=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True)
        if result.stdout and capture_output:
            print(result.stdout)
        if result.stderr and capture_output:
            print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return e

def install_ish_dependencies():
    """Install essential development packages for iSH-shell."""
    print("🔧 Installing iSH-shell development dependencies...")
    
    # Essential packages for iSH-shell
    essential_packages = [
        "gcc",
        "python3-dev", 
        "musl-dev",
        "linux-headers",
        "build-base",
        "libffi-dev",
        "openssl-dev"
    ]
    
    for package in essential_packages:
        print(f"Installing {package}...")
        result = run_command(f"apk add {package}", check=False)
        if result.returncode != 0:
            print(f"⚠️  Failed to install {package}, continuing...")

def upgrade_python_packages():
    """Upgrade Python packaging tools to fix compatibility issues."""
    print("⬆️  Upgrading Python packaging tools...")
    
    # Upgrade pip, setuptools, and wheel
    packages_to_upgrade = [
        "pip",
        "setuptools", 
        "wheel",
        "packaging"
    ]
    
    for package in packages_to_upgrade:
        print(f"Upgrading {package}...")
        run_command(f"pip3 install --upgrade {package}", check=False)

def install_core_dependencies():
    """Install core dependencies with iSH-shell compatibility."""
    print("🔧 Installing core dependencies...")
    
    # Core dependencies that work well in iSH-shell
    core_deps = [
        "click>=8.1.0",
        "requests>=2.31.0",
        "tabulate>=0.9.0", 
        "colorama>=0.4.6",
        "huggingface_hub>=0.20.0",
        "tqdm>=4.66.0"
    ]
    
    for dep in core_deps:
        print(f"Installing {dep}...")
        result = run_command(f"pip3 install '{dep}'", check=False)
        if result.returncode != 0:
            # Try without version constraint
            dep_name = dep.split('>=')[0]
            print(f"Trying {dep_name} without version constraint...")
            run_command(f"pip3 install {dep_name}", check=False)

def install_psutil_alternative():
    """Install psutil alternative or skip if compilation fails."""
    print("🔧 Handling psutil installation...")
    
    # Try to install psutil
    result = run_command("pip3 install psutil", check=False)
    if result.returncode != 0:
        print("⚠️  psutil compilation failed, trying alternative...")
        
        # Try installing from wheel if available
        run_command("pip3 install --only-binary=psutil psutil", check=False)
        
        # If still fails, we'll modify the code to make psutil optional
        print("⚠️  psutil will be optional - some features may not work")

def install_optional_dependencies():
    """Install optional dependencies, skipping problematic ones."""
    print("🔧 Installing optional dependencies...")
    
    # Try to install optional dependencies, but don't fail if they don't work
    optional_deps = [
        "duckduckgo-search",
        "PyPDF2"
    ]
    
    for dep in optional_deps:
        print(f"Installing {dep}...")
        result = run_command(f"pip3 install {dep}", check=False)
        if result.returncode != 0:
            print(f"⚠️  Skipping {dep} - not critical for basic functionality")

def create_ish_compatible_delta():
    """Create an iSH-shell compatible version of Delta."""
    print("🔧 Creating iSH-shell compatible Delta...")
    
    # Read the original cli.py
    cli_path = Path("delta/cli.py")
    if cli_path.exists():
        content = cli_path.read_text()
        
        # Add iSH-shell compatibility imports
        ish_compatibility = '''
# iSH-shell compatibility
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available - some features disabled")
'''
        
        # Insert compatibility code after imports
        if "import psutil" in content:
            content = content.replace("import psutil", ish_compatibility)
        else:
            # Add after other imports
            import_end = content.find("from . import __version__")
            if import_end != -1:
                content = content[:import_end] + ish_compatibility + "\n" + content[import_end:]
        
        # Write the modified file
        cli_path.write_text(content)
        print("✅ Created iSH-shell compatible Delta")

def install_delta_ish():
    """Install Delta with iSH-shell compatibility."""
    print("📦 Installing Delta for iSH-shell...")
    
    # Remove any existing delta installation
    run_command("pip3 uninstall delta -y", check=False)
    
    # Install Delta in development mode
    result = run_command("pip3 install -e .", check=False)
    if result.returncode != 0:
        print("⚠️  Development install failed, trying regular install...")
        result = run_command("pip3 install .", check=False)
        if result.returncode != 0:
            print("❌ Failed to install Delta")
            return False
    
    print("✅ Delta installed successfully")
    return True

def test_installation():
    """Test the installation."""
    print("🧪 Testing installation...")
    
    # Test click import
    result = run_command("python3 -c 'import click; print(\"Click OK\")'", check=False)
    if result.returncode != 0:
        print("❌ Click import failed")
        return False
    
    # Test delta CLI import
    result = run_command("python3 -c 'from delta.cli import cli; print(\"Delta CLI OK\")'", check=False)
    if result.returncode != 0:
        print("❌ Delta CLI import failed")
        return False
    
    # Test delta command
    result = run_command("python3 -m delta.cli --help", check=False)
    if result.returncode != 0:
        print("❌ Delta CLI command failed")
        return False
    
    print("✅ Installation test passed")
    return True

def main():
    """Main installation process for iSH-shell."""
    print("🚀 Delta iSH-Shell Installation Script")
    print("=" * 50)
    
    # Step 1: Install iSH-shell dependencies
    print("\n🔧 Step 1: Installing iSH-shell dependencies...")
    install_ish_dependencies()
    
    # Step 2: Upgrade Python packages
    print("\n⬆️  Step 2: Upgrading Python packages...")
    upgrade_python_packages()
    
    # Step 3: Install core dependencies
    print("\n🔧 Step 3: Installing core dependencies...")
    install_core_dependencies()
    
    # Step 4: Handle psutil
    print("\n🔧 Step 4: Handling psutil...")
    install_psutil_alternative()
    
    # Step 5: Install optional dependencies
    print("\n🔧 Step 5: Installing optional dependencies...")
    install_optional_dependencies()
    
    # Step 6: Create iSH-shell compatible Delta
    print("\n🔧 Step 6: Creating iSH-shell compatible Delta...")
    create_ish_compatible_delta()
    
    # Step 7: Install Delta
    print("\n📦 Step 7: Installing Delta...")
    if not install_delta_ish():
        print("❌ Delta installation failed")
        return False
    
    # Step 8: Test installation
    print("\n🧪 Step 8: Testing installation...")
    if not test_installation():
        print("❌ Installation test failed")
        return False
    
    print("\n🎉 iSH-shell installation completed successfully!")
    print("\nYou can now use Delta with:")
    print("  python3 -m delta.cli --help")
    print("  python3 -m delta.cli setup")
    print("  python3 -m delta.cli run")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
