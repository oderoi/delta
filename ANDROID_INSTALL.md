# 🤖 Android Installation Guide

## ✅ Quick Start

### Prerequisites

- Android 7.0 (API level 24) or later
- Android Studio 4.0 or later
- Python 3.8+ (via Termux or similar)
- Internet connection

### Method 1: Termux (Recommended)

```bash
# In Termux, install Delta CLI
pkg install python
pip install delta-cli

# Test installation
python -m delta.cli --help
```

### Method 2: Manual Integration

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

## 🔧 Detailed Installation

### Step 1: Download Pre-built llama.cpp

```bash
# Download pre-built llama.cpp for Android
# Go to: https://github.com/ggerganov/llama.cpp/releases
# Download: llama-main-android.zip

# Extract to your Android app
# Place in: app/src/main/assets/llama-main
```

### Step 2: Install Delta CLI

#### Option A: Termux

```bash
# Install Termux from F-Droid or Google Play
# Open Termux and run:

# Update packages
pkg update && pkg upgrade

# Install Python
pkg install python

# Install Delta CLI
pip install delta-cli

# Test installation
python -m delta.cli --help
```

#### Option B: Manual Integration

```java
// Java code to integrate Delta CLI
public class DeltaCLIManager {
    private String deltaPath;
    
    public DeltaCLIManager(Context context) {
        // Path to Delta CLI in app bundle
        this.deltaPath = context.getFilesDir().getAbsolutePath() + "/delta-cli";
    }
    
    public List<String> listModels() {
        // Implementation for listing models
        return new ArrayList<>();
    }
    
    public boolean pullModel(String modelName) {
        // Implementation for downloading models
        return true;
    }
    
    public String runModel(String modelName, String prompt) {
        // Implementation for running models
        return "";
    }
}
```

### Step 3: Test Installation

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

## 🚀 Alternative Methods

### Using Gradle

```gradle
// build.gradle
dependencies {
    implementation 'com.github.ggerganov:llama-cpp:1.0.0'
}
```

### Using Maven

```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.github.ggerganov</groupId>
    <artifactId>llama-cpp</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Using JitPack

```gradle
// build.gradle
allprojects {
    repositories {
        maven { url 'https://jitpack.io' }
    }
}

dependencies {
    implementation 'com.github.ggerganov:llama-cpp:1.0.0'
}
```

---

## 🔧 Troubleshooting

### Issue: Python not found

**Solution**: Install Python via Termux

```bash
# Install Termux
# Download from F-Droid or Google Play

# Install Python
pkg install python
```

### Issue: Android Studio not found

**Solution**: Install Android Studio

```bash
# Download Android Studio from developer.android.com
# Or use Android Studio Canary
```

### Issue: Permission denied

**Solution**: Fix permissions

```bash
# Fix permissions in Android Studio
# Go to: app/src/main/AndroidManifest.xml
# Add: <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

### Issue: Build failed

**Solution**: Check dependencies

```bash
# Check Android SDK version
# Minimum: API level 24 (Android 7.0)

# Check Gradle version
# Minimum: Gradle 6.0
```

---

## 📋 System Requirements

- **OS**: Android 7.0 (API level 24) or later
- **Python**: 3.8 or later (via Termux)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 1GB free space
- **Network**: Internet connection for model downloads

---

## 🎯 Quick Commands

```bash
# Install Delta CLI
pip install delta-cli

# Test installation
python -m delta.cli list

# Download model
python -m delta.cli pull qwen2:0.5b

# Start chatting
python -m delta.cli run qwen2:0.5b
```

---

## ✅ Success!

You now have Delta CLI working on Android! The pre-built llama.cpp approach eliminates build issues and provides a smooth installation experience.

For more information, see:
- [Universal Installation Guide](UNIVERSAL_INSTALLATION_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
