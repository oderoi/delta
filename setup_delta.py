#!/usr/bin/env python3
"""
Delta Setup Script - One-command installation for all platforms
Handles automatic installation with pre-built binaries and fallback compilation
"""

import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        print("Please upgrade Python and try again")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def check_dependencies():
    """Check and install required dependencies"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'requests',
        'click', 
        'tabulate',
        'huggingface_hub',
        'tqdm',
        'psutil',
        'colorama'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("Please install manually: pip install " + " ".join(missing_packages))
            sys.exit(1)

def install_delta():
    """Install Delta CLI"""
    print("🚀 Installing Delta CLI...")
    
    try:
        # Install in development mode
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'], check=True)
        print("✅ Delta CLI installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Delta CLI: {e}")
        sys.exit(1)

def setup_llama_cpp():
    """Setup llama.cpp binary"""
    print("🔧 Setting up llama.cpp...")
    
    try:
        # Import and run the installer
        from delta.installer import DeltaInstaller
        installer = DeltaInstaller()
        
        if installer.install():
            print("✅ llama.cpp setup completed")
        else:
            print("❌ llama.cpp setup failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Failed to setup llama.cpp: {e}")
        print("You may need to install build tools manually")
        sys.exit(1)

def verify_installation():
    """Verify the installation"""
    print("🔍 Verifying installation...")
    
    try:
        # Test delta command
        result = subprocess.run(['delta', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Delta CLI is working")
        else:
            print("❌ Delta CLI not working properly")
            return False
            
        # Test setup
        result = subprocess.run(['delta', 'doctor'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Delta doctor check passed")
        else:
            print("⚠️  Some issues detected - run 'delta doctor' for details")
            
        return True
        
    except FileNotFoundError:
        print("❌ Delta command not found in PATH")
        print("Please add the installation directory to your PATH")
        return False

def main():
    """Main installation process"""
    print("🎯 Delta CLI Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check and install dependencies
    check_dependencies()
    
    # Install Delta
    install_delta()
    
    # Setup llama.cpp
    setup_llama_cpp()
    
    # Verify installation
    if verify_installation():
        print("\n🎉 Delta CLI installation completed successfully!")
        print("\nNext steps:")
        print("1. Run 'delta doctor' to check your system")
        print("2. Run 'delta setup' if you need to reconfigure")
        print("3. Run 'delta list' to see available models")
        print("4. Run 'delta pull <model>' to download a model")
        print("5. Run 'delta run <model>' to start chatting")
        print("\nFor help, run 'delta --help'")
    else:
        print("\n❌ Installation verification failed")
        print("Please check the error messages above and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()
