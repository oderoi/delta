# 🪟 Windows Installation & Usage Guide

## 🚀 Quick Installation

### Method 1: Automated Installer (Recommended)
```powershell
# Complete automated installation
.\install_delta_windows.bat
```

### Method 2: Python Installer
```powershell
# Run Python installer directly
python WINDOWS_COMPLETE_INSTALL.py
```

### Method 3: Manual Installation
```powershell
# Install pre-built llama.cpp
winget install llama.cpp

# Install Delta CLI
python -m pip install -e .

# Test installation
python -m delta.cli list
python -m delta.cli pull qwen2:0.5b
python -m delta.cli run qwen2:0.5b
```

---

## 📋 Prerequisites

### System Requirements
- **Windows**: 10 or later
- **Python**: 3.8 or later
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space minimum
- **Internet**: Required for model downloads

### Required Software
1. **Python 3.8+**
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **Git** (for development)
   - Download from: https://git-scm.com/download/win
   - Or install via: `winget install Git.Git`

3. **Build Tools** (if building from source)
   - Visual Studio Build Tools
   - Or install via: `winget install Microsoft.VisualStudio.2022.BuildTools`

---

## 🔧 Installation Methods

### Method 1: Automated Installer (Easiest)

1. **Download the installer**:
   ```powershell
   # The installer is already in your project directory
   .\install_delta_windows.bat
   ```

2. **Follow the prompts**:
   - The installer will check your system
   - Install dependencies automatically
   - Set up Delta CLI
   - Download llama.cpp binary

3. **Test installation**:
   ```powershell
   python -m delta.cli list
   ```

### Method 2: Python Installer

1. **Run the Python installer**:
   ```powershell
   python WINDOWS_COMPLETE_INSTALL.py
   ```

2. **The installer will**:
   - Check system requirements
   - Clean existing packages
   - Install dependencies
   - Set up Delta CLI
   - Download llama.cpp binary
   - Test functionality

### Method 3: Manual Installation

1. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

2. **Install Delta CLI**:
   ```powershell
   python -m pip install -e .
   ```

3. **Install llama.cpp**:
   ```powershell
   # Option A: Use winget (recommended)
   winget install llama.cpp
   
   # Option B: Download manually
   # Go to: https://github.com/ggerganov/llama.cpp/releases
   # Download: llama-main-win64.zip
   # Extract to: %USERPROFILE%\.delta\bin\
   # Rename to: llama-main.exe
   ```

4. **Test installation**:
   ```powershell
   # Test with short commands (recommended)
   delta --help
   delta list
   
   # Alternative (also works)
   python -m delta.cli --help
   python -m delta.cli list
   ```

---

## 🎯 Usage Guide

### 1. List Available Models
```powershell
# Short command (recommended)
delta list

# Alternative (also works)
python -m delta.cli list

# Output shows:
# - Installed models
# - Available models to download
```

### 2. Download Models
```powershell
# Download small models (recommended for testing)
delta pull qwen2:0.5b
delta pull tinyllama
delta pull qwen3:0.6b

# Download larger models (if you have enough RAM)
delta pull llama3.1:8b
delta pull mistral
delta pull phi3
```

### 3. Run Models (Interactive Chat)
```powershell
# Start interactive chat
delta run qwen2:0.5b
delta run tinyllama
delta run qwen3:0.6b

# Chat interface will start
# Type your messages and press Enter
# Type 'exit' to terminate Delta and return to command prompt
# Use Ctrl+C to force exit if needed
```

### 4. Generate Text from Prompts
```powershell
# Generate text from a prompt
delta generate qwen2:0.5b "Explain quantum computing"
delta generate tinyllama "Write a short story about a robot"
```

### 5. Start Chat Server
```powershell
# Start a web server for API access
delta server qwen2:0.5b --port 8080

# Server will be available at http://localhost:8080
# Press Ctrl+C to stop the server

# Test the server with curl:
curl http://localhost:8080/v1/models
```

### 6. Other Commands
```powershell
# Get help
delta --help

# Check version
delta version

# System diagnostics
delta doctor

# Get model information
delta info qwen2:0.5b

# Benchmark model performance
delta benchmark qwen2:0.5b

# Get embeddings
delta embeddings qwen2:0.5b "Hello world"

# Quantize model
delta quantize input_model output_model --quantization Q4_K_M
```

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### Issue 1: `[WinError 216] This version of %1 is not compatible`

**Cause**: The llama.cpp binary is not compatible with your Windows version.

**Solution**:
1. Go to: https://github.com/ggerganov/llama.cpp/releases
2. Download: `llama-main-win64.zip`
3. Extract to: `%USERPROFILE%\.delta\bin\`
4. Rename to: `llama-main.exe`
5. Try again: `python -m delta.cli run qwen2:0.5b`

#### Issue 2: `python: command not found`

**Cause**: Python is not installed or not in PATH.

**Solution**:
1. Install Python from: https://www.python.org/downloads/
2. Make sure to check "Add Python to PATH" during installation
3. Restart your terminal
4. Test: `python --version`

#### Issue 3: `Permission denied` or `Access is denied`

**Cause**: Insufficient permissions.

**Solution**:
1. Run PowerShell as Administrator
2. Right-click PowerShell → "Run as administrator"
3. Try the installation again

#### Issue 4: Model download fails

**Cause**: Network issues or model not found.

**Solution**:
1. Check internet connection
2. Try a different model: `python -m delta.cli pull tinyllama`
3. Check available models: `python -m delta.cli list`

#### Issue 5: Installation fails

**Cause**: Missing dependencies or system issues.

**Solution**:
1. Run as Administrator
2. Check Python version: `python --version`
3. Reinstall: `python WINDOWS_COMPLETE_INSTALL.py`
4. Check system requirements

#### Issue 6: Unicode errors

**Cause**: Windows console encoding issues.

**Solution**:
1. Set environment variable: `set PYTHONIOENCODING=utf-8`
2. Use the automated installer: `.\install_delta_windows.bat`
3. The installer handles Unicode issues automatically

---

## 🔍 Verification

### Test Your Installation

1. **Test basic functionality**:
   ```powershell
   delta --help
   ```

2. **Test model listing**:
   ```powershell
   delta list
   ```

3. **Test model download**:
   ```powershell
   delta pull qwen2:0.5b
   ```

4. **Test model running**:
   ```powershell
   delta run qwen2:0.5b
   ```

### Success Checklist

- [ ] Python 3.8+ installed
- [ ] Delta CLI installed
- [ ] `delta --help` works
- [ ] `delta list` works
- [ ] Model download works
- [ ] Model running works

---

## 🚀 Advanced Usage

### Chat Session Management

```powershell
# Start a chat session
delta run qwen2:0.5b

# During the chat session:
# - Type your messages and press Enter
# - Type 'exit' to terminate Delta and return to command prompt
# - Use Ctrl+C to force exit if needed

# Example chat session:
# > Hello, how are you?
# [Model responds...]
# > exit
# Exiting chat session...
# [Returns to command prompt]
```

### GPU Acceleration

```powershell
# Use CUDA (NVIDIA GPU)
python -m delta.cli run qwen2:0.5b --gpu-layers 20 --gpu-backend cuda

# Use OpenCL (AMD/Intel GPU)
python -m delta.cli run qwen2:0.5b --gpu-layers 20 --gpu-backend opencl
```

### Server Mode

```powershell
# Start HTTP server
python -m delta.cli server qwen2:0.5b --host 0.0.0.0 --port 8080

# Access via HTTP API
curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "n_predict": 100}'
```

### Model Quantization

```powershell
# Quantize model to reduce size
python -m delta.cli quantize input_model.q4_k_m output_model.q4_0 --quantization Q4_0

# Available quantizations: Q4_0, Q4_1, Q4_K_M, Q4_K_S, Q5_0, Q5_1, Q5_K_M, Q5_K_S, Q6_K, Q8_0, F16, F32
```

---

## 📊 Performance Tips

### For Better Performance

1. **Use quantized models**: Q4_K_M is recommended for good quality/size balance
2. **Enable GPU acceleration**: If you have a compatible GPU
3. **Use smaller models**: For faster response times
4. **Adjust thread count**: Based on your CPU cores

### Model Size Recommendations

- **0.5B-1.5B models**: Good for testing and mobile devices
- **3B-7B models**: Good balance of quality and performance
- **8B+ models**: High quality but require more RAM

---

## 🆘 Getting Help

### If You Need Help

1. **Check system**: `python -m delta.cli doctor`
2. **Read logs**: Check error messages carefully
3. **Try quick fixes**: See troubleshooting section above
4. **Report issues**: Create an issue on GitHub with:
   - Windows version
   - Python version
   - Error message
   - Steps to reproduce

### Community Support

- **GitHub Issues**: Report bugs and get help
- **GitHub Discussions**: Ask questions and share tips
- **Documentation**: Check other platform guides

---

## 🎉 Success!

If you've followed this guide, you should now have:

✅ **Delta CLI installed and working**  
✅ **Models downloading and running**  
✅ **Interactive chat working**  
✅ **All commands functional**  

**Welcome to Delta CLI on Windows!** 🚀

---

## 📚 Next Steps

1. **Explore models**: Try different models to find your favorite
2. **Learn commands**: Use `python -m delta.cli --help` to see all options
3. **Join community**: Share your experience and get help
4. **Contribute**: Help improve Delta CLI for everyone

**Happy chatting with your local AI!** 🤖
