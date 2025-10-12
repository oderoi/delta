# Delta Installation Guide

## Quick Fix for "delta: command not found" Error

If you're getting `delta: command not found` after installing, here are the solutions:

### Method 1: Use Python Module (Immediate Fix)

Instead of `delta setup`, use:
```bash
python -m delta.cli setup
```

Or for any delta command:
```bash
python -m delta.cli run qwen2:0.5b
python -m delta.cli list
python -m delta.cli --help
```

### Method 2: Fix PATH Issue (Permanent Fix)

Run the PATH fix script:
```bash
python fix_delta_path.py
```

This will:
- ✅ Find your Python scripts directory
- ✅ Create a delta wrapper script
- ✅ Add the directory to your PATH
- ✅ Test that delta command works

### Method 3: Manual PATH Setup

#### On macOS/Linux:
1. Find your Python scripts directory:
   ```bash
   python -c "import site; print(site.getsitepackages()[0])"
   ```
   The scripts directory is usually `../bin` from the site-packages directory.

2. Add to your shell profile:
   ```bash
   # For zsh (default on macOS)
   echo 'export PATH="$PATH:/path/to/scripts"' >> ~/.zshrc
   source ~/.zshrc
   
   # For bash
   echo 'export PATH="$PATH:/path/to/scripts"' >> ~/.bashrc
   source ~/.bashrc
   ```

#### On Windows:
1. Find your Python scripts directory (usually in your Python installation)
2. Add it to System PATH in Environment Variables
3. Or run: `setx PATH "%PATH%;C:\path\to\scripts"`

#### On Mobile Devices:

##### Android (Termux):
```bash
# Install delta
pip install delta

# Use as module
python -m delta.cli setup
python -m delta.cli run qwen2:0.5b
```

##### iOS (a-Shell/iSH):
```bash
# Install delta
pip3 install delta

# Use as module
python3 -m delta.cli setup
python3 -m delta.cli run qwen2:0.5b
```

## Complete Installation Process

### 1. Install Delta
```bash
pip install delta
```

### 2. Fix PATH Issue
```bash
python fix_delta_path.py
```

### 3. Setup Delta
```bash
delta setup
```

### 4. Test Installation
```bash
python test_delta_installation.py
```

### 5. Start Using Delta
```bash
delta run qwen2:0.5b
```

## Troubleshooting

### If `delta` command still not found:

1. **Check if delta is installed:**
   ```bash
   pip show delta
   ```

2. **Find the installation location:**
   ```bash
   python -c "import delta; print(delta.__file__)"
   ```

3. **Use the module directly:**
   ```bash
   python -m delta.cli --help
   ```

4. **Check your PATH:**
   ```bash
   echo $PATH  # On Unix
   echo %PATH%  # On Windows
   ```

### Platform-Specific Issues:

#### macOS:
- Make sure you're using the correct Python installation
- Check if you have multiple Python versions installed
- Try: `python3 -m delta.cli setup`

#### Windows:
- Make sure Python is in your PATH
- Check if you're using the correct Python installation
- Try: `py -m delta.cli setup`

#### Linux:
- Make sure you have the correct permissions
- Check if you need to use `python3` instead of `python`
- Try: `python3 -m delta.cli setup`

## Alternative Installation Methods

### Using Virtual Environment:
```bash
# Create virtual environment
python -m venv delta_env
source delta_env/bin/activate  # On Unix
# or
delta_env\Scripts\activate  # On Windows

# Install delta
pip install delta

# Use delta
python -m delta.cli setup
```

### Using Conda:
```bash
# Install delta
conda install -c conda-forge delta

# Or use pip in conda environment
conda create -n delta python=3.8
conda activate delta
pip install delta
```

## Verification

After installation, verify everything works:

```bash
# Test delta command
delta --help

# Test setup
delta setup

# Test with a model
delta run qwen2:0.5b
```

If any step fails, use the module method:
```bash
python -m delta.cli --help
python -m delta.cli setup
python -m delta.cli run qwen2:0.5b
```

## Support

If you're still having issues:

1. Run the diagnostic script:
   ```bash
   python test_delta_installation.py
   ```

2. Check the installation:
   ```bash
   delta doctor
   ```

3. Use the module method as a workaround:
   ```bash
   python -m delta.cli [command]
   ```
