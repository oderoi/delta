# 🔧 Troubleshooting Guide

## 🚨 Common Issues & Solutions

### Issue 1: CURL not found

**Error**: `Could NOT find CURL`

**Solutions**:
1. **Use pre-built binaries** (Recommended)
   ```bash
   # Windows
   winget install llama.cpp
   
   # macOS
   brew install llama.cpp
   
   # Linux
   brew install llama.cpp
   ```

2. **Install CURL manually**
   ```bash
   # Windows
   winget install curl.curl
   
   # macOS
   brew install curl
   
   # Linux
   sudo apt install curl
   ```

3. **Disable CURL in llama.cpp**
   ```bash
   # Add to CMake flags
   -DLLAMA_CURL=OFF
   ```

### Issue 2: Permission denied

**Error**: `PermissionError: [WinError 5] Access is denied`

**Solutions**:
1. **Run as Administrator** (Windows)
   ```powershell
   # Right-click PowerShell → "Run as administrator"
   python -m delta.cli pull qwen2:0.5b
   ```

2. **Fix permissions** (Linux/macOS)
   ```bash
   sudo chown -R $USER:$USER ~/.delta
   chmod +x ~/.delta/bin/llama-main
   ```

3. **Clean .delta directory**
   ```bash
   # Windows
   rmdir /s /q "%USERPROFILE%\.delta"
   
   # Linux/macOS
   rm -rf ~/.delta
   ```

### Issue 3: Build tools missing

**Error**: `Could NOT find CMAKE` or `Could NOT find CURL`

**Solutions**:
1. **Use pre-built binaries** (Recommended)
   ```bash
   # Windows
   winget install llama.cpp
   
   # macOS
   brew install llama.cpp
   
   # Linux
   brew install llama.cpp
   ```

2. **Install build tools**
   ```bash
   # Windows
   winget install Kitware.CMake
   winget install curl.curl
   
   # macOS
   brew install cmake curl
   
   # Linux
   sudo apt install cmake curl build-essential
   ```

### Issue 4: Python not found

**Error**: `python: command not found`

**Solutions**:
1. **Install Python**
   ```bash
   # Windows
   winget install Python.Python.3.11
   
   # macOS
   brew install python
   
   # Linux
   sudo apt install python3 python3-pip
   ```

2. **Add Python to PATH**
   ```bash
   # Windows
   # Add to PATH: C:\Users\username\AppData\Local\Programs\Python\Python311\
   
   # Linux/macOS
   echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Issue 5: Git not found

**Error**: `git: command not found`

**Solutions**:
1. **Install Git**
   ```bash
   # Windows
   winget install Git.Git
   
   # macOS
   brew install git
   
   # Linux
   sudo apt install git
   ```

2. **Configure Git**
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

### Issue 6: Network issues

**Error**: `RPC failed; curl 56` or `Connection was reset`

**Solutions**:
1. **Check internet connection**
   ```bash
   ping google.com
   ```

2. **Configure Git for large files**
   ```bash
   git config --global http.postBuffer 524288000
   git config --global http.maxRequestBuffer 100M
   ```

3. **Use shallow clone**
   ```bash
   git clone --depth 1 https://github.com/ggerganov/llama.cpp.git
   ```

### Issue 7: Unicode errors

**Error**: `UnicodeEncodeError: 'charmap' codec can't encode character`

**Solutions**:
1. **Set environment variables**
   ```bash
   # Windows
   set PYTHONIOENCODING=utf-8
   
   # Linux/macOS
   export PYTHONIOENCODING=utf-8
   ```

2. **Use pre-built binaries**
   ```bash
   # Avoid building from source
   winget install llama.cpp
   ```

### Issue 8: Model download fails

**Error**: `Failed to download model`

**Solutions**:
1. **Check internet connection**
   ```bash
   ping huggingface.co
   ```

2. **Use different model**
   ```bash
   python -m delta.cli pull qwen2:0.5b
   ```

3. **Clear cache**
   ```bash
   # Clear Delta cache
   rm -rf ~/.delta/cache
   ```

---

## 🛠️ Platform-Specific Solutions

### Windows

See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for complete Windows troubleshooting guide.

### macOS

#### Issue: Homebrew not found
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Issue: Xcode Command Line Tools
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

#### Issue: Permission denied
```bash
# Fix permissions
sudo chown -R $(whoami) /usr/local
```

### Linux

#### Issue: Package manager not found
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip git

# Fedora/RHEL
sudo dnf install python3 python3-pip git

# Arch Linux
sudo pacman -S python python-pip git
```

#### Issue: Permission denied
```bash
# Fix permissions
sudo chown -R $USER:$USER ~/.delta
chmod +x ~/.delta/bin/llama-main
```

---

## 🧪 Testing Solutions

### Test 1: Basic functionality
```bash
# Test Python
python --version

# Test pip
pip --version

# Test Git
git --version
```

### Test 2: Delta CLI
```bash
# Test Delta CLI
python -m delta.cli --help

# Test model listing
python -m delta.cli list
```

### Test 3: Model download
```bash
# Test model download
python -m delta.cli pull qwen2:0.5b

# Test model running
python -m delta.cli run qwen2:0.5b
```

---

## 📞 Getting Help

### 1. Check logs
```bash
# Enable verbose logging
python -m delta.cli --verbose pull qwen2:0.5b
```

### 2. Check system requirements
```bash
# Check Python version
python --version

# Check available memory
# Windows: wmic computersystem get TotalPhysicalMemory
# Linux/macOS: free -h
```

### 3. Report issues
- **GitHub Issues**: Create a new issue with:
  - Operating system and version
  - Python version
  - Error message
  - Steps to reproduce

### 4. Community support
- **Discord**: Join our Discord server
- **Reddit**: r/deltacli
- **Stack Overflow**: Tag questions with `delta-cli`

---

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Git installed and configured
- [ ] Pre-built llama.cpp installed
- [ ] Delta CLI installed
- [ ] `python -m delta.cli --help` works
- [ ] `python -m delta.cli list` works
- [ ] Model download works
- [ ] Model running works

---

## 🎯 Quick Fixes

### Windows
See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for complete Windows installation and troubleshooting.

### macOS
```bash
# Fix everything
brew install llama.cpp
python -m pip install -e .
python -m delta.cli list
```

### Linux
```bash
# Fix everything
brew install llama.cpp
python -m pip install -e .
python -m delta.cli list
```

---

## 🚀 Advanced Solutions

### Custom llama.cpp build
```bash
# If pre-built binaries don't work
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
mkdir build && cd build
cmake .. -DLLAMA_CURL=OFF
make -j$(nproc)
```

### Docker installation
```bash
# Use Docker for consistent environment
docker run -it --rm -v $(pwd):/workspace python:3.11 bash
cd /workspace
pip install -e .
```

### Virtual environment
```bash
# Use virtual environment for isolation
python -m venv delta-env
source delta-env/bin/activate  # Linux/macOS
# or
delta-env\Scripts\activate     # Windows
pip install -e .
```

---

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.15, Linux (Ubuntu 18.04+)
- **Python**: 3.8 or later
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Network**: Internet connection

### Recommended Requirements
- **OS**: Windows 11, macOS 12+, Linux (Ubuntu 20.04+)
- **Python**: 3.11 or later
- **RAM**: 8GB
- **Storage**: 5GB free space
- **Network**: Fast internet connection

---

## 🎉 Success!

If you've followed this guide and still have issues, please:

1. **Check the logs** for specific error messages
2. **Try the quick fixes** above
3. **Report the issue** with detailed information
4. **Join our community** for support

The pre-built llama.cpp approach should eliminate most build issues and provide a smooth installation experience across all platforms!
