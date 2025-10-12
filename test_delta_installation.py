#!/usr/bin/env python3
"""
Delta Installation Test Script
Run this script to test if Delta is properly installed and working
"""

import sys
import subprocess
import platform
from pathlib import Path

def test_delta_import():
    """Test if Delta can be imported"""
    try:
        import delta
        print("✅ Delta module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Delta import failed: {e}")
        return False

def test_delta_cli():
    """Test if Delta CLI is available"""
    try:
        result = subprocess.run(['delta', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Delta CLI is working")
            return True
        else:
            print(f"❌ Delta CLI failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Delta CLI not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Delta CLI timed out")
        return False
    except Exception as e:
        print(f"❌ Delta CLI error: {e}")
        return False

def test_llama_binary():
    """Test if llama.cpp binary is available"""
    try:
        # Check if binary exists in expected location
        home_dir = Path.home() / ".delta" / "bin" / "llama-main"
        if home_dir.exists():
            print("✅ llama.cpp binary found")
            
            # Test if binary is executable
            if platform.system() != 'Windows':
                if home_dir.stat().st_mode & 0o111:
                    print("✅ Binary is executable")
                else:
                    print("❌ Binary is not executable")
                    return False
            
            # Test if binary runs
            result = subprocess.run([str(home_dir), '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ llama.cpp binary is working")
                return True
            else:
                print(f"❌ llama.cpp binary failed: {result.stderr}")
                return False
        else:
            print("❌ llama.cpp binary not found")
            return False
    except Exception as e:
        print(f"❌ Binary test error: {e}")
        return False

def test_platform_detection():
    """Test platform detection"""
    try:
        from delta.installer import DeltaInstaller
        installer = DeltaInstaller()
        
        print(f"Platform: {installer.platform_info['system']} {installer.platform_info['architecture']}")
        print(f"GPU Support: {installer.platform_info['gpu_support']}")
        
        # Validate platform info
        assert installer.platform_info['system'] in ['windows', 'darwin', 'linux']
        assert installer.platform_info['architecture'] in ['x64', 'arm64', 'armv7']
        
        print("✅ Platform detection working")
        return True
    except Exception as e:
        print(f"❌ Platform detection failed: {e}")
        return False

def test_model_management():
    """Test model management functionality"""
    try:
        from delta.models import list_models
        models = list_models()
        print(f"✅ Model management working (found {len(models['installed'])} installed models)")
        return True
    except Exception as e:
        print(f"❌ Model management failed: {e}")
        return False

def run_all_tests():
    """Run all installation tests"""
    print("🧪 Testing Delta Installation")
    print("=" * 40)
    
    tests = [
        ("Delta Import", test_delta_import),
        ("Platform Detection", test_platform_detection),
        ("Model Management", test_model_management),
        ("llama.cpp Binary", test_llama_binary),
        ("Delta CLI", test_delta_cli),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Delta is properly installed.")
        return True
    else:
        print("❌ Some tests failed. Please run 'delta setup' to fix issues.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
