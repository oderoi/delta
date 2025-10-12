# Delta iSH-Shell Installation Guide

This guide specifically addresses installation issues on iPhone iSH-shell environment.

## 🚨 Common iSH-Shell Issues

### 1. Missing Python Development Headers
**Error:** `Python.h: No such file or directory`
**Solution:** Install development packages

### 2. Setuptools/Packaging Compatibility
**Error:** `canonicalize_version() got an unexpected keyword argument 'strip_trailing_zero'`
**Solution:** Upgrade setuptools and packaging

### 3. psutil Compilation Failures
**Error:** `Failed building wheel for psutil`
**Solution:** Install build tools or use compatibility layer

## 🚀 Quick Fix (Recommended)

```bash
# One-liner fix for iSH-shell
curl -s https://raw.githubusercontent.com/your-repo/delta/main/fix_ish_install.sh | bash
```

## 📋 Step-by-Step Installation

### Method 1: Automated iSH-Shell Installer

```bash
# Download and run the iSH-shell installer
curl -O https://raw.githubusercontent.com/your-repo/delta/main/ish_install.sh
chmod +x ish_install.sh
./ish_install.sh
```

### Method 2: Python-based Installer

```bash
# Download and run the Python installer
curl -O https://raw.githubusercontent.com/your-repo/delta/main/install_delta_ish.py
python3 install_delta_ish.py
```

### Method 3: Manual Installation

```bash
# Step 1: Install development packages
apk add gcc python3-dev musl-dev linux-headers build-base libffi-dev openssl-dev

# Step 2: Upgrade Python tools
python3 -m pip install --upgrade pip setuptools wheel packaging

# Step 3: Install core dependencies
python3 -m pip install click requests tabulate colorama huggingface_hub tqdm

# Step 4: Handle psutil (may fail)
python3 -m pip install psutil || echo "psutil failed - continuing without it"

# Step 5: Install Delta
python3 -m pip uninstall delta -y || true
python3 -m pip install .

# Step 6: Test installation
python3 -m delta.cli --help
```

## 🔧 Troubleshooting

### Issue: `Python.h: No such file or directory`
```bash
# Install Python development headers
apk add python3-dev musl-dev linux-headers
```

### Issue: `strip_trailing_zero` error
```bash
# Upgrade setuptools and packaging
python3 -m pip install --upgrade setuptools packaging
```

### Issue: psutil compilation fails
```bash
# Try binary wheel
python3 -m pip install --only-binary=psutil psutil

# Or skip psutil (some features disabled)
echo "psutil will be optional"
```

### Issue: wikipedia/duckduckgo-search fails
```bash
# Skip optional dependencies
echo "Skipping problematic optional dependencies"
```

## 📱 iSH-Shell Specific Considerations

### 1. Limited Resources
- Use smaller models (TinyLlama, Phi-3-mini)
- Reduce thread count: `--threads 2`
- Monitor memory usage

### 2. File System Limitations
- iSH-shell has limited file system access
- Some operations may be restricted
- Use module syntax: `python3 -m delta.cli`

### 3. Network Limitations
- Some network operations may be restricted
- Use local models when possible
- Test connectivity first

## 🎯 Optimized Usage for iSH-Shell

```bash
# Check system specs
python3 -m delta.cli check

# Setup Delta
python3 -m delta.cli setup

# Download a small model
python3 -m delta.cli pull tinyllama

# Run with mobile-optimized settings
python3 -m delta.cli run tinyllama --threads 2

# Generate with limited tokens
python3 -m delta.cli generate tinyllama "Hello" --max-tokens 100 --threads 2
```

## 🚨 Known Limitations

1. **psutil may not work** - Some system monitoring features disabled
2. **Some optional dependencies fail** - Wikipedia, DuckDuckGo search may not work
3. **Limited GPU support** - No GPU acceleration in iSH-shell
4. **Memory constraints** - Use small models only

## ✅ Success Indicators

After successful installation, you should see:
- `python3 -m delta.cli --help` works
- `python3 -m delta.cli doctor` shows no critical errors
- Core dependencies (click, requests, etc.) are available

## 🆘 If All Else Fails

If you're still having issues:

1. **Reset iSH-shell**: Close and reopen the app
2. **Use minimal installation**: Skip optional dependencies
3. **Use alternative**: Try a different Python environment
4. **Report issues**: Include full error output

## 📞 Support

For iSH-shell specific issues:
1. Run `python3 -m delta.cli doctor` and share output
2. Check iSH-shell version and Python version
3. Verify all development packages are installed
4. Try the minimal installation approach
