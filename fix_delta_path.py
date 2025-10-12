#!/usr/bin/env python3
"""
Delta PATH Fix Script
This script fixes the PATH issue that prevents the 'delta' command from being found
"""

import sys
import os
import subprocess
import platform
from pathlib import Path
import shutil

def find_delta_executable():
    """Find the delta executable in the Python environment"""
    try:
        # Try to find delta in the current Python environment
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', 'delta'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # Parse the location from pip show output
            for line in result.stdout.split('\n'):
                if line.startswith('Location:'):
                    location = line.split(':', 1)[1].strip()
                    delta_path = Path(location) / 'delta'
                    if delta_path.exists():
                        return delta_path
    except Exception:
        pass
    
    # Try to find delta in the current environment
    try:
        import delta
        delta_path = Path(delta.__file__).parent
        return delta_path
    except ImportError:
        pass
    
    return None

def find_python_scripts_dir():
    """Find the Python scripts directory where console scripts are installed"""
    try:
        # Get the site-packages directory
        import site
        site_packages = site.getsitepackages()[0]
        scripts_dir = Path(site_packages).parent / 'Scripts' if platform.system() == 'Windows' else Path(site_packages).parent / 'bin'
        return scripts_dir
    except Exception:
        # Fallback method
        try:
            result = subprocess.run([sys.executable, '-c', 'import site; print(site.getsitepackages()[0])'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                site_packages = result.stdout.strip()
                scripts_dir = Path(site_packages).parent / 'Scripts' if platform.system() == 'Windows' else Path(site_packages).parent / 'bin'
                return scripts_dir
        except Exception:
            pass
    return None

def create_delta_wrapper():
    """Create a delta wrapper script that can be found in PATH"""
    scripts_dir = find_python_scripts_dir()
    if not scripts_dir:
        print("❌ Could not find Python scripts directory")
        return False
    
    # Create the scripts directory if it doesn't exist
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the wrapper script
    if platform.system() == 'Windows':
        wrapper_content = f'''@echo off
python -m delta.cli %*
'''
        wrapper_path = scripts_dir / 'delta.bat'
    else:
        wrapper_content = f'''#!/bin/bash
python -m delta.cli "$@"
'''
        wrapper_path = scripts_dir / 'delta'
    
    try:
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content)
        
        if platform.system() != 'Windows':
            wrapper_path.chmod(0o755)
        
        print(f"✅ Created delta wrapper at {wrapper_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create wrapper: {e}")
        return False

def add_to_path():
    """Add the Python scripts directory to PATH"""
    scripts_dir = find_python_scripts_dir()
    if not scripts_dir:
        print("❌ Could not find Python scripts directory")
        return False
    
    print(f"📁 Python scripts directory: {scripts_dir}")
    
    # Check if it's already in PATH
    current_path = os.environ.get('PATH', '')
    if str(scripts_dir) in current_path:
        print("✅ Python scripts directory is already in PATH")
        return True
    
    # Add to PATH for current session
    os.environ['PATH'] = f"{scripts_dir}{os.pathsep}{current_path}"
    print(f"✅ Added {scripts_dir} to PATH for current session")
    
    # Provide instructions for permanent PATH setup
    shell = os.environ.get('SHELL', '').lower()
    if platform.system() == 'Windows':
        print(f"\n🔧 To make this permanent, run:")
        print(f'setx PATH "%PATH%;{scripts_dir}"')
    elif 'zsh' in shell:
        profile = Path.home() / '.zshrc'
        export_line = f'export PATH="$PATH:{scripts_dir}"'
        print(f"\n🔧 To make this permanent, add to {profile}:")
        print(export_line)
    elif 'bash' in shell:
        profile = Path.home() / '.bashrc'
        export_line = f'export PATH="$PATH:{scripts_dir}"'
        print(f"\n🔧 To make this permanent, add to {profile}:")
        print(export_line)
    else:
        print(f"\n🔧 To make this permanent, add {scripts_dir} to your PATH")
    
    return True

def test_delta_command():
    """Test if the delta command works"""
    try:
        result = subprocess.run(['delta', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Delta command is working!")
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

def main():
    """Main function to fix the delta PATH issue"""
    print("🔧 Fixing Delta PATH Issue")
    print("=" * 40)
    
    # Step 1: Find Python scripts directory
    print("\n🔍 Step 1: Finding Python scripts directory...")
    scripts_dir = find_python_scripts_dir()
    if not scripts_dir:
        print("❌ Could not find Python scripts directory")
        return False
    print(f"✅ Found: {scripts_dir}")
    
    # Step 2: Create delta wrapper
    print("\n🔧 Step 2: Creating delta wrapper...")
    if not create_delta_wrapper():
        print("❌ Failed to create delta wrapper")
        return False
    
    # Step 3: Add to PATH
    print("\n📁 Step 3: Adding to PATH...")
    if not add_to_path():
        print("❌ Failed to add to PATH")
        return False
    
    # Step 4: Test delta command
    print("\n🧪 Step 4: Testing delta command...")
    if test_delta_command():
        print("\n🎉 Delta PATH issue fixed successfully!")
        print("You can now use 'delta' command from anywhere.")
        return True
    else:
        print("\n❌ Delta command still not working")
        print("Try running: python -m delta.cli --help")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
