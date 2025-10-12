#!/usr/bin/env python3
"""
Quick Fix for Delta Phone Installation Issues
This script specifically addresses the 'ModuleNotFoundError: No module named 'click'' error
"""

import subprocess
import sys
import os

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

def fix_click_dependency():
    """Fix the missing click dependency issue."""
    print("🔧 Fixing click dependency...")
    
    # Install click specifically
    result = run_command("pip3 install click", check=False)
    if result.returncode != 0:
        print("⚠️  pip3 install click failed, trying alternative...")
        run_command("python3 -m pip install click", check=False)
    
    # Test click import
    test_result = run_command("python3 -c 'import click; print(\"Click imported successfully\")'", check=False)
    if test_result.returncode == 0:
        print("✅ Click dependency fixed!")
        return True
    else:
        print("❌ Click dependency still missing")
        return False

def fix_all_dependencies():
    """Install all missing dependencies."""
    print("🔧 Installing all dependencies...")
    
    dependencies = [
        "click",
        "requests", 
        "tabulate",
        "colorama",
        "huggingface_hub",
        "tqdm",
        "psutil"
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        result = run_command(f"pip3 install {dep}", check=False)
        if result.returncode != 0:
            print(f"⚠️  Failed to install {dep}, trying alternative...")
            run_command(f"python3 -m pip install {dep}", check=False)

def test_delta_cli():
    """Test if delta CLI works after fixes."""
    print("🧪 Testing Delta CLI...")
    
    # Test import
    result = run_command("python3 -c 'from delta.cli import cli; print(\"Delta CLI imported successfully\")'", check=False)
    if result.returncode != 0:
        print("❌ Delta CLI import failed")
        return False
    
    # Test command
    result = run_command("python3 -m delta.cli --help", check=False)
    if result.returncode != 0:
        print("❌ Delta CLI command failed")
        return False
    
    print("✅ Delta CLI is working!")
    return True

def main():
    """Main fix process."""
    print("🚀 Delta Phone Quick Fix")
    print("=" * 30)
    
    # Step 1: Fix click dependency
    print("\n🔧 Step 1: Fixing click dependency...")
    if not fix_click_dependency():
        print("⚠️  Click fix failed, trying comprehensive approach...")
        fix_all_dependencies()
    
    # Step 2: Test Delta CLI
    print("\n🧪 Step 2: Testing Delta CLI...")
    if test_delta_cli():
        print("\n🎉 Fix successful!")
        print("\nYou can now use Delta with:")
        print("  python3 -m delta.cli --help")
        print("  python3 -m delta.cli setup")
        print("  python3 -m delta.cli run")
        return True
    else:
        print("\n❌ Fix failed. Try running the full installation script:")
        print("  python3 install_delta_phone.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
