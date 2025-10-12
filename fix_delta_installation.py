#!/usr/bin/env python3
"""
Comprehensive Delta Installation Fix
This script fixes all Delta installation issues including the llama.cpp binary problem
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

def check_delta_installation():
    """Check if Delta is properly installed"""
    print("🔍 Checking Delta installation...")
    
    try:
        result = subprocess.run(['delta', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Delta command works")
            return True
    except:
        pass
    
    try:
        result = subprocess.run([sys.executable, '-m', 'delta.cli', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Delta Python module works")
            return True
    except:
        pass
    
    print("❌ Delta not working")
    return False

def fix_llama_binary_issue():
    """Fix the llama.cpp binary issue"""
    print("\n🔧 Fixing llama.cpp binary issue...")
    
    # Check if we have a working binary
    home_dir = Path.home() / ".delta"
    bin_dir = home_dir / "bin"
    binary_path = bin_dir / "llama-main"
    
    if binary_path.exists():
        print("✅ llama.cpp binary already exists")
        return True
    
    # Try to find the binary in the build directory
    build_dir = home_dir / "llama.cpp" / "build"
    if build_dir.exists():
        print(f"🔍 Found build directory: {build_dir}")
        
        # Look for the actual binary
        possible_names = ["llama-cli", "main", "llama", "llama-server"]
        binary_source = None
        
        for name in possible_names:
            candidate = build_dir / name
            if candidate.exists() and candidate.is_file():
                binary_source = candidate
                print(f"✅ Found binary: {candidate}")
                break
        
        if binary_source:
            # Copy to the expected location
            bin_dir.mkdir(parents=True, exist_ok=True)
            binary_dest = bin_dir / "llama-main"
            
            try:
                shutil.copy(binary_source, binary_dest)
                
                # Make executable on Unix systems
                if platform.system() != 'Windows':
                    binary_dest.chmod(0o755)
                
                print(f"✅ Copied binary to {binary_dest}")
                
                # Test the binary
                try:
                    result = subprocess.run([str(binary_dest), '--help'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print("✅ Binary is working!")
                        return True
                    else:
                        print(f"❌ Binary test failed: {result.stderr}")
                except Exception as e:
                    print(f"❌ Binary test error: {e}")
                    
            except Exception as e:
                print(f"❌ Failed to copy binary: {e}")
        else:
            print("❌ No binary found in build directory")
            print(f"Contents of {build_dir}:")
            for item in build_dir.iterdir():
                print(f"  - {item.name}")
    else:
        print("❌ Build directory not found")
    
    return False

def reinstall_delta():
    """Reinstall Delta with the fixed installer"""
    print("\n🔧 Reinstalling Delta with fixes...")
    
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Install in development mode
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'], 
                      check=True)
        print("✅ Delta reinstalled successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to reinstall Delta: {e}")
        return False

def run_delta_setup():
    """Run delta setup with the fixed installer"""
    print("\n🔧 Running delta setup...")
    
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

def test_delta_functionality():
    """Test if Delta is working properly"""
    print("\n🧪 Testing Delta functionality...")
    
    # Test delta command
    try:
        result = subprocess.run(['delta', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Delta command works")
            return True
    except:
        pass
    
    # Test Python module
    try:
        result = subprocess.run([sys.executable, '-m', 'delta.cli', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Delta Python module works")
            return True
    except:
        pass
    
    print("❌ Delta functionality test failed")
    return False

def main():
    """Main function to fix all Delta issues"""
    print("🚀 Comprehensive Delta Installation Fix")
    print("=" * 50)
    
    # Step 1: Check current installation
    print("\n🔍 Step 1: Checking current installation...")
    if check_delta_installation():
        print("✅ Delta is already working!")
        return True
    
    # Step 2: Fix llama.cpp binary issue
    print("\n🔧 Step 2: Fixing llama.cpp binary issue...")
    if fix_llama_binary_issue():
        print("✅ llama.cpp binary fixed!")
    else:
        print("⚠️  llama.cpp binary issue not resolved")
    
    # Step 3: Reinstall Delta with fixes
    print("\n📦 Step 3: Reinstalling Delta with fixes...")
    if not reinstall_delta():
        print("❌ Failed to reinstall Delta")
        return False
    
    # Step 4: Run delta setup
    print("\n⚙️  Step 4: Running delta setup...")
    if not run_delta_setup():
        print("⚠️  Delta setup had issues, but continuing...")
    
    # Step 5: Test functionality
    print("\n🧪 Step 5: Testing functionality...")
    if test_delta_functionality():
        print("✅ Delta is working!")
        
        print("\n🎉 Delta installation fixed successfully!")
        print("You can now use Delta:")
        print("  delta --help")
        print("  delta run llama3.2:1b")
        print("  python -m delta.cli run llama3.2:1b")
        return True
    else:
        print("\n❌ Delta installation still has issues")
        print("Please try the manual installation method:")
        print("  python -m delta.cli setup")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
