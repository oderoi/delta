# 📱 iOS Installation Guide

## ✅ Quick Start

### Prerequisites

- iOS 13.0 or later
- Xcode 12.0 or later
- Python 3.8+ (via Pythonista or similar)
- Internet connection

### Method 1: Pythonista (Recommended)

```python
# In Pythonista, install Delta CLI
import subprocess
import sys

# Install Delta CLI
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'delta-cli'])

# Test installation
import delta.cli
```

### Method 2: Manual Integration

```swift
// Swift code to integrate llama.cpp
import Foundation

class LlamaCppManager {
    private let llamaPath: String
    
    init() {
        // Path to llama-main binary in app bundle
        self.llamaPath = Bundle.main.path(forResource: "llama-main", ofType: nil) ?? ""
    }
    
    func runModel(modelPath: String, prompt: String) -> String {
        // Implementation for running models
        return ""
    }
}
```

---

## 🔧 Detailed Installation

### Step 1: Download Pre-built llama.cpp

```bash
# Download pre-built llama.cpp for iOS
# Go to: https://github.com/ggerganov/llama.cpp/releases
# Download: llama-main-ios.zip

# Extract to your iOS app bundle
# Place in: YourApp.app/llama-main
```

### Step 2: Install Delta CLI

#### Option A: Pythonista

```python
# In Pythonista, install via pip
import subprocess
import sys

# Install Delta CLI
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'delta-cli'])

# Test installation
python -m delta.cli --help
```

#### Option B: Manual Integration

```swift
// Swift code to integrate Delta CLI
import Foundation

class DeltaCLIManager {
    private let deltaPath: String
    
    init() {
        // Path to Delta CLI in app bundle
        self.deltaPath = Bundle.main.path(forResource: "delta-cli", ofType: nil) ?? ""
    }
    
    func listModels() -> [String] {
        // Implementation for listing models
        return []
    }
    
    func pullModel(modelName: String) -> Bool {
        // Implementation for downloading models
        return true
    }
    
    func runModel(modelName: String, prompt: String) -> String {
        // Implementation for running models
        return ""
    }
}
```

### Step 3: Test Installation

```python
# Test Delta CLI
python -m delta.cli --help

# List available models
python -m delta.cli list

# Download a model
python -m delta.cli pull qwen2:0.5b

# Start chatting
python -m delta.cli run qwen2:0.5b
```

---

## 🚀 Alternative Methods

### Using Cocoapods

```ruby
# Podfile
platform :ios, '13.0'
use_frameworks!

target 'YourApp' do
  pod 'llama-cpp', '~> 1.0'
end
```

### Using Swift Package Manager

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/ggerganov/llama.cpp.git", from: "1.0.0")
]
```

### Using Carthage

```bash
# Cartfile
github "ggerganov/llama.cpp" "1.0.0"

# Install
carthage update
```

---

## 🔧 Troubleshooting

### Issue: Python not found

**Solution**: Install Pythonista

```bash
# Download Pythonista from App Store
# Or use alternative Python apps
```

### Issue: Xcode not found

**Solution**: Install Xcode

```bash
# Download Xcode from App Store
# Or use Xcode Command Line Tools
xcode-select --install
```

### Issue: Permission denied

**Solution**: Fix permissions

```bash
# Fix permissions in Xcode
# Go to: Project Settings → Build Phases → Run Script
# Add: chmod +x YourScript.sh
```

### Issue: Build failed

**Solution**: Check dependencies

```bash
# Check Xcode version
xcodebuild -version

# Check iOS deployment target
# Minimum: iOS 13.0
```

---

## 📋 System Requirements

- **OS**: iOS 13.0 or later
- **Python**: 3.8 or later (via Pythonista)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 1GB free space
- **Network**: Internet connection for model downloads

---

## 🎯 Quick Commands

```python
# Install Delta CLI
python -m pip install delta-cli

# Test installation
python -m delta.cli list

# Download model
python -m delta.cli pull qwen2:0.5b

# Start chatting
python -m delta.cli run qwen2:0.5b
```

---

## ✅ Success!

You now have Delta CLI working on iOS! The pre-built llama.cpp approach eliminates build issues and provides a smooth installation experience.

For more information, see:
- [Universal Installation Guide](UNIVERSAL_INSTALLATION_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
