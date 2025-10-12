#!/usr/bin/env python3
"""
Delta Installation Script
This script handles the complete installation of Delta CLI with all fixes
"""

import sys
import os
import subprocess
import platform
from pathlib import Path
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version OK: {sys.version}")
    return True

def uninstall_wrong_delta():
    """Uninstall the wrong delta package if installed"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'delta'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # Check if it's the wrong delta package
            if "Human friendly context aware duration parsing" in result.stdout:
                print("🔧 Found wrong delta package, uninstalling...")
                subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'delta', '-y'], 
                              check=True)
                print("✅ Wrong delta package uninstalled")
                return True
    except Exception:
        pass
    return False

def install_dependencies():
    """Install required dependencies first"""
    print("🔧 Installing dependencies...")
    
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
    
    for dep in core_deps:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # Try without version constraint
            dep_name = dep.split('>=')[0]
            print(f"Trying {dep_name} without version constraint...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep_name], 
                         check=False, capture_output=True)
    
    # Install optional dependencies
    optional_deps = [
        "duckduckgo-search>=3.0.0",
        "wikipedia>=1.4.0", 
        "PyPDF2>=3.0.0"
    ]
    
    for dep in optional_deps:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         check=False, capture_output=True)
        except:
            pass  # Optional dependencies can fail

def install_delta_local():
    """Install Delta from local source"""
    print("🔧 Installing Delta from local source...")
    
    # First install dependencies
    install_dependencies()
    
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Install in development mode
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'], 
                      check=True)
        print("✅ Delta installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Delta: {e}")
        # Try regular install as fallback
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '.'], 
                          check=True)
            print("✅ Delta installed successfully (fallback method)")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"❌ Fallback installation also failed: {e2}")
            return False

def test_delta_command():
    """Test if delta command works"""
    try:
        result = subprocess.run(['delta', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Delta command works!")
            return True
        else:
            print(f"❌ Delta command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Delta command not found")
        return False
    except Exception as e:
        print(f"❌ Delta command error: {e}")
        return False

def test_python_module():
    """Test if Python module works"""
    try:
        result = subprocess.run([sys.executable, '-m', 'delta.cli', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Python module works!")
            return True
        else:
            print(f"❌ Python module failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Python module error: {e}")
        return False

def setup_delta():
    """Setup Delta environment"""
    print("🔧 Setting up Delta environment...")
    try:
        # Try delta setup command
        result = subprocess.run(['delta', 'setup'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ Delta setup completed")
            return True
        else:
            print(f"⚠️  Delta setup had issues: {result.stderr}")
            # Try Python module method
            result = subprocess.run([sys.executable, '-m', 'delta.cli', 'setup'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ Delta setup completed via Python module")
                return True
            else:
                print(f"❌ Delta setup failed: {result.stderr}")
                return False
    except subprocess.TimeoutExpired:
        print("❌ Delta setup timed out")
        return False
    except Exception as e:
        print(f"❌ Delta setup error: {e}")
        return False

def create_usage_guide():
    """Create a usage guide for the user"""
    print("\n📚 Usage Guide")
    print("=" * 50)
    print("Delta is now installed! You can use it in two ways:")
    print()
    print("1. Direct command (if PATH is fixed):")
    print("   delta --help")
    print("   delta setup")
    print("   delta run qwen2:0.5b")
    print()
    print("2. Python module (always works):")
    print("   python -m delta.cli --help")
    print("   python -m delta.cli setup")
    print("   python -m delta.cli run qwen2:0.5b")
    print()
    print("If you get 'delta: command not found', use the Python module method.")
    print("Run 'python universal_delta_fix.py' to fix the PATH issue.")

def main():
    """Main installation process"""
    print("🚀 Delta Installation Script")
    print("=" * 50)
    
    # Step 1: Check Python version
    print("\n🔍 Step 1: Checking Python version...")
    if not check_python_version():
        return False
    
    # Step 2: Uninstall wrong delta package
    print("\n🔧 Step 2: Checking for conflicting packages...")
    uninstall_wrong_delta()
    
    # Step 3: Install Delta locally
    print("\n📦 Step 3: Installing Delta...")
    if not install_delta_local():
        return False
    
    # Step 4: Test delta command
    print("\n🧪 Step 4: Testing delta command...")
    delta_command_works = test_delta_command()
    
    # Step 5: Test Python module
    print("\n🧪 Step 5: Testing Python module...")
    python_module_works = test_python_module()
    
    if not delta_command_works and not python_module_works:
        print("❌ Both delta command and Python module failed")
        return False
    
    # Step 6: Setup Delta
    print("\n⚙️  Step 6: Setting up Delta...")
    setup_success = setup_delta()
    
    # Step 7: Create usage guide
    create_usage_guide()
    
    print("\n" + "=" * 50)
    print("📊 Installation Summary")
    print("=" * 50)
    print(f"✅ Delta installed: Yes")
    print(f"✅ Delta command works: {'Yes' if delta_command_works else 'No'}")
    print(f"✅ Python module works: {'Yes' if python_module_works else 'No'}")
    print(f"✅ Delta setup completed: {'Yes' if setup_success else 'No'}")
    
    if delta_command_works:
        print("\n🎉 Delta is ready to use!")
        print("Run 'delta --help' to get started")
    elif python_module_works:
        print("\n🎉 Delta is ready to use!")
        print("Run 'python -m delta.cli --help' to get started")
        print("Run 'python universal_delta_fix.py' to fix the PATH issue")
    else:
        print("\n❌ Installation failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
