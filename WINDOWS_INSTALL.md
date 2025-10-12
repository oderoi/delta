# Delta CLI - Windows Installation

## 🚀 Simple Installation

**This is the ONLY working method for Windows:**

### Option 1: Automated Installation (Recommended)

**Run the batch file:**
```cmd
install_delta_windows.bat
```

**Or run the PowerShell script:**
```powershell
.\install_delta_windows.ps1
```

### Option 2: Manual Installation

```cmd
# 1. Remove conflicting packages
pip uninstall delta delta-0.4.2 delta-cli delta-ai -y

# 2. Install dependencies
pip install requests>=2.31.0 click>=8.1.0 tabulate>=0.9.0 colorama>=0.4.6 huggingface_hub>=0.20.0 tqdm>=4.66.0 psutil>=5.9.0

# 3. Install Delta
python final_windows_install.py
```

## 📋 Usage

After installation, use Delta CLI like this:

```cmd
# List available models
python -m delta.cli list

# Download a model (requires build tools)
python -m delta.cli pull qwen2:0.5b

# Start chatting
python -m delta.cli run qwen2:0.5b

# Get help
python -m delta.cli --help
```

## 🔧 Optional: Build Tools for Model Downloading

If you want to download models, install these:

```cmd
# Install build tools
winget install Kitware.CMake
winget install Git.Git
winget install Microsoft.VisualStudio.2022.BuildTools
winget install curl.curl

# Add CMake to PATH
$env:PATH += ";C:\Program Files\CMake\bin"
```

## 🆘 Troubleshooting

### "delta: command not found"
**Solution**: Always use `python -m delta.cli [command]`

### "Permission denied" during model download
**Solution**: Run as Administrator or use pre-built binary

### "Cannot build llama.cpp"
**Solution**: Download pre-built binary from GitHub releases

## ✅ Success!

Once installed, you can:
- Download and run local LLMs
- Use GPU acceleration (if available)
- Run models as servers
- Generate embeddings and more

**That's it! Delta CLI is ready to use on Windows.** 🎉
