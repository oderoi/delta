# Delta Installation Guide for Windows 🪟

This comprehensive guide will help you install Delta CLI on Windows with multiple installation methods and troubleshooting steps.

## 🚀 Quick Installation (Recommended)

### Method 1: One-Command Install
```cmd
# Open Command Prompt or PowerShell as Administrator
pip install delta && delta setup
```

### Method 2: Step-by-Step Install
```cmd
# 1. Install Delta
pip install delta

# 2. Setup environment
delta setup

# 3. Download a model
delta pull qwen2:0.5b

# 4. Start chatting
delta run qwen2:0.5b
```

## 📋 Prerequisites

### Required Software
- **Python 3.8+** (Download from [python.org](https://www.python.org/downloads/))
- **Git** (Download from [git-scm.com](https://git-scm.com/download/win))
- **Visual Studio Build Tools** (For compiling llama.cpp)

### System Requirements
- **Windows 10/11** (64-bit recommended)
- **4GB RAM** minimum (8GB+ recommended)
- **2GB free disk space** (more for larger models)
- **Internet connection** (for downloading models)

## 🔧 Installation Methods

### Method 1: Using pip (Recommended)

#### Step 1: Install Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation:
```cmd
python --version
pip --version
```

#### Step 2: Install Delta
```cmd
# Install Delta
pip install delta

# Setup environment
delta setup
```

### Method 2: Using winget (Windows Package Manager)

#### Step 1: Install Python
```cmd
# Install Python 3.11
winget install Python.Python.3.11

# Verify installation
python --version
```

#### Step 2: Install Delta
```cmd
# Install Delta
pip install delta

# Setup environment
delta setup
```

### Method 3: Using Chocolatey

#### Step 1: Install Chocolatey
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### Step 2: Install Python and Delta
```cmd
# Install Python
choco install python

# Install Delta
pip install delta
delta setup
```

### Method 4: Using Anaconda/Miniconda

#### Step 1: Install Anaconda
1. Download from [anaconda.com](https://www.anaconda.com/download)
2. Install with default settings

#### Step 2: Install Delta
```cmd
# Create virtual environment (optional)
conda create -n delta python=3.11
conda activate delta

# Install Delta
pip install delta
delta setup
```

## 🛠️ Build Tools Setup (For Compilation)

### Visual Studio Build Tools
```cmd
# Install Visual Studio Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools

# Or download from:
# https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
```

### Alternative: Visual Studio Community
1. Download Visual Studio Community (free)
2. During installation, select "Desktop development with C++"
3. This includes all necessary build tools

## 🚨 Troubleshooting Common Issues

### Issue 1: "delta: command not found"

#### Solution A: Use Python Module Method
```cmd
# Instead of: delta setup
python -m delta.cli setup

# Instead of: delta run model
python -m delta.cli run qwen2:0.5b
```

#### Solution B: Fix PATH
```cmd
# Find Python Scripts directory
python -c "import site; print(site.getusersitepackages())"

# Add to PATH (replace with your path)
setx PATH "%PATH%;C:\Users\YourUsername\AppData\Roaming\Python\Python311\Scripts"
```

#### Solution C: Reinstall with User Flag
```cmd
# Uninstall
pip uninstall delta

# Reinstall with user flag
pip install --user delta

# Add to PATH
setx PATH "%PATH%;%USERPROFILE%\AppData\Roaming\Python\Python311\Scripts"
```

### Issue 2: "Microsoft Visual C++ 14.0 is required"

#### Solution: Install Build Tools
```cmd
# Install Visual Studio Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools

# Or install Visual Studio Community
winget install Microsoft.VisualStudio.2022.Community
```

### Issue 3: "Permission denied" or "Access denied"

#### Solution A: Run as Administrator
1. Right-click Command Prompt
2. Select "Run as administrator"
3. Try installation again

#### Solution B: Use User Installation
```cmd
# Install for current user only
pip install --user delta
```

### Issue 4: Antivirus Blocking Installation

#### Solution: Add Exclusions
1. Open Windows Security
2. Go to "Virus & threat protection"
3. Click "Manage settings" under "Virus & threat protection settings"
4. Add exclusions for:
   - `%USERPROFILE%\.delta`
   - `%USERPROFILE%\AppData\Local\Temp`

### Issue 5: Network/Proxy Issues

#### Solution A: Use Different Index
```cmd
pip install -i https://pypi.org/simple/ delta
```

#### Solution B: Configure Proxy
```cmd
pip install --proxy http://proxy:port delta
```

#### Solution C: Use Trusted Hosts
```cmd
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org delta
```

### Issue 6: Python Not Found

#### Solution: Reinstall Python
1. Download Python from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH"
3. Restart Command Prompt
4. Verify: `python --version`

## 🔍 Verification Steps

### Step 1: Test Installation
```cmd
# Check if Delta is installed
python -m delta.cli --version

# Check system status
python -m delta.cli doctor
```

### Step 2: Test Basic Functionality
```cmd
# List available models
python -m delta.cli list

# Download a small model
python -m delta.cli pull qwen2:0.5b

# Start chatting
python -m delta.cli run qwen2:0.5b
```

### Step 3: Performance Test
```cmd
# Benchmark performance
python -m delta.cli benchmark qwen2:0.5b

# Test generation
python -m delta.cli generate qwen2:0.5b "Hello world"
```

## 🎯 Quick Start After Installation

### 1. Download Your First Model
```cmd
# Small model (0.5B parameters, ~0.3GB)
python -m delta.cli pull qwen2:0.5b

# Medium model (1.5B parameters, ~0.9GB)
python -m delta.cli pull qwen3:1.7b

# Large model (3B parameters, ~1.8GB)
python -m delta.cli pull llama3.2:3b
```

### 2. Start Chatting
```cmd
# Interactive chat
python -m delta.cli run qwen2:0.5b

# One-time generation
python -m delta.cli generate qwen2:0.5b "Write a short story about a robot"
```

### 3. Explore Features
```cmd
# List installed models
python -m delta.cli list

# Check system status
python -m delta.cli doctor

# Get help
python -m delta.cli --help
```

## 🔧 Advanced Configuration

### GPU Acceleration (NVIDIA)
```cmd
# Install CUDA toolkit
winget install Nvidia.CUDA

# Install Delta with GPU support
pip install delta[gpu]
python -m delta.cli setup
```

### Custom Installation Directory
```cmd
# Set custom data directory
set DELTA_DATA_DIR=C:\MyDeltaData
python -m delta.cli setup
```

### Virtual Environment
```cmd
# Create virtual environment
python -m venv delta-env

# Activate
delta-env\Scripts\activate

# Install Delta
pip install delta
python -m delta.cli setup
```

## 📱 Mobile Installation (Windows Subsystem for Android)

If you have WSA (Windows Subsystem for Android):

### Install Termux
1. Install Termux from F-Droid (not Play Store)
2. Open Termux
3. Follow Android installation guide:

```bash
# Update packages
pkg update && pkg upgrade

# Install dependencies
pkg install python git cmake clang

# Install Delta
pip install delta
delta setup
```

## 🆘 Getting Help

### If Installation Fails
1. **Check Python version**: `python --version` (should be 3.8+)
2. **Check pip**: `pip --version`
3. **Run as Administrator**: Right-click Command Prompt → "Run as administrator"
4. **Check antivirus**: Add exclusions for Delta directories
5. **Check network**: Try different pip index or proxy settings

### If Models Don't Download
1. **Check internet connection**
2. **Check disk space**: Need at least 2GB free
3. **Check permissions**: Run as Administrator
4. **Try different model**: Start with smaller models

### If Chat Doesn't Work
1. **Check model installation**: `python -m delta.cli list`
2. **Check binary**: `python -m delta.cli doctor`
3. **Reinstall**: `python -m delta.cli setup`
4. **Check logs**: Look for error messages

## 📝 Uninstallation

### Remove Delta
```cmd
# Uninstall Delta
pip uninstall delta

# Remove data directory
rmdir /s "%USERPROFILE%\.delta"

# Remove from PATH (if added manually)
# Edit System Environment Variables
```

### Clean Up
```cmd
# Remove Python cache
pip cache purge

# Remove temporary files
del /q "%TEMP%\delta*"
```

## 🎉 Success!

Once installation is complete, you can:

1. **Download models**: `python -m delta.cli pull model-name`
2. **Start chatting**: `python -m delta.cli run model-name`
3. **Explore features**: `python -m delta.cli --help`
4. **Check status**: `python -m delta.cli doctor`

Enjoy using Delta CLI on Windows! 🚀
