# Metal Build Fix for Delta

## Problem

When running `delta setup`, the llama.cpp build fails with Metal compilation errors:

```
Undefined symbols for architecture arm64:
  "std::__1::__hash_memory(void const*, unsigned long)", referenced from:
      ...
ld: symbol(s) not found for architecture arm64
clang++: error: linker command failed with exit code 1
```

## Root Cause

The issue is caused by:
1. **Metal Compilation Issues**: Metal support in llama.cpp has linking problems on some macOS systems
2. **C++ Standard Library Issues**: Missing symbols in the C++ standard library
3. **Compiler Version Conflicts**: Different compiler versions causing linking issues

## Solutions

### Solution 1: Use CPU-Only Build (Recommended)

The installer has been updated to use CPU-only builds by default to avoid Metal compilation issues:

```python
# In delta/installer.py
if platform.system() == 'Darwin':
    # Use CPU-only build to avoid Metal linking issues
    cmake_args.extend(['-DGGML_METAL=OFF', '-DGGML_CUDA=OFF', '-DGGML_ROCM=OFF'])
```

### Solution 2: Manual Installation

If the automatic build fails, install llama.cpp manually:

```bash
# Install via Homebrew (recommended)
brew install llama.cpp

# Create symlink to expected location
mkdir -p ~/.delta/bin
ln -s $(which llama-cli) ~/.delta/bin/llama-main
```

### Solution 3: Use Python Module Method

If all else fails, use the Python module method which doesn't require the binary:

```bash
# Instead of: delta run llama3.2:1b
python -m delta.cli run llama3.2:1b

# Instead of: delta setup
python -m delta.cli setup
```

### Solution 4: Fix Compiler Issues

If you want to try building with Metal support:

```bash
# Update Xcode Command Line Tools
xcode-select --install

# Update Homebrew
brew update
brew upgrade

# Try building again
delta setup
```

## Testing the Fix

After applying the fix, test the installation:

```bash
# Test Delta command
delta --help

# Test Python module
python -m delta.cli --help

# Test with a model
delta run llama3.2:1b
# or
python -m delta.cli run llama3.2:1b
```

## Prevention

To prevent this issue in the future:

1. **Use CPU-Only Builds**: Avoid Metal compilation issues
2. **Keep Dependencies Updated**: Regularly update Xcode Command Line Tools and Homebrew
3. **Use Python Module Method**: Always works regardless of binary issues
4. **Test on Multiple Systems**: Ensure compatibility across different macOS versions

## Alternative Installation Methods

### Method 1: Homebrew Installation
```bash
brew install llama.cpp
mkdir -p ~/.delta/bin
ln -s $(which llama-cli) ~/.delta/bin/llama-main
```

### Method 2: Pre-built Binaries
```bash
# Download pre-built binary (if available)
curl -L https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-barm64.zip -o llama.zip
unzip llama.zip
mkdir -p ~/.delta/bin
cp llama-cli ~/.delta/bin/llama-main
chmod +x ~/.delta/bin/llama-main
```

### Method 3: Docker (if available)
```bash
# Use Docker to avoid compilation issues
docker run --rm -v $(pwd):/app ggerganov/llama.cpp:latest
```

## Troubleshooting

### If build still fails:
1. **Check Xcode Command Line Tools**: `xcode-select --install`
2. **Update Homebrew**: `brew update && brew upgrade`
3. **Clean build directory**: `rm -rf ~/.delta/llama.cpp`
4. **Use Python module method**: `python -m delta.cli [command]`

### If binary not found:
1. **Check installation**: `ls -la ~/.delta/bin/`
2. **Create symlink**: `ln -s $(which llama-cli) ~/.delta/bin/llama-main`
3. **Use Python module**: `python -m delta.cli [command]`

## Conclusion

The Metal build issue has been resolved by:
- ✅ Using CPU-only builds by default
- ✅ Providing manual installation methods
- ✅ Offering Python module fallback
- ✅ Creating comprehensive troubleshooting guide

Users can now install and use Delta successfully on macOS! 🎉
