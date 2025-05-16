# Delta

## Delta Settup for Ubuntu

**1. Install System Dependencies**
```bash
sudo apt update && sudo apt install -y python3 python3-venv curl git libjpeg-dev zlib1g-dev
```

**2. Install Ollama**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**3. Clone & Setup Delta**
```bash
# Clone repository
git clone https://github.com/oderoi/delta.git
cd delta

### Create virtual environment
python3 -m venv delta_env
source delta_env/bin/activate

### Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt  # Create this file with your dependencies if missing
```

**4. Configure System Integration**
```bash
# Run setup to create symlinks and PATH configuration
python delta.py setup

### Start Ollama service
ollama serve &
```

**5. Verify Installation**
```bash
delta list
delta pull mistral  # Example model
delta run mistral --wiki
```

**Recommended requirements.txt:**
```txt
rich>=13.7.0
ollama>=0.1.14
wikipedia>=1.4.0
arxiv>=2.1.0
Pillow>=10.3.0
duckduckgo-search>=5.0.1
```

**To Update Delta:**
```bash
cd ~/delta
git pull origin main
source delta_env/bin/activate
pip install --upgrade -r requirements.txt
```

**Troubleshooting Additions:**
```bash
# If you get web search errors
pip install --upgrade duckduckgo-search

# For image processing support
sudo apt install -y libjpeg-dev zlib1g-dev

# To run as background service
sudo systemctl enable ollama
```

---

### **macOS Setup Guide** (Intel & Apple Silicon)

**1. Install System Dependencies**
```bash
# Install Homebrew (package manager)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Core dependencies
brew install python3 libjpeg ollama
```

**2. Clone & Setup Delta**
```bash
git clone https://github.com/oderoi/delta.git
cd delta

# Create virtual environment
python3 -m venv delta_env
source delta_env/bin/activate

# Install requirements
pip install -r requirements.txt
```

**3. Configure System Integration**
```bash
# Run setup
python delta.py setup

# Start Ollama service (auto-start on login)
brew services start ollama
```

**4. Verify Installation**
```bash
delta list
delta pull mistral
delta run mistral --wiki
```

---

### **Windows Setup Guide** (10/11)

**1. Install Prerequisites** (PowerShell Admin)
```powershell
# Install Chocolatey (package manager)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install dependencies
choco install python ollama git vcredist2019
```

**2. Clone & Setup Delta**
```powershell
git clone https://github.com/oderoi/delta.git
cd delta

# Create virtual environment
python -m venv delta_env
delta_env\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

**3. Configure System Integration**
```powershell
# Run setup
python delta.py setup

# Start Ollama service (new PowerShell window)
Start-Process ollama -ArgumentList "serve"
```

**4. Add to PATH** (One-Time)
```powershell
[Environment]::SetEnvironmentVariable("Path", "$env:Path;$env:USERPROFILE\bin", "User")
```

---

### **Cross-Platform Notes**

**Common Commands**
```bash
# Update Delta
git pull origin main
pip install --upgrade -r requirements.txt

# Remove Delta
ollama app rm
rm -rf ~/delta  # macOS/Linux
Remove-Item -Recurse -Force ~\delta  # Windows
```

**Troubleshooting**

| Issue | macOS Fix | Windows Fix |
|-------|-----------|-------------|
| **Ollama not found** | `export PATH="$PATH:/usr/local/bin"` | Add `C:\Program Files\Ollama` to PATH |
| **Image processing** | `brew install libtiff webp` | `choco install libjpeg-turbo` |
| **GPU Acceleration** | `export OLLAMA_NUM_GPU=1` | Install [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) |

---

### **Platform-Specific Optimizations**

**For Apple Silicon (M1/M2/M3):**
```bash
# In ~/.zshrc
export OLLAMA_MLOCK=1
export OLLAMA_NUM_GPU=1
```

**For Windows WSL (Recommended):**
```bash
# In WSL Ubuntu
curl -fsSL https://ollama.ai/install.sh | sh
sudo systemctl enable ollama
```

---

### **Repository Enhancements**
Add these files to your GitHub repo:

**1. `.gitignore`**
```gitignore
delta_env/
__pycache__/
*.pyc
.DS_Store
*.log
```

**2. `README.md`** (Cross-Platform Badges)
````markdown
![macOS](https://img.shields.io/badge/macOS-兼容-success)
![Windows](https://img.shields.io/badge/Windows-兼容-success)
![Linux](https://img.shields.io/badge/Linux-兼容-success)

## Quick Start
```bash
git clone https://github.com/oderoi/delta.git
cd delta && python delta.py setup
```
````

**3. GitHub Actions (`.github/workflows/ci.yml`)**
```yaml
name: CI
on: [push]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        
    steps:
    - uses: actions/checkout@v4
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
```

This maintains consistency with your Ubuntu setup while addressing platform-specific requirements. Would you like me to elaborate on any particular aspect?
