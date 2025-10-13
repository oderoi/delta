# Delta CLI

A lightweight, privacy-focused CLI for running local LLMs using llama.cpp. Delta is designed to run seamlessly on PCs, phones, and all edge devices with full llama.cpp capabilities.

## ✨ Features

- **Cross-platform support**: Windows, macOS, Linux, Android (Termux), iOS (a-Shell/iSH)
- **Automatic installation**: Pre-built binaries with fallback compilation
- **Full llama.cpp integration**: Server mode, embeddings, GPU acceleration, quantization
- **Easy model management**: Download, list, and manage GGUF models
- **Multiple chat formats**: ChatML, Llama3, and more
- **GPU acceleration**: CUDA, ROCm, Metal, OpenCL support
- **Streaming generation**: Real-time text generation
- **Model quantization**: Reduce model size with various quantization methods
- **Server mode**: Run models as HTTP servers
- **Embeddings**: Generate text embeddings
- **Benchmarking**: Performance testing tools

## 🚀 Quick Start

### Easy Installation (Recommended)

#### Windows:
```powershell
# See WINDOWS_INSTALL.md for complete Windows installation guide
# Quick start: .\install_delta_windows.bat
```

#### macOS/Linux:
```bash
# Install pre-built llama.cpp
brew install llama.cpp

# Install Delta CLI
python -m pip install -e .
```

#### iOS/Android:
```bash
# Download pre-built binaries manually
# See platform-specific guides for details
```

### Manual Installation

#### Windows:
```powershell
# See WINDOWS_INSTALL.md for complete Windows installation guide
# Quick start: .\install_delta_windows.bat
```

#### macOS:
```bash
# Install pre-built llama.cpp
brew install llama.cpp

# Install Delta CLI
python -m pip install -e .

# Test installation
python -m delta.cli list
python -m delta.cli pull qwen2:0.5b
python -m delta.cli run qwen2:0.5b
```

#### Linux:
```bash
# Install pre-built llama.cpp
brew install llama.cpp

# Install Delta CLI
python -m pip install -e .

# Test installation
python -m delta.cli list
python -m delta.cli pull qwen2:0.5b
python -m delta.cli run qwen2:0.5b
```


### Platform-Specific Guides

- **[Windows Installation](WINDOWS_INSTALL.md)** - Complete Windows setup
- **[macOS Installation](MACOS_INSTALL.md)** - Complete macOS setup
- **[Linux Installation](LINUX_INSTALL.md)** - Complete Linux setup
- **[iOS Installation](IOS_INSTALL.md)** - Complete iOS setup
- **[Android Installation](ANDROID_INSTALL.md)** - Complete Android setup
- **[Universal Guide](UNIVERSAL_INSTALLATION_GUIDE.md)** - Cross-platform installation
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

## 📖 Usage

### Basic Commands

```bash
# Download a model
delta pull qwen2:0.5b

# List available models
delta list

# Start interactive chat
delta run qwen2:0.5b

# Generate text from prompt
delta generate qwen2:0.5b "Explain quantum computing"

# Start server mode
delta server qwen2:0.5b --port 8080

# Get embeddings
delta embeddings qwen2:0.5b "Hello world"

# Benchmark model
delta benchmark qwen2:0.5b

# Get model info
delta info qwen2:0.5b

# Quantize model
delta quantize input_model output_model --quantization Q4_K_M

# System diagnostics
delta doctor
```

### Advanced Features

#### GPU Acceleration

```bash
# Use CUDA (NVIDIA)
delta run qwen2:0.5b --gpu-layers 20 --gpu-backend cuda

# Use Metal (Apple Silicon)
delta run qwen2:0.5b --gpu-layers 20 --gpu-backend metal

# Use ROCm (AMD)
delta run qwen2:0.5b --gpu-layers 20 --gpu-backend rocm
```

#### Streaming Generation

```bash
# Stream output as it generates
delta generate qwen2:0.5b "Write a story" --stream
```

#### Server Mode

```bash
# Start HTTP server
delta server qwen2:0.5b --host 0.0.0.0 --port 8080

# Access via HTTP API
curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "n_predict": 100}'
```

#### Model Quantization

```bash
# Quantize to Q4_K_M (recommended)
delta quantize input_model.q4_k_m output_model.q4_0 --quantization Q4_0

# Available quantizations: Q4_0, Q4_1, Q4_K_M, Q4_K_S, Q5_0, Q5_1, Q5_K_M, Q5_K_S, Q6_K, Q8_0, F16, F32
```

## 🔧 Configuration

Delta stores configuration in `~/.delta/config.json`:

```json
{
  "platform": {
    "system": "Darwin",
    "architecture": "arm64",
    "gpu_support": {
      "cuda": false,
      "rocm": false,
      "metal": true,
      "opencl": false
    }
  },
  "binary_path": "/Users/user/.delta/bin/llama-main",
  "models_dir": "/Users/user/.delta/models"
}
```

## 📦 Available Models

Delta supports all GGUF format models. Popular options:

- **qwen2:0.5b** - 0.5B parameters, great for mobile
- **qwen2:1.5b** - 1.5B parameters, balanced performance
- **qwen2:3b** - 3B parameters, high quality
- **llama3.1:8b** - 8B parameters, excellent quality
- **gemma2:2b** - 2B parameters, Google's model
- **phi3** - 3.8B parameters, Microsoft's model

## 🛠️ Troubleshooting

### Common Issues

1. **Binary not found**: Run `delta setup` to install llama.cpp
2. **Permission denied**: Ensure binary is executable (`chmod +x ~/.delta/bin/llama-main`)
3. **Out of memory**: Use smaller models or reduce context size
4. **GPU not detected**: Check GPU drivers and run `delta doctor`
5. **Installation fails**: See [Troubleshooting Guide](TROUBLESHOOTING.md) for solutions

### Installation Validation

Test your installation with:
```bash
# Test basic functionality
python -m delta.cli --help

# Test model listing
python -m delta.cli list

# Test model download
python -m delta.cli pull qwen2:0.5b
```

This will verify:
- ✅ Delta CLI functionality
- ✅ Model management
- ✅ llama.cpp binary
- ✅ Platform compatibility

### System Requirements

- **Minimum**: 2GB RAM, 1GB storage
- **Recommended**: 8GB RAM, 5GB storage
- **GPU**: Optional, but significantly faster

### Performance Tips

- Use quantized models (Q4_K_M) for better performance
- Enable GPU acceleration when available
- Use smaller models on mobile devices
- Adjust thread count based on CPU cores

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - The amazing C++ implementation
- [Hugging Face](https://huggingface.co/) - Model hosting and distribution
- All the open-source contributors who make this possible