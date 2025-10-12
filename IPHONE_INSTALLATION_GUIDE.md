# Delta Installation Guide for iPhone 📱

This guide covers installing Delta CLI on iPhone using terminal apps available on iOS.

## 📱 Required Apps

### Option 1: iSH (Recommended)
- **Download**: [iSH Shell](https://apps.apple.com/app/ish-shell/id1436902243) from App Store
- **Cost**: Free
- **Features**: Full Alpine Linux environment, package manager, Python support

### Option 2: a-Shell
- **Download**: [a-Shell](https://apps.apple.com/app/a-shell/id1473805438) from App Store  
- **Cost**: Free
- **Features**: Unix shell, Python support, file management

### Option 3: Termius
- **Download**: [Termius](https://apps.apple.com/app/termius-ssh-client/id549039908) from App Store
- **Cost**: Free with premium features
- **Features**: SSH client, can connect to remote servers

## 🚀 Installation Methods

### Method 1: iSH (Alpine Linux)

#### Step 1: Install iSH
1. Download iSH from App Store
2. Open iSH app

#### Step 2: Update System
```bash
# Update package list
apk update

# Install Python and dependencies
apk add python3 py3-pip git cmake make clang
```

#### Step 3: Install Delta
```bash
# Install Delta
pip3 install delta

# Setup Delta
python3 -m delta.cli setup
```

#### Step 4: Test Installation
```bash
# Test Delta
python3 -m delta.cli --help

# Download a small model
python3 -m delta.cli pull qwen2:0.5b

# Start chatting
python3 -m delta.cli run qwen2:0.5b
```

### Method 2: a-Shell

#### Step 1: Install a-Shell
1. Download a-Shell from App Store
2. Open a-Shell app

#### Step 2: Install Python
```bash
# Install Python (if not available)
pip3 install --user delta
```

#### Step 3: Install Delta
```bash
# Install Delta
python3 -m pip install delta

# Setup Delta
python3 -m delta.cli setup
```

### Method 3: Remote Server (Termius)

#### Step 1: Set up Remote Server
1. Get a VPS or cloud server (DigitalOcean, AWS, etc.)
2. Install Delta on the server following Linux instructions
3. Use Termius to SSH into the server

#### Step 2: Connect via Termius
```bash
# SSH into your server
ssh user@your-server-ip

# Use Delta remotely
delta run qwen2:0.5b
```

## 📋 iPhone-Specific Considerations

### Storage Limitations
- **iPhone Storage**: Models can be large (0.5GB - 8GB+)
- **Recommendation**: Use smaller models (0.5B - 1.5B parameters)
- **Best Models for iPhone**:
  - `qwen2:0.5b` (0.3 GB)
  - `qwen3:0.6b` (0.4 GB)
  - `llama3.2:1b` (0.8 GB)

### Performance
- **CPU Only**: No GPU acceleration on iPhone
- **Memory**: Limited RAM (4GB-8GB typical)
- **Speed**: Slower than desktop, but functional

### Network Requirements
- **WiFi Recommended**: Large model downloads
- **Data Usage**: Models can be 100MB-8GB+ to download

## 🛠️ Troubleshooting

### Common Issues

#### Issue 1: "Command not found: delta"
```bash
# Solution: Use Python module method
python3 -m delta.cli --help
python3 -m delta.cli run qwen2:0.5b
```

#### Issue 2: "No space left on device"
```bash
# Check storage
df -h

# Clean up if needed
rm -rf ~/.cache
```

#### Issue 3: "Permission denied"
```bash
# Install with user flag
pip3 install --user delta
```

#### Issue 4: "Python not found"
```bash
# Install Python in iSH
apk add python3 py3-pip

# Or use a-Shell which has Python built-in
```

### Performance Optimization

#### Use Smaller Models
```bash
# Best models for iPhone
delta pull qwen2:0.5b      # 0.3 GB
delta pull qwen3:0.6b      # 0.4 GB  
delta pull llama3.2:1b     # 0.8 GB
```

#### Reduce Context Size
```bash
# Use smaller context for better performance
delta run qwen2:0.5b --ctx-size 2048
```

## 📱 Usage Examples

### Basic Usage
```bash
# Download a model
python3 -m delta.cli pull qwen2:0.5b

# Start chatting
python3 -m delta.cli run qwen2:0.5b

# Generate text
python3 -m delta.cli generate qwen2:0.5b "Explain AI"
```

### Server Mode (Advanced)
```bash
# Start server
python3 -m delta.cli server qwen2:0.5b --port 8080

# Access via browser (if supported)
# http://localhost:8080
```

## 🔧 Advanced Setup

### Custom Installation Directory
```bash
# Set custom data directory
export DELTA_DATA_DIR=/tmp/delta
python3 -m delta.cli setup
```

### Background Processing
```bash
# Run in background (if supported)
nohup python3 -m delta.cli run qwen2:0.5b &
```

## 📚 Recommended Apps

### For Terminal Access
1. **iSH** - Best for full Linux environment
2. **a-Shell** - Good for basic Python usage
3. **Termius** - For remote server access

### For File Management
1. **Files** - Built-in iOS file manager
2. **Documents by Readdle** - Advanced file management

## ⚠️ Limitations

### iOS Restrictions
- **No Background Processing**: Apps may close when switching
- **Limited Storage**: iPhone storage is limited
- **No GPU Acceleration**: CPU-only inference
- **App Switching**: May lose context when switching apps

### Workarounds
- **Use Smaller Models**: Stick to 0.5B-1.5B parameter models
- **Save Work**: Export conversations regularly
- **Remote Access**: Use Termius for remote server access

## 🎯 Quick Start

### Fastest Method (iSH)
```bash
# 1. Install iSH from App Store
# 2. Open iSH and run:
apk update && apk add python3 py3-pip git cmake make clang
pip3 install delta
python3 -m delta.cli setup
python3 -m delta.cli pull qwen2:0.5b
python3 -m delta.cli run qwen2:0.5b
```

## 🆘 Getting Help

### If Installation Fails
1. **Check Storage**: Ensure you have at least 2GB free
2. **Use Python Module**: `python3 -m delta.cli` instead of `delta`
3. **Try Smaller Model**: Start with `qwen2:0.5b`
4. **Check Network**: Ensure stable WiFi connection

### Performance Tips
1. **Close Other Apps**: Free up memory
2. **Use WiFi**: Avoid cellular data for downloads
3. **Be Patient**: First run may be slow
4. **Save Progress**: Export conversations

## 🎉 Success!

Once installed, you can:
- **Chat with AI**: `python3 -m delta.cli run qwen2:0.5b`
- **Generate Text**: `python3 -m delta.cli generate qwen2:0.5b "Your prompt"`
- **List Models**: `python3 -m delta.cli list`
- **Get Help**: `python3 -m delta.cli --help`

Enjoy using Delta on your iPhone! 🚀📱
