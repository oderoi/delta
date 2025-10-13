# 🌍 Universal Delta CLI Installation Guide

## 📱 Supported Platforms

| Platform | Status | Installation Method |
|----------|--------|-------------------|
| **Windows** | ✅ | Winget, Manual |
| **macOS** | ✅ | Homebrew, MacPorts, Nix |
| **Linux** | ✅ | Homebrew, Nix, Manual |
| **iOS** | ✅ | Manual (Pre-built) |
| **Android** | ✅ | Manual (Pre-built) |

---

## 🪟 Windows Installation

See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for complete Windows installation guide.

---

## 🍎 macOS Installation

### Method 1: Homebrew (Recommended)

```bash
# Install pre-built llama.cpp
brew install llama.cpp

# Install Delta CLI
python -m pip install -e .
```

### Method 2: MacPorts

```bash
# Install pre-built llama.cpp
sudo port install llama.cpp

# Install Delta CLI
python -m pip install -e .
```

### Method 3: Nix

```bash
# Install pre-built llama.cpp
nix profile install nixpkgs#llama-cpp

# Install Delta CLI
python -m pip install -e .
```

### Method 4: Manual Installation

```bash
# Download pre-built llama.cpp
# Go to: https://github.com/ggerganov/llama.cpp/releases
# Download: llama-main-macos.zip
# Extract to: ~/.delta/bin/
# Rename to: llama-main

# Install Delta CLI
python -m pip install -e .
```

---

## 🐧 Linux Installation

### Method 1: Homebrew (Recommended)

```bash
# Install pre-built llama.cpp
brew install llama.cpp

# Install Delta CLI
python -m pip install -e .
```

### Method 2: Nix

```bash
# Install pre-built llama.cpp
nix profile install nixpkgs#llama-cpp

# Install Delta CLI
python -m pip install -e .
```

### Method 3: Manual Installation

```bash
# Download pre-built llama.cpp
# Go to: https://github.com/ggerganov/llama.cpp/releases
# Download: llama-main-linux-x64.zip
# Extract to: ~/.delta/bin/
# Rename to: llama-main

# Install Delta CLI
python -m pip install -e .
```

---

## 📱 iOS Installation

### Prerequisites

- iOS 13.0 or later
- Xcode (for development)
- Python 3.8+ (via Pythonista or similar)

### Installation Steps

```bash
# 1. Download pre-built llama.cpp for iOS
# Go to: https://github.com/ggerganov/llama.cpp/releases
# Download: llama-main-ios.zip

# 2. Extract to your iOS app bundle
# Place in: YourApp.app/llama-main

# 3. Install Delta CLI (if using Pythonista)
# In Pythonista, install via pip:
pip install delta-cli
```

### iOS App Integration

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

## 🤖 Android Installation

### Prerequisites

- Android 7.0 (API level 24) or later
- Android Studio (for development)
- Python 3.8+ (via Termux or similar)

### Installation Steps

```bash
# 1. Download pre-built llama.cpp for Android
# Go to: https://github.com/ggerganov/llama.cpp/releases
# Download: llama-main-android.zip

# 2. Extract to your Android app
# Place in: app/src/main/assets/llama-main

# 3. Install Delta CLI (if using Termux)
# In Termux, install via pip:
pip install delta-cli
```

### Android App Integration

```java
// Java code to integrate llama.cpp
public class LlamaCppManager {
    private String llamaPath;
    
    public LlamaCppManager(Context context) {
        // Path to llama-main binary in assets
        this.llamaPath = context.getFilesDir().getAbsolutePath() + "/llama-main";
    }
    
    public String runModel(String modelPath, String prompt) {
        // Implementation for running models
        return "";
    }
}
```

---

## 🧪 Testing Installation

After installation on any platform, test with:

```bash
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

## 🔧 Troubleshooting

### Common Issues

1. **CURL not found**: Use pre-built binaries instead of building from source
2. **Permission denied**: Run as administrator (Windows) or use sudo (Linux/macOS)
3. **Python not found**: Install Python 3.8+ from python.org
4. **Build tools missing**: Use pre-built binaries instead of building from source

### Platform-Specific Solutions

#### Windows
See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for complete Windows troubleshooting.

#### macOS
```bash
# Fix Homebrew
brew update && brew upgrade

# Use pre-built llama.cpp
brew install llama.cpp
```

#### Linux
```bash
# Fix permissions
sudo chown -R $USER:$USER ~/.delta

# Use pre-built llama.cpp
brew install llama.cpp
```

---

## 📋 Quick Start

### 1. Choose Your Platform
- **Windows**: See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)
- **macOS**: Use `brew install llama.cpp`
- **Linux**: Use `brew install llama.cpp` or `nix profile install nixpkgs#llama-cpp`
- **iOS/Android**: Download pre-built binaries manually

### 2. Install Delta CLI
```bash
python -m pip install -e .
```

### 3. Test Installation
```bash
python -m delta.cli list
python -m delta.cli pull qwen2:0.5b
python -m delta.cli run qwen2:0.5b
```

---

## 🎉 Success!

You now have Delta CLI working on your platform! The pre-built llama.cpp approach eliminates build issues and provides a smooth installation experience across all devices.

For more information, see the platform-specific guides:
- [Windows Installation](WINDOWS_INSTALL.md)
- [macOS Installation](MACOS_INSTALL.md)
- [Linux Installation](LINUX_INSTALL.md)
- [iOS Installation](IOS_INSTALL.md)
- [Android Installation](ANDROID_INSTALL.md)
