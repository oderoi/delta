# Delta CLI - Windows Installation

## 🚀 Quick Start

**For Windows users, use this simple installation method:**

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

# Download a model
python -m delta.cli pull qwen2:0.5b

# Start chatting
python -m delta.cli run qwen2:0.5b

# Get help
python -m delta.cli --help
```

## 🆘 Troubleshooting

### "delta: command not found"
**Solution**: Always use `python -m delta.cli [command]`

### "Permission denied" during model download
**Solution**: Run as Administrator or use pre-built binary

### "Cannot build llama.cpp"
**Solution**: Download pre-built binary from GitHub releases

## 📚 More Information

- **Detailed Guide**: See `WINDOWS_INSTALLATION_GUIDE.md`
- **Complete Solution**: See `FINAL_WINDOWS_SOLUTION.md`

## ✅ Success!

Once installed, you can:
- Download and run local LLMs
- Use GPU acceleration (if available)
- Run models as servers
- Generate embeddings and more

**That's it! Delta CLI is ready to use on Windows.** 🎉
