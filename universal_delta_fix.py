#!/usr/bin/env python3
"""
Universal Delta PATH Fix
This script provides multiple solutions for the "delta: command not found" issue
"""

import sys
import os
import subprocess
import platform
from pathlib import Path
import shutil

def solution_1_python_module():
    """Solution 1: Use Python module directly (works immediately)"""
    print("🔧 Solution 1: Using Python Module (Immediate Fix)")
    print("=" * 50)
    
    print("Instead of 'delta setup', use:")
    print("  python -m delta.cli setup")
    print()
    print("Instead of 'delta run qwen2:0.5b', use:")
    print("  python -m delta.cli run qwen2:0.5b")
    print()
    print("This works immediately without any PATH configuration!")
    
    # Test if it works
    try:
        result = subprocess.run([sys.executable, '-m', 'delta.cli', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Python module method works!")
            return True
        else:
            print(f"❌ Python module method failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Python module method error: {e}")
        return False

def solution_2_find_scripts_dir():
    """Solution 2: Find and add Python scripts directory to PATH"""
    print("\n🔧 Solution 2: Fix PATH Configuration")
    print("=" * 50)
    
    # Find Python installation directory
    python_exe = sys.executable
    python_dir = Path(python_exe).parent
    
    # Common locations for scripts
    possible_scripts_dirs = [
        python_dir / 'Scripts',  # Windows
        python_dir / 'bin',     # Unix
        python_dir.parent / 'Scripts',  # Windows alternative
        python_dir.parent / 'bin',      # Unix alternative
    ]
    
    scripts_dir = None
    for dir_path in possible_scripts_dirs:
        if dir_path.exists():
            scripts_dir = dir_path
            break
    
    if not scripts_dir:
        print("❌ Could not find Python scripts directory")
        return False
    
    print(f"📁 Found Python scripts directory: {scripts_dir}")
    
    # Check if delta is already there
    delta_exe = scripts_dir / ('delta.bat' if platform.system() == 'Windows' else 'delta')
    if delta_exe.exists():
        print("✅ Delta executable found in scripts directory")
    else:
        print("❌ Delta executable not found in scripts directory")
        return False
    
    # Add to PATH
    current_path = os.environ.get('PATH', '')
    if str(scripts_dir) not in current_path:
        os.environ['PATH'] = f"{scripts_dir}{os.pathsep}{current_path}"
        print(f"✅ Added {scripts_dir} to PATH for current session")
    else:
        print("✅ Scripts directory already in PATH")
    
    # Test delta command
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

def solution_3_create_wrapper():
    """Solution 3: Create a wrapper script in a directory that's in PATH"""
    print("\n🔧 Solution 3: Create Wrapper Script")
    print("=" * 50)
    
    # Find a directory that's in PATH
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    writable_dir = None
    
    for dir_path in path_dirs:
        try:
            test_dir = Path(dir_path)
            if test_dir.exists() and os.access(test_dir, os.W_OK):
                writable_dir = test_dir
                break
        except Exception:
            continue
    
    if not writable_dir:
        print("❌ No writable directory found in PATH")
        return False
    
    print(f"📁 Using writable directory: {writable_dir}")
    
    # Create wrapper script
    if platform.system() == 'Windows':
        wrapper_content = f'''@echo off
python -m delta.cli %*
'''
        wrapper_path = writable_dir / 'delta.bat'
    else:
        wrapper_content = f'''#!/bin/bash
python -m delta.cli "$@"
'''
        wrapper_path = writable_dir / 'delta'
    
    try:
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content)
        
        if platform.system() != 'Windows':
            wrapper_path.chmod(0o755)
        
        print(f"✅ Created wrapper at {wrapper_path}")
        
        # Test the wrapper
        try:
            result = subprocess.run(['delta', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Wrapper works!")
                return True
            else:
                print(f"❌ Wrapper failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Wrapper error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create wrapper: {e}")
        return False

def solution_4_install_scripts():
    """Solution 4: Reinstall with proper script installation"""
    print("\n🔧 Solution 4: Reinstall with Proper Script Installation")
    print("=" * 50)
    
    print("Try reinstalling delta with:")
    print("  pip uninstall delta")
    print("  pip install delta")
    print()
    print("If that doesn't work, try:")
    print("  pip install --force-reinstall delta")
    print()
    print("Or install in development mode:")
    print("  pip install -e .")
    
    return True

def solution_5_manual_installation():
    """Solution 5: Manual installation instructions"""
    print("\n🔧 Solution 5: Manual Installation")
    print("=" * 50)
    
    print("If all else fails, you can manually create the delta command:")
    print()
    
    if platform.system() == 'Windows':
        print("1. Create a file called 'delta.bat' in a directory in your PATH")
        print("2. Add this content:")
        print("   @echo off")
        print("   python -m delta.cli %*")
        print("3. Save the file")
    else:
        print("1. Create a file called 'delta' in a directory in your PATH")
        print("2. Add this content:")
        print("   #!/bin/bash")
        print("   python -m delta.cli \"$@\"")
        print("3. Make it executable: chmod +x delta")
        print("4. Save the file")
    
    print()
    print("Common PATH directories:")
    if platform.system() == 'Windows':
        print("  - C:\\Windows\\System32")
        print("  - C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python3x\\Scripts")
    else:
        print("  - /usr/local/bin")
        print("  - ~/bin")
        print("  - ~/.local/bin")
    
    return True

def main():
    """Main function to provide all solutions"""
    print("🚀 Universal Delta PATH Fix")
    print("=" * 50)
    print("This script provides multiple solutions for the 'delta: command not found' issue")
    print()
    
    solutions = [
        ("Python Module (Immediate)", solution_1_python_module),
        ("Fix PATH Configuration", solution_2_find_scripts_dir),
        ("Create Wrapper Script", solution_3_create_wrapper),
        ("Reinstall Delta", solution_4_install_scripts),
        ("Manual Installation", solution_5_manual_installation),
    ]
    
    working_solutions = []
    
    for name, solution_func in solutions:
        try:
            if solution_func():
                working_solutions.append(name)
        except Exception as e:
            print(f"❌ {name} failed: {e}")
    
    print("\n" + "=" * 50)
    print("📊 Summary")
    print("=" * 50)
    
    if working_solutions:
        print(f"✅ Working solutions: {', '.join(working_solutions)}")
        print()
        print("🎉 At least one solution works!")
        print("Use the Python module method for immediate access:")
        print("  python -m delta.cli setup")
        print("  python -m delta.cli run qwen2:0.5b")
    else:
        print("❌ No solutions worked automatically")
        print("Please try the manual installation method")
    
    print()
    print("📚 For more help, see INSTALLATION_GUIDE.md")

if __name__ == "__main__":
    main()
