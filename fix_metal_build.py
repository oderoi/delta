#!/usr/bin/env python3
"""
Fix Metal Build Issues for Delta
This script provides immediate solutions for the Metal compilation error
"""

import subprocess
import sys
import os
from pathlib import Path

def check_homebrew():
    """Check if Homebrew is available"""
    try:
        result = subprocess.run(['which', 'brew'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def install_via_homebrew():
    """Install llama.cpp via Homebrew"""
    print("🍺 Installing llama.cpp via Homebrew...")
    
    try:
        # Install llama.cpp
        result = subprocess.run(['brew', 'install', 'llama.cpp'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ llama.cpp installed via Homebrew")
            return True
        else:
            print(f"❌ Homebrew installation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Homebrew installation timed out")
        return False
    except Exception as e:
        print(f"❌ Homebrew installation error: {e}")
        return False

def create_symlink():
    """Create symlink to expected location"""
    try:
        # Find llama-cli binary
        result = subprocess.run(['which', 'llama-cli'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ llama-cli binary not found")
            return False
        
        llama_cli_path = result.stdout.strip()
        
        # Create .delta/bin directory
        home_dir = Path.home() / ".delta"
        bin_dir = home_dir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        
        # Create symlink
        binary_dest = bin_dir / "llama-main"
        if binary_dest.exists():
            binary_dest.unlink()  # Remove existing symlink
        
        os.symlink(llama_cli_path, str(binary_dest))
        print(f"✅ Created symlink: {binary_dest} -> {llama_cli_path}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create symlink: {e}")
        return False

def test_installation():
    """Test if the installation works"""
    try:
        # Test the binary
        home_dir = Path.home() / ".delta"
        binary_path = home_dir / "bin" / "llama-main"
        
        if not binary_path.exists():
            print("❌ Binary not found")
            return False
        
        # Test with --help
        result = subprocess.run([str(binary_path), '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Binary is working!")
            return True
        else:
            print(f"❌ Binary test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Binary test error: {e}")
        return False

def main():
    """Main function to fix Metal build issues"""
    print("🔧 Fixing Metal Build Issues for Delta")
    print("=" * 50)
    
    # Check if Homebrew is available
    if not check_homebrew():
        print("❌ Homebrew not found. Please install Homebrew first:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False
    
    print("✅ Homebrew found")
    
    # Install llama.cpp via Homebrew
    if not install_via_homebrew():
        print("❌ Failed to install llama.cpp via Homebrew")
        return False
    
    # Create symlink
    if not create_symlink():
        print("❌ Failed to create symlink")
        return False
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        return False
    
    print("\n🎉 Metal build issues fixed!")
    print("You can now use Delta:")
    print("  delta run llama3.2:1b")
    print("  python -m delta.cli run llama3.2:1b")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
