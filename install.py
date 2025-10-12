#!/usr/bin/env python3
"""
Delta Universal Installer
One-command installation for all platforms with automatic dependency resolution
"""

import sys
import os
import platform
import subprocess
import shutil
import json
from pathlib import Path

def print_banner():
    """Print installation banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    Delta CLI Installer                      ║
║              Universal Installation Script                 ║
║                                                              ║
║  🚀 Cross-platform LLM CLI with llama.cpp integration      ║
║  📱 Works on PC, Mac, Linux, Android, iOS                  ║
║  🔧 Automatic setup with pre-built binaries                 ║
╚══════════════════════════════════════════════════════════════╝
""")

def check_requirements():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check platform
    system = platform.system()
    print(f"✅ Platform: {system} {platform.machine()}")
    
    # Check available tools
    tools = ['pip']
    if system != 'Windows':
        tools.extend(['git', 'make'])
    
    missing_tools = []
    for tool in tools:
        if not shutil.which(tool):
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"❌ Missing required tools: {', '.join(missing_tools)}")
        print("Please install them and try again")
        return False
    
    print("✅ All required tools available")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Core dependencies
    core_deps = [
        'requests>=2.31.0',
        'click>=8.1.0',
        'tabulate>=0.9.0',
        'colorama>=0.4.6',
        'huggingface_hub>=0.20.0',
        'tqdm>=4.66.0',
        'psutil>=5.9.0'
    ]
    
    # Optional dependencies
    optional_deps = [
        'duckduckgo-search>=3.0.0',
        'wikipedia>=1.4.0',
        'PyPDF2>=3.0.0'
    ]
    
    # GPU dependencies (platform-specific)
    gpu_deps = []
    if platform.system() in ['Linux', 'Windows']:
        gpu_deps.append('nvidia-ml-py>=12.560.30')
    
    all_deps = core_deps + optional_deps + gpu_deps
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True, capture_output=True)
        
        subprocess.run([
            sys.executable, '-m', 'pip', 'install'
        ] + all_deps, check=True, capture_output=True)
        
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def install_delta():
    """Install Delta CLI"""
    print("🚀 Installing Delta CLI...")
    
    try:
        # Install in development mode
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-e', '.'
        ], check=True, capture_output=True)
        
        print("✅ Delta CLI installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Delta CLI: {e}")
        return False

def setup_llama_cpp():
    """Setup llama.cpp binary"""
    print("🔧 Setting up llama.cpp...")
    
    try:
        from delta.installer import DeltaInstaller
        installer = DeltaInstaller()
        
        if installer.install():
            print("✅ llama.cpp setup completed")
            return True
        else:
            print("❌ llama.cpp setup failed")
            return False
    except Exception as e:
        print(f"❌ Failed to setup llama.cpp: {e}")
        return False

def setup_environment():
    """Setup environment variables and PATH"""
    print("🔧 Setting up environment...")
    
    try:
        # Test delta command
        result = subprocess.run(['delta', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Delta CLI is working")
        else:
            print("❌ Delta CLI not working properly")
            return False
        
        # Run setup
        result = subprocess.run(['delta', 'setup'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Delta setup completed")
        else:
            print("⚠️  Delta setup had issues, but continuing...")
        
        return True
    except Exception as e:
        print(f"❌ Failed to setup environment: {e}")
        return False

def verify_installation():
    """Verify the installation works"""
    print("🔍 Verifying installation...")
    
    try:
        # Test basic commands
        commands = [
            ['delta', '--help'],
            ['delta', 'version'],
            ['delta', 'doctor']
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"❌ Command failed: {' '.join(cmd)}")
                print(f"Error: {result.stderr}")
                return False
        
        print("✅ All commands working correctly")
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def print_success_message():
    """Print success message with next steps"""
    print("""
🎉 Delta CLI Installation Complete!

Next steps:
1. Run 'delta doctor' to check your system
2. Run 'delta list' to see available models
3. Run 'delta pull qwen2:0.5b' to download a model
4. Run 'delta run qwen2:0.5b' to start chatting

For help, run 'delta --help'

Happy chatting! 🚀
""")

def main():
    """Main installation process"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Install Delta
    if not install_delta():
        print("❌ Delta installation failed")
        sys.exit(1)
    
    # Setup llama.cpp
    if not setup_llama_cpp():
        print("❌ llama.cpp setup failed")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        sys.exit(1)
    
    # Success!
    print_success_message()

if __name__ == "__main__":
    main()
