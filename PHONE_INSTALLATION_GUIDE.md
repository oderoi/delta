# Delta Phone Installation Guide

This guide helps you install Delta on mobile devices (Android phones, tablets) and resolves common installation issues.

## Quick Fix for Phone Installation

If you're getting `ModuleNotFoundError: No module named 'click'` or similar dependency errors, use this quick fix:

### Method 1: Automated Fix Script

```bash
# Download and run the phone installation script
curl -O https://raw.githubusercontent.com/your-repo/delta/main/phone_install.sh
chmod +x phone_install.sh
./phone_install.sh
```

### Method 2: Manual Fix

```bash
# 1. Install missing dependencies
pip3 install click requests tabulate colorama huggingface_hub tqdm psutil

# 2. Reinstall delta
pip3 uninstall delta -y
pip3 install .

# 3. Test installation
python3 -m delta.cli --help
```

## Step-by-Step Installation

### Prerequisites

1. **Python 3.8+** - Install from your app store or use Termux
2. **pip** - Usually comes with Python
3. **Internet connection** - For downloading models

### Installation Steps

1. **Clone or download Delta**
   ```bash
   git clone https://github.com/your-repo/delta.git
   cd delta
   ```

2. **Run the phone installation script**
   ```bash
   chmod +x phone_install.sh
   ./phone_install.sh
   ```

3. **Or use the Python installer**
   ```bash
   python3 install_delta_phone.py
   ```

4. **Verify installation**
   ```bash
   python3 -m delta.cli doctor
   ```

## Common Issues and Solutions

### Issue: `ModuleNotFoundError: No module named 'click'`

**Solution:**
```bash
pip3 install click
python3 -m delta.cli --help
```

### Issue: `ModuleNotFoundError: No module named 'requests'`

**Solution:**
```bash
pip3 install requests
```

### Issue: Permission denied errors

**Solution:**
```bash
# Use --user flag for local installation
pip3 install --user click requests tabulate colorama huggingface_hub tqdm psutil
```

### Issue: Delta command not found

**Solution:**
```bash
# Use module syntax instead
python3 -m delta.cli --help
python3 -m delta.cli setup
python3 -m delta.cli run
```

## Mobile-Specific Considerations

### Android/Termux Installation

1. **Install Termux from F-Droid**
2. **Update packages:**
   ```bash
   pkg update && pkg upgrade
   pkg install python git
   ```

3. **Install Delta:**
   ```bash
   git clone https://github.com/your-repo/delta.git
   cd delta
   ./phone_install.sh
   ```

### iOS/iPadOS Installation

1. **Install Python from App Store** (Pythonista, Pyto, etc.)
2. **Use the Python installer:**
   ```bash
   python3 install_delta_phone.py
   ```

## Testing Your Installation

After installation, test with these commands:

```bash
# Check system specs
python3 -m delta.cli check

# List available models
python3 -m delta.cli list

# Download a small model
python3 -m delta.cli pull tinyllama

# Run a chat
python3 -m delta.cli run tinyllama
```

## Troubleshooting

### Run Diagnostics

```bash
python3 -m delta.cli doctor
```

This will show:
- Python version
- System specs
- Installed dependencies
- Model status
- Common issues

### Manual Dependency Check

```bash
python3 -c "import click, requests, tabulate, colorama, huggingface_hub, tqdm, psutil; print('All dependencies OK')"
```

### Reset Installation

If everything fails:

```bash
# Remove everything
pip3 uninstall delta -y
pip3 uninstall click requests tabulate colorama huggingface_hub tqdm psutil -y

# Reinstall
pip3 install click requests tabulate colorama huggingface_hub tqdm psutil
pip3 install .
```

## Performance Tips for Mobile

1. **Use smaller models** - Start with TinyLlama or Phi-3-mini
2. **Reduce threads** - Use `--threads 2` for mobile devices
3. **Monitor memory** - Use `python3 -m delta.cli check` to see recommendations
4. **Use quantized models** - Q4_K_M or Q8_0 quantization

## Example Usage

```bash
# Setup Delta
python3 -m delta.cli setup

# Download a small model
python3 -m delta.cli pull tinyllama

# Run chat with mobile-optimized settings
python3 -m delta.cli run tinyllama --threads 2

# Generate text
python3 -m delta.cli generate tinyllama "Hello, how are you?" --max-tokens 100
```

## Support

If you're still having issues:

1. Run `python3 -m delta.cli doctor` and share the output
2. Check your Python version: `python3 --version`
3. Verify pip is working: `pip3 --version`
4. Try the manual dependency installation above

The phone installation scripts handle most common issues automatically, but mobile devices can have unique constraints that require manual intervention.
