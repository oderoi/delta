#!/usr/bin/env python3
"""
Fix llama.cpp binary installation
This script fixes the issue where the installer looks for 'main' but finds 'llama-cli'
"""

import os
import shutil
from pathlib import Path
import platform

def fix_llama_binary():
    """Fix the llama.cpp binary installation"""
    print("🔧 Fixing llama.cpp binary installation...")
    
    # Find the build directory
    home_dir = Path.home() / ".delta"
    build_dir = home_dir / "llama.cpp" / "build"
    
    if not build_dir.exists():
        print("❌ Build directory not found. Please run 'delta setup' first.")
        return False
    
    # Look for the actual binary
    possible_names = ["llama-cli", "main", "llama", "llama-server"]
    binary_source = None
    
    for name in possible_names:
        candidate = build_dir / name
        if candidate.exists() and candidate.is_file():
            binary_source = candidate
            print(f"✅ Found binary: {candidate}")
            break
    
    if not binary_source:
        print("❌ No binary found in build directory")
        print(f"Contents of {build_dir}:")
        for item in build_dir.iterdir():
            print(f"  - {item.name}")
        return False
    
    # Copy to the expected location
    bin_dir = home_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    binary_dest = bin_dir / "llama-main"
    
    try:
        shutil.copy(binary_source, binary_dest)
        
        # Make executable on Unix systems
        if platform.system() != 'Windows':
            binary_dest.chmod(0o755)
        
        print(f"✅ Copied binary to {binary_dest}")
        
        # Test the binary
        import subprocess
        try:
            result = subprocess.run([str(binary_dest), '--help'], 
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
            
    except Exception as e:
        print(f"❌ Failed to copy binary: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Fixing llama.cpp binary installation")
    print("=" * 50)
    
    if fix_llama_binary():
        print("\n🎉 Binary installation fixed!")
        print("You can now use Delta normally:")
        print("  delta run llama3.2:1b")
    else:
        print("\n❌ Failed to fix binary installation")
        print("Please run 'delta setup' again or contact support")

if __name__ == "__main__":
    main()
