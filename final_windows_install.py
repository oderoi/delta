#!/usr/bin/env python3
"""
Final Windows Installation Solution for Delta CLI
Comprehensive fix for all Windows installation issues
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path

def print_header():
    print("=" * 70)
    print("🔧 Delta CLI - Final Windows Installation Solution")
    print("=" * 70)
    print("This script will fix all Windows installation issues")
    print()

def check_system():
    """Check system requirements."""
    print("🔍 Checking system requirements...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required! Current: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    
    if platform.system() != 'Windows':
        print("❌ This script is for Windows only!")
        return False
    print(f"✅ Platform: {platform.system()} {platform.architecture()[0]}")
    
    return True

def clean_environment():
    """Clean conflicting packages."""
    print("\n🧹 Cleaning environment...")
    
    packages = ["delta", "delta-0.4.2", "delta-cli", "delta-ai"]
    for pkg in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", pkg, "-y"], 
                          capture_output=True)
            print(f"✅ Cleaned {pkg}")
        except:
            pass

def install_dependencies():
    """Install all required dependencies."""
    print("\n📦 Installing dependencies...")
    
    dependencies = [
        "requests>=2.31.0",
        "click>=8.1.0", 
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
        "huggingface_hub>=0.20.0",
        "tqdm>=4.66.0",
        "psutil>=5.9.0"
    ]
    
    for dep in dependencies:
        try:
            print(f"   Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                          check=True, capture_output=True)
            print(f"✅ {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}")
            return False
    
    return True

def install_delta_manual():
    """Install Delta manually."""
    print("\n🚀 Installing Delta manually...")
    
    try:
        # Get site-packages directory
        result = subprocess.run([sys.executable, "-c", 
                               "import site; print(site.getusersitepackages())"], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Could not find site-packages")
            return False
        
        site_packages = Path(result.stdout.strip())
        delta_dir = site_packages / "delta"
        
        # Create delta directory
        delta_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created {delta_dir}")
        
        # Copy all Python files from delta directory
        source_dir = Path("delta")
        if source_dir.exists():
            for file in source_dir.glob("*.py"):
                dest_file = delta_dir / file.name
                shutil.copy2(file, dest_file)
                print(f"✅ Copied {file.name}")
        else:
            print("❌ Delta source directory not found")
            return False
        
        # Create __init__.py if it doesn't exist
        init_file = delta_dir / "__init__.py"
        if not init_file.exists():
            with open(init_file, 'w') as f:
                f.write('"""Delta CLI package"""\n')
            print("✅ Created __init__.py")
        
        # Create entry point script
        scripts_dir = site_packages.parent / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        delta_bat = scripts_dir / "delta.bat"
        with open(delta_bat, 'w') as f:
            f.write('@echo off\npython -m delta.cli %*\n')
        print(f"✅ Created {delta_bat}")
        
        # Add to PATH for current session
        current_path = os.environ.get('PATH', '')
        if str(scripts_dir) not in current_path:
            os.environ['PATH'] = f"{scripts_dir};{current_path}"
            print(f"✅ Added {scripts_dir} to PATH")
        
        return True
        
    except Exception as e:
        print(f"❌ Manual installation failed: {e}")
        return False

def test_delta():
    """Test Delta installation."""
    print("\n🧪 Testing Delta...")
    
    try:
        # Test import
        import delta
        print("✅ Delta import works")
        
        # Test CLI
        result = subprocess.run([sys.executable, "-m", "delta.cli", "version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Delta CLI works")
            return True
        else:
            print(f"❌ Delta CLI failed: {result.stderr}")
            return False
            
    except ImportError as e:
        print(f"❌ Delta import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def setup_delta():
    """Setup Delta environment."""
    print("\n🔧 Setting up Delta...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "delta.cli", "setup"], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ Delta setup completed!")
            return True
        else:
            print(f"⚠️  Setup failed: {result.stderr}")
            print("   You can try manually: python -m delta.cli setup")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Setup timed out")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "delta.cli", "list"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Delta list command works!")
            return True
        else:
            print(f"⚠️  List command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def print_usage():
    """Print usage instructions."""
    print("\n" + "=" * 70)
    print("🎉 Installation Complete!")
    print("=" * 70)
    print()
    print("📋 Usage Instructions:")
    print()
    print("1. Download a model:")
    print("   python -m delta.cli pull qwen2:0.5b")
    print()
    print("2. Start chatting:")
    print("   python -m delta.cli run qwen2:0.5b")
    print()
    print("3. List available models:")
    print("   python -m delta.cli list")
    print()
    print("4. Get help:")
    print("   python -m delta.cli --help")
    print()
    print("5. Check system status:")
    print("   python -m delta.cli doctor")
    print()
    print("📚 For more information, see:")
    print("   - README.md")
    print("   - WINDOWS_INSTALLATION_GUIDE.md")
    print()
    print("🆘 If you have issues:")
    print("   - Run: python -m delta.cli doctor")
    print("   - Check WINDOWS_INSTALLATION_GUIDE.md")
    print("   - Report issues on GitHub")

def main():
    """Main installation function."""
    print_header()
    
    # Check system
    if not check_system():
        print("\n❌ System check failed!")
        return False
    
    # Clean environment
    clean_environment()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed!")
        return False
    
    # Install Delta manually
    if not install_delta_manual():
        print("\n❌ Delta installation failed!")
        return False
    
    # Test Delta
    if not test_delta():
        print("\n❌ Delta test failed!")
        return False
    
    # Setup Delta
    setup_delta()
    
    # Test basic functionality
    test_basic_functionality()
    
    # Print usage
    print_usage()
    
    print("\n✅ Windows installation completed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Delta CLI is ready to use on Windows!")
        else:
            print("\n❌ Installation failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
