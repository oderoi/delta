# 🍎 macOS Installation Guide

## ✅ Quick Start

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

---

## 🔧 Detailed Installation

### Prerequisites

- macOS 10.15 or later
- Python 3.8+
- Xcode Command Line Tools
- Homebrew (recommended)

### Step 1: Install Pre-built llama.cpp

```bash
# Install via Homebrew (recommended)
brew install llama.cpp

# Verify installation
llama-main --version
```

### Step 2: Install Delta CLI

```bash
# Clone repository
git clone https://github.com/your-repo/delta.git
cd delta

# Install Delta CLI
python -m pip install -e .
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

### Manual Installation

If package managers don't work:

```bash
# 1. Download pre-built llama.cpp
# Go to: https://github.com/ggerganov/llama.cpp/releases
# Download: llama-main-macos.zip

# 2. Extract to Delta directory
# Extract to: ~/.delta/bin/
# Rename to: llama-main

# 3. Make executable
chmod +x ~/.delta/bin/llama-main

# 4. Install Delta CLI
python -m pip install -e .
```

### Using MacPorts

```bash
# Install MacPorts (if not already installed)
# Download from: https://www.macports.org/install.php

# Install llama.cpp
sudo port install llama.cpp

# Install Delta CLI
python -m pip install -e .
```

### Using Nix

```bash
# Install Nix (if not already installed)
# Run: curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install

# Install llama.cpp
nix profile install nixpkgs#llama-cpp

# Install Delta CLI
python -m pip install -e .
```

---

## 🔧 Troubleshooting

### Issue: Homebrew not found

**Solution**: Install Homebrew

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH (if needed)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

### Issue: Xcode Command Line Tools missing

**Solution**: Install Xcode Command Line Tools

```bash
# Install Xcode Command Line Tools
xcode-select --install
```

### Issue: Python not found

**Solution**: Install Python

```bash
# Install Python via Homebrew
brew install python

# Or download from python.org
```

### Issue: Permission denied

**Solution**: Fix permissions

```bash
# Fix permissions
sudo chown -R $USER:$USER ~/.delta
chmod +x ~/.delta/bin/llama-main
```

---

## 📋 System Requirements

- **OS**: macOS 10.15 or later
- **Python**: 3.8 or later
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for model downloads

---

## 🎯 Quick Commands

```bash
# Install everything
brew install llama.cpp
python -m pip install -e .

# Test installation
python -m delta.cli list

# Download model
python -m delta.cli pull qwen2:0.5b

# Start chatting
python -m delta.cli run qwen2:0.5b
```

---

## ✅ Success!

You now have Delta CLI working on macOS! The pre-built llama.cpp approach eliminates build issues and provides a smooth installation experience.

For more information, see:
- [Universal Installation Guide](UNIVERSAL_INSTALLATION_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
