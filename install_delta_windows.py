#!/usr/bin/env python3
"""
Delta Windows Installation Script
Automated installation script for Windows users.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_header():
    """Print installation header."""
    print("=" * 60)
    print("🚀 Delta CLI - Windows Installation Script")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please download Python from: https://www.python.org/downloads/")
        print("   Make sure to check 'Add Python to PATH' during installation.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_pip():
    """Check if pip is available."""
    print("🔍 Checking pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available!")
        print("   Please install pip or reinstall Python with pip included.")
        return False

def check_git():
    """Check if Git is available."""
    print("🔍 Checking Git...")
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("✅ Git is available")
        return True
    except FileNotFoundError:
        print("⚠️  Git is not found!")
        print("   Git is recommended for building llama.cpp from source.")
        print("   Download from: https://git-scm.com/download/win")
        print("   Continuing without Git...")
        return False

def check_build_tools():
    """Check if build tools are available."""
    print("🔍 Checking build tools...")
    
    # Check for Visual Studio Build Tools
    vs_paths = [
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools",
        r"C:\Program Files\Microsoft Visual Studio\2022\Community",
        r"C:\Program Files\Microsoft Visual Studio\2022\Professional",
        r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise"
    ]
    
    for path in vs_paths:
        if os.path.exists(path):
            print("✅ Visual Studio Build Tools found")
            return True
    
    # Check for cl.exe in PATH
    try:
        subprocess.run(["cl"], capture_output=True, check=True)
        print("✅ C++ compiler found in PATH")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    print("⚠️  Build tools not found!")
    print("   This may cause issues when building llama.cpp from source.")
    print("   Install Visual Studio Build Tools from:")
    print("   https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022")
    print("   Continuing anyway...")
    return False

def install_delta():
    """Install Delta CLI."""
    print("📦 Installing Delta CLI...")
    
    try:
        # Check for conflicting packages
        print("🔍 Checking for conflicting packages...")
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                              capture_output=True, text=True)
        
        conflicting_packages = ["delta-0.4.2", "delta"]
        for package in conflicting_packages:
            if package in result.stdout:
                print(f"⚠️  Found conflicting package: {package}")
                print(f"   Uninstalling {package}...")
                subprocess.run([sys.executable, "-m", "pip", "uninstall", package, "-y"], 
                             capture_output=True)
        
        # Install Delta
        print("📥 Installing Delta...")
        subprocess.run([sys.executable, "-m", "pip", "install", "delta"], 
                      check=True)
        print("✅ Delta installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Delta: {e}")
        return False

def test_delta_command():
    """Test if delta command works."""
    print("🧪 Testing Delta command...")
    
    try:
        # Test command method
        result = subprocess.run(["delta", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Delta command works!")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Test Python module method
    try:
        result = subprocess.run([sys.executable, "-m", "delta.cli", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Delta Python module works!")
            print("   Use: python -m delta.cli [command]")
            return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass
    
    print("❌ Delta command not working!")
    return False

def setup_delta():
    """Setup Delta environment."""
    print("🔧 Setting up Delta environment...")
    
    try:
        # Try command method first
        subprocess.run(["delta", "setup"], check=True, timeout=300)
        print("✅ Delta setup completed!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        # Try Python module method
        try:
            subprocess.run([sys.executable, "-m", "delta.cli", "setup"], 
                          check=True, timeout=300)
            print("✅ Delta setup completed!")
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print("❌ Delta setup failed!")
            return False

def test_basic_functionality():
    """Test basic Delta functionality."""
    print("🧪 Testing basic functionality...")
    
    try:
        # Test list command
        result = subprocess.run([sys.executable, "-m", "delta.cli", "list"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Delta list command works!")
            return True
        else:
            print(f"⚠️  Delta list command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Delta list command timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Delta: {e}")
        return False

def print_usage_guide():
    """Print usage guide."""
    print("\n" + "=" * 60)
    print("🎉 Installation Complete!")
    print("=" * 60)
    print()
    print("📋 Usage Guide:")
    print()
    print("1. Download a model:")
    print("   python -m delta.cli pull qwen2:0.5b")
    print()
    print("2. Start chatting:")
    print("   python -m delta.cli run qwen2:0.5b")
    print()
    print("3. List available models:")
    print("   python -m delta.cli list")
    print()
    print("4. Get help:")
    print("   python -m delta.cli --help")
    print()
    print("📚 For more information, see:")
    print("   - README.md")
    print("   - WINDOWS_INSTALLATION_GUIDE.md")
    print()
    print("🆘 If you have issues:")
    print("   - Check WINDOWS_INSTALLATION_GUIDE.md for troubleshooting")
    print("   - Run: python -m delta.cli doctor")
    print("   - Report issues on GitHub")

def main():
    """Main installation function."""
    print_header()
    
    # Check system requirements
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    check_git()
    check_build_tools()
    
    # Install Delta
    if not install_delta():
        return False
    
    # Test installation
    if not test_delta_command():
        print("⚠️  Delta command not found, but Python module should work")
    
    # Setup Delta
    if not setup_delta():
        print("⚠️  Delta setup failed, but you can try manually:")
        print("   python -m delta.cli setup")
    
    # Test functionality
    test_basic_functionality()
    
    # Print usage guide
    print_usage_guide()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Installation completed successfully!")
        else:
            print("\n❌ Installation failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
