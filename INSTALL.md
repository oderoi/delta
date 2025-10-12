# Delta Installation Guide

This guide provides comprehensive installation instructions for Delta CLI across all platforms.

## 🚀 Quick Installation

### One-Command Install (Recommended)

```bash
# Install and setup everything automatically
pip install delta && delta setup
```

### Manual Installation

```bash
# 1. Install Delta
pip install delta

# 2. Setup environment
delta setup

# 3. Download a model
delta pull qwen2:0.5b

# 4. Start chatting
delta run qwen2:0.5b
```

## 📱 Platform-Specific Instructions

### Windows

#### Option 1: Using pip (Recommended)
```cmd
# Install Python 3.8+ from python.org
pip install delta
delta setup
```

#### Option 2: Using winget
```cmd
# Install Python
winget install Python.Python.3.11

# Install Delta
pip install delta
delta setup
```

#### Option 3: Using Chocolatey
```cmd
# Install Python
choco install python

# Install Delta
pip install delta
delta setup
```

### macOS

#### Option 1: Using Homebrew (Recommended)
```bash
# Install Python
brew install python

# Install Delta
pip install delta
delta setup
```

#### Option 2: Using MacPorts
```bash
# Install Python
sudo port install python311

# Install Delta
pip install delta
delta setup
```

#### Option 3: Using pyenv
```bash
# Install pyenv
brew install pyenv

# Install Python
pyenv install 3.11.0
pyenv global 3.11.0

# Install Delta
pip install delta
delta setup
```

### Linux

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git cmake build-essential

# Install Delta
pip install delta
delta setup
```

#### CentOS/RHEL/Fedora
```bash
# Install Python and dependencies
sudo yum install python3 python3-pip git cmake gcc gcc-c++ make
# or for newer versions:
sudo dnf install python3 python3-pip git cmake gcc gcc-c++ make

# Install Delta
pip install delta
delta setup
```

#### Arch Linux
```bash
# Install Python and dependencies
sudo pacman -S python python-pip git cmake base-devel

# Install Delta
pip install delta
delta setup
```

#### openSUSE
```bash
# Install Python and dependencies
sudo zypper install python3 python3-pip git cmake gcc gcc-c++ make

# Install Delta
pip install delta
delta setup
```

### Android (Termux)

```bash
# Install Termux from F-Droid (not Play Store)
# Update packages
pkg update && pkg upgrade

# Install Python and dependencies
pkg install python git cmake clang

# Install Delta
pip install delta
delta setup
```

### iOS (a-Shell/iSH)

#### iSH
```bash
# Install dependencies
apk add python3 py3-pip git cmake make clang

# Install Delta
pip3 install delta
delta setup
```

#### a-Shell
```bash
# Install dependencies
pkg install python git cmake make clang

# Install Delta
pip install delta
delta setup
```

## 🔧 Advanced Installation

### Development Installation

```bash
# Clone repository
git clone https://github.com/oderoi/delta.git
cd delta

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python test_installation.py
```

### GPU Acceleration Setup

#### NVIDIA CUDA
```bash
# Install CUDA toolkit
# Ubuntu/Debian:
sudo apt install nvidia-cuda-toolkit

# Install Delta with GPU support
pip install delta[gpu]
delta setup
```

#### AMD ROCm
```bash
# Install ROCm
# Ubuntu:
sudo apt install rocm-dev

# Install Delta
pip install delta
delta setup
```

#### Apple Metal (macOS)
```bash
# Metal is automatically detected on macOS
pip install delta
delta setup
```

### Docker Installation

```bash
# Pull Delta Docker image
docker pull oderoi/delta:latest

# Run Delta
docker run -it --rm oderoi/delta:latest delta --help
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Python Version Issues
```bash
# Check Python version
python --version

# If Python < 3.8, upgrade:
# Ubuntu/Debian:
sudo apt install python3.11

# macOS:
brew install python@3.11

# Windows: Download from python.org
```

#### 2. Permission Issues
```bash
# Install with user flag
pip install --user delta

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

#### 3. Build Tools Missing
```bash
# Ubuntu/Debian:
sudo apt install build-essential cmake git

# CentOS/RHEL:
sudo yum groupinstall "Development Tools"
sudo yum install cmake git

# macOS:
xcode-select --install
```

#### 4. Network Issues
```bash
# Use different index
pip install -i https://pypi.org/simple/ delta

# Use proxy
pip install --proxy http://proxy:port delta
```

#### 5. Binary Not Found
```bash
# Reinstall llama.cpp
delta setup

# Check PATH
echo $PATH

# Add to PATH manually
export PATH="$HOME/.delta/bin:$PATH"
```

### Platform-Specific Issues

#### Windows
- **Antivirus blocking**: Add `~/.delta` to exclusions
- **PATH not updated**: Restart terminal or use `setx`
- **Build tools missing**: Install Visual Studio Build Tools

#### macOS
- **Xcode Command Line Tools**: Run `xcode-select --install`
- **Homebrew issues**: Update with `brew update && brew upgrade`
- **Permission denied**: Use `sudo` or fix permissions

#### Linux
- **Package manager issues**: Update package lists first
- **Missing dependencies**: Install build-essential
- **Permission issues**: Use `sudo` or `--user` flag

#### Mobile
- **Termux**: Install from F-Droid, not Play Store
- **Storage issues**: Use external storage
- **Performance**: Use smaller models (0.5B-1.5B)

## 🔍 Verification

### Test Installation
```bash
# Run comprehensive test
python test_installation.py

# Check system
delta doctor

# Test basic functionality
delta --help
delta version
delta list
```

### Performance Test
```bash
# Download a small model
delta pull qwen2:0.5b

# Benchmark performance
delta benchmark qwen2:0.5b

# Test generation
delta generate qwen2:0.5b "Hello world"
```

## 📚 Next Steps

After successful installation:

1. **Download a model**: `delta pull qwen2:0.5b`
2. **Start chatting**: `delta run qwen2:0.5b`
3. **Explore features**: `delta --help`
4. **Check system**: `delta doctor`
5. **Read documentation**: Check README.md

## 🆘 Getting Help

If you encounter issues:

1. **Check system**: `delta doctor`
2. **Read logs**: Check error messages
3. **Search issues**: GitHub Issues
4. **Ask community**: GitHub Discussions
5. **Report bugs**: Create an issue

## 📝 Uninstallation

```bash
# Remove Delta
pip uninstall delta

# Remove data directory
rm -rf ~/.delta

# Remove from PATH (if added manually)
# Edit ~/.bashrc, ~/.zshrc, or system PATH
```
