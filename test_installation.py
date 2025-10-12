#!/usr/bin/env python3
"""
Delta Installation Test Script
Tests the installation and functionality across different platforms
"""

import sys
import os
import platform
import subprocess
import tempfile
from pathlib import Path

def test_python_version():
    """Test Python version compatibility"""
    print("🐍 Testing Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {sys.version.split()[0]} OK")
    return True

def test_imports():
    """Test that all modules can be imported"""
    print("📦 Testing imports...")
    
    required_modules = [
        'delta',
        'delta.installer',
        'delta.llama_cpp_wrapper',
        'delta.models',
        'delta.chat',
        'delta.cli'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            return False
    
    return True

def test_cli_commands():
    """Test CLI commands work"""
    print("🔧 Testing CLI commands...")
    
    commands = [
        ['delta', '--help'],
        ['delta', 'version'],
        ['delta', 'doctor']
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"  ✅ {' '.join(cmd)}")
            else:
                print(f"  ❌ {' '.join(cmd)}: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  {' '.join(cmd)}: Timeout")
        except FileNotFoundError:
            print(f"  ❌ {' '.join(cmd)}: Command not found")
            return False
    
    return True

def test_installer():
    """Test the installer functionality"""
    print("🔧 Testing installer...")
    
    try:
        from delta.installer import DeltaInstaller
        installer = DeltaInstaller()
        
        # Test platform detection
        platform_info = installer.platform_info
        print(f"  ✅ Platform detected: {platform_info['system']} {platform_info['architecture']}")
        
        # Test GPU detection
        gpu_support = platform_info['gpu_support']
        print(f"  ✅ GPU support: {gpu_support}")
        
        return True
    except Exception as e:
        print(f"  ❌ Installer test failed: {e}")
        return False

def test_llama_cpp_wrapper():
    """Test the llama.cpp wrapper"""
    print("🔧 Testing llama.cpp wrapper...")
    
    try:
        from delta.llama_cpp_wrapper import LlamaCppWrapper, GPUBackend, QuantizationType
        
        # Test enum imports
        print("  ✅ Enums imported successfully")
        
        # Test wrapper initialization (without binary)
        try:
            wrapper = LlamaCppWrapper()
            print("  ✅ Wrapper initialized")
        except FileNotFoundError:
            print("  ⚠️  llama.cpp binary not found (expected if not installed)")
        
        return True
    except Exception as e:
        print(f"  ❌ Wrapper test failed: {e}")
        return False

def test_models():
    """Test model management"""
    print("🔧 Testing model management...")
    
    try:
        from delta.models import list_models, init_config
        
        # Test config initialization
        init_config()
        print("  ✅ Config initialized")
        
        # Test model listing
        models = list_models()
        print(f"  ✅ Model listing works: {len(models['installed'])} installed, {len(models['available'])} available")
        
        return True
    except Exception as e:
        print(f"  ❌ Models test failed: {e}")
        return False

def test_cross_platform():
    """Test cross-platform compatibility"""
    print("🌍 Testing cross-platform compatibility...")
    
    system = platform.system()
    machine = platform.machine()
    
    print(f"  System: {system}")
    print(f"  Machine: {machine}")
    print(f"  Python: {sys.version}")
    
    # Test platform-specific features
    if system == 'Darwin':
        print("  ✅ macOS detected")
    elif system == 'Windows':
        print("  ✅ Windows detected")
    elif system == 'Linux':
        print("  ✅ Linux detected")
    else:
        print(f"  ⚠️  Unknown system: {system}")
    
    return True

def test_dependencies():
    """Test all dependencies are available"""
    print("📦 Testing dependencies...")
    
    dependencies = [
        'requests',
        'click',
        'tabulate',
        'colorama',
        'huggingface_hub',
        'tqdm',
        'psutil'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} - missing")
            missing.append(dep)
    
    if missing:
        print(f"  Missing dependencies: {', '.join(missing)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Delta Installation Test Suite")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Cross-platform", test_cross_platform),
        ("Installer", test_installer),
        ("LLaMA CPP Wrapper", test_llama_cpp_wrapper),
        ("Models", test_models),
        ("CLI Commands", test_cli_commands)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Delta is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
