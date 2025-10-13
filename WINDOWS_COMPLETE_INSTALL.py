#!/usr/bin/env python3
"""
Delta CLI - Complete Windows Installation & Usage Guide
This is the ONLY Windows installation file you need!
Includes installation, model download, and model running instructions.
"""

import sys
import os
import subprocess
import platform
import shutil
import tempfile
import requests
import zipfile
from pathlib import Path

def print_header():
    print("=" * 60)
    print("Delta CLI - Complete Windows Installation & Usage")
    print("=" * 60)
    print()

def print_status(message, status="OK"):
    color = "32" if status == "OK" else "31" if status == "ERROR" else "33"
    print(f"\033[{color}m{status}:\033[0m {message}")

def check_system():
    """Check system requirements."""
    print("Checking system requirements...")
    
    # Check Python version
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_status(f"Python 3.8+ required! Current: {version.major}.{version.minor}.{version.micro}", "ERROR")
        return False
    print_status(f"Python {version.major}.{version.minor}.{version.micro}")
    
    # Check platform
    if platform.system() != 'Windows':
        print_status("This script is for Windows only!", "ERROR")
        return False
    print_status(f"Platform: {platform.system()}")
    
    return True

def clean_packages():
    """Remove conflicting packages."""
    print("\nCleaning conflicting packages...")
    
    packages = ["delta", "delta-0.4.2", "delta-cli", "delta-ai"]
    for pkg in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", pkg, "-y"], 
                          capture_output=True)
            print_status(f"Cleaned {pkg}")
        except:
            pass

def install_dependencies():
    """Install dependencies."""
    print("\nInstalling dependencies...")
    
    deps = [
        "requests>=2.31.0",
        "click>=8.1.0", 
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
        "huggingface_hub>=0.20.0",
        "tqdm>=4.66.0",
        "psutil>=5.9.0"
    ]
    
    for dep in deps:
        try:
            print(f"   Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                          check=True, capture_output=True)
            print_status(f"{dep}")
        except subprocess.CalledProcessError as e:
            print_status(f"Failed to install {dep}: {e}", "ERROR")
            return False
    
    return True

def install_delta_manual():
    """Install Delta manually."""
    print("\nInstalling Delta CLI...")
    
    try:
        # Get site-packages directory
        result = subprocess.run([sys.executable, "-c", 
                               "import site; print(site.getusersitepackages())"], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            print_status("Could not find site-packages", "ERROR")
            return False
        
        site_packages = Path(result.stdout.strip())
        delta_dir = site_packages / "delta"
        
        # Create delta directory
        delta_dir.mkdir(parents=True, exist_ok=True)
        print_status(f"Created {delta_dir}")
        
        # Copy all Python files from delta directory
        source_dir = Path("delta")
        if source_dir.exists():
            for file in source_dir.glob("*.py"):
                dest_file = delta_dir / file.name
                shutil.copy2(file, dest_file)
                print_status(f"Copied {file.name}")
        else:
            print_status("Delta source directory not found", "ERROR")
            return False
        
        # Create __init__.py if it doesn't exist
        init_file = delta_dir / "__init__.py"
        if not init_file.exists():
            with open(init_file, 'w') as f:
                f.write('"""Delta CLI package"""\n')
            print_status("Created __init__.py")
        
        # Create entry point script in the correct Scripts directory
        # Use the system Python Scripts directory that's already in PATH
        import sysconfig
        scripts_dir = Path(sysconfig.get_path('scripts'))
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        delta_bat = scripts_dir / "delta.bat"
        with open(delta_bat, 'w') as f:
            f.write('@echo off\npython -m delta.cli %*\n')
        print_status(f"Created {delta_bat}")
        
        # Also create in user Scripts directory as backup
        user_scripts_dir = site_packages.parent / "Scripts"
        user_scripts_dir.mkdir(parents=True, exist_ok=True)
        user_delta_bat = user_scripts_dir / "delta.bat"
        with open(user_delta_bat, 'w') as f:
            f.write('@echo off\npython -m delta.cli %*\n')
        print_status(f"Created backup {user_delta_bat}")
        
        # Add user Scripts to PATH for current session if not already there
        current_path = os.environ.get('PATH', '')
        if str(user_scripts_dir) not in current_path:
            os.environ['PATH'] = f"{user_scripts_dir};{current_path}"
            print_status(f"Added {user_scripts_dir} to PATH")
        
        return True
        
    except Exception as e:
        print_status(f"Manual installation failed: {e}", "ERROR")
        return False

def setup_llama_cpp():
    """Setup llama.cpp by downloading the real binary."""
    print("\nSetting up llama.cpp...")
    
    # Create .delta/bin directory
    delta_dir = Path.home() / ".delta"
    bin_dir = delta_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    llama_main_path = bin_dir / "llama-main.exe"
    
    # Check if a real llama.cpp binary already exists
    if llama_main_path.exists() and llama_main_path.is_file() and llama_main_path.stat().st_size > 10 * 1024 * 1024: # >10MB heuristic for real binary
        print_status("Real llama.cpp binary already exists")
        return True

    # Attempt to download the latest pre-built binary
    print_status("Attempting to download pre-built llama.cpp...")
    release_url = "https://api.github.com/repos/ggerganov/llama.cpp/releases/latest"
    try:
        response = requests.get(release_url, timeout=10)
        response.raise_for_status()
        latest_release = response.json()
        
        download_url = None
        for asset in latest_release['assets']:
            if "llama-b6746-bin-win-cpu-x64.zip" in asset['name']:
                download_url = asset['browser_download_url']
                break
        
        if download_url:
            print_status(f"Downloading from: {download_url}")
            zip_path = bin_dir / "llama-main-win64.zip"
            with requests.get(download_url, stream=True, timeout=300) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                from tqdm import tqdm
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading llama.cpp") as pbar:
                    with open(zip_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            print_status("Extracting llama.cpp...")
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Extract to a temporary directory first
                    temp_dir = bin_dir / "temp_extract"
                    temp_dir.mkdir(exist_ok=True)
                    zip_ref.extractall(temp_dir)
                    
                    # Move files from temp to final location
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            src = Path(root) / file
                            dst = bin_dir / file
                            try:
                                if dst.exists():
                                    dst.unlink()  # Remove existing file
                                shutil.move(str(src), str(dst))
                            except PermissionError:
                                print_status(f"Could not move {file}, file may be in use", "WARNING")
                                continue
                    
                    # Clean up temp directory
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    
            except Exception as e:
                print_status(f"Failed to extract: {e}", "ERROR")
                return False
            
            # Find the extracted executable (look for llama-cli.exe)
            extracted_exe = None
            for root, dirs, files in os.walk(bin_dir):
                for file in files:
                    if file == "llama-cli.exe":
                        extracted_exe = Path(root) / file
                        break
                if extracted_exe:
                    break
            
            if extracted_exe and extracted_exe.exists():
                # Copy to the correct location and rename
                shutil.copy2(str(extracted_exe), str(llama_main_path))
                print_status(f"Downloaded and extracted real llama.cpp to {llama_main_path}")
                zip_path.unlink() # Clean up zip file
                return True
            else:
                print_status("Extracted llama.cpp executable not found", "ERROR")
                return False
        else:
            print_status("No Windows binary found in latest release", "ERROR")
    except requests.exceptions.RequestException as e:
        print_status(f"Failed to download llama.cpp: {e}", "ERROR")
    except Exception as e:
        print_status(f"Failed to process llama.cpp download: {e}", "ERROR")

    print_status("Failed to download llama.cpp, creating wrapper...", "WARNING")
    # Fallback to creating a wrapper script if download fails
    return create_llama_cpp_wrapper()

def create_llama_cpp_wrapper():
    """Create a wrapper script with instructions."""
    bin_dir = Path.home() / ".delta" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    
    # Create wrapper with clear instructions
    wrapper_content = '''@echo off
REM llama.cpp wrapper
REM This provides helpful instructions when llama.cpp is not found

echo ERROR: llama.cpp not found!
echo.
echo To fix this, install llama.cpp manually:
echo.
echo 1. Go to: https://github.com/ggerganov/llama.cpp/releases
echo 2. Download: llama-main-win64.zip
echo 3. Extract to: %USERPROFILE%\\.delta\\bin\\
echo 4. Rename to: llama-main.exe
echo.
echo After installation, try again:
echo   python -m delta.cli run qwen2:0.5b
echo.
exit /b 1
'''
    
    # Create wrapper files
    batch_file = bin_dir / "llama-main.bat"
    exe_file = bin_dir / "llama-main.exe"
    
    try:
        with open(batch_file, 'w') as f:
            f.write(wrapper_content)
        print_status(f"Created llama.cpp wrapper at {batch_file}")
    except Exception as e:
        print_status(f"Failed to create batch wrapper: {e}", "ERROR")
    
    try:
        # Remove existing file if it exists and is locked
        if exe_file.exists():
            exe_file.unlink()
        with open(exe_file, 'w') as f:
            f.write(wrapper_content)
        print_status(f"Created llama.cpp wrapper at {exe_file}")
    except Exception as e:
        print_status(f"Failed to create exe wrapper: {e}", "ERROR")
        # Create a .txt file instead as fallback
        txt_file = bin_dir / "llama-main.txt"
        try:
            with open(txt_file, 'w') as f:
                f.write(wrapper_content)
            print_status(f"Created fallback wrapper at {txt_file}")
        except Exception as e2:
            print_status(f"Failed to create fallback wrapper: {e2}", "ERROR")
    
    return True

def test_delta():
    """Test Delta installation."""
    print("\nTesting Delta...")
    
    try:
        # Test import
        import delta
        print_status("Delta import works")
        
        # Test CLI
        result = subprocess.run([sys.executable, "-m", "delta.cli", "version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print_status("Delta CLI works")
            return True
        else:
            print_status(f"Delta CLI failed: {result.stderr}", "ERROR")
            return False
            
    except ImportError as e:
        print_status(f"Delta import failed: {e}", "ERROR")
        return False
    except Exception as e:
        print_status(f"Test error: {e}", "ERROR")
        return False

def test_model_functionality():
    """Test model functionality."""
    print("\nTesting model functionality...")
    
    try:
        # Test model listing
        result = subprocess.run([sys.executable, "-m", "delta.cli", "list"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print_status("Model listing works")
        else:
            print_status(f"Model listing failed: {result.stderr}", "ERROR")
            return False
        
        return True
        
    except Exception as e:
        print_status(f"Model test error: {e}", "ERROR")
        return False

def print_usage_instructions():
    """Print comprehensive usage instructions."""
    print("\n" + "=" * 60)
    print("INSTALLATION COMPLETE!")
    print("=" * 60)
    print()
    print("USAGE INSTRUCTIONS:")
    print()
    print("1. LIST AVAILABLE MODELS:")
    print("   python -m delta.cli list")
    print()
    print("2. DOWNLOAD MODELS:")
    print("   python -m delta.cli pull qwen2:0.5b")
    print("   python -m delta.cli pull tinyllama")
    print("   python -m delta.cli pull qwen3:0.6b")
    print()
    print("3. RUN MODELS (CHAT):")
    print("   python -m delta.cli run qwen2:0.5b")
    print("   python -m delta.cli run tinyllama")
    print("   python -m delta.cli run qwen3:0.6b")
    print()
    print("4. OTHER COMMANDS:")
    print("   python -m delta.cli --help")
    print("   python -m delta.cli version")
    print("   python -m delta.cli doctor")
    print()
    print("5. IF MODEL RUNNING FAILS:")
    print("   The llama.cpp binary may need to be installed manually.")
    print("   Go to: https://github.com/ggerganov/llama.cpp/releases")
    print("   Download: llama-main-win64.zip")
    print("   Extract to: %USERPROFILE%\\.delta\\bin\\")
    print("   Rename to: llama-main.exe")
    print()
    print("6. TROUBLESHOOTING:")
    print("   - If download fails: Check internet connection")
    print("   - If run fails: Install real llama.cpp binary")
    print("   - If import fails: Reinstall Delta CLI")
    print()

def main():
    """Main installation function."""
    print_header()
    
    # Check system
    if not check_system():
        print_status("System check failed!", "ERROR")
        return False
    
    # Clean packages
    clean_packages()
    
    # Install dependencies
    if not install_dependencies():
        print_status("Dependency installation failed!", "ERROR")
        return False
    
    # Install Delta manually
    if not install_delta_manual():
        print_status("Delta installation failed!", "ERROR")
        return False
    
    # Setup llama.cpp
    setup_llama_cpp()
    
    # Test Delta
    if not test_delta():
        print_status("Delta test failed!", "ERROR")
        return False
    
    # Test model functionality
    if not test_model_functionality():
        print_status("Model functionality test failed!", "ERROR")
        return False
    
    # Print usage instructions
    print_usage_instructions()
    
    print_status("Windows installation completed!", "SUCCESS")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nDelta CLI is ready to use on Windows!")
            print("\nQuick start:")
            print("  python -m delta.cli list")
            print("  python -m delta.cli pull qwen2:0.5b")
            print("  python -m delta.cli run qwen2:0.5b")
        else:
            print("\nInstallation failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        print(f"Full error traceback: {traceback.format_exc()}")
        sys.exit(1)