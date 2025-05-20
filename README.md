<div align="center">

<picture>
  <source media="(prefers-color-scheme: light)" srcset="/img/delta.png">
  <img alt="tiny corp logo" src="/img/delta.png" width="20%" height="20%">
</picture>

</div>

# Delta

![macOS](https://img.shields.io/badge/macOS-兼容-success)
![Windows](https://img.shields.io/badge/Windows-兼容-success)
![Linux](https://img.shields.io/badge/Linux-兼容-success)

## Quick Start
```bash
git clone https://github.com/oderoi/delta.git
cd delta && python delta.py setup
```

## Delta Settup Guide

### **Ubuntu**

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

### **macOS** (Intel & Apple Silicon)

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
```

**4. Verify Installation**
```bash
delta list
delta pull mistral
delta run mistral --wiki
```

---

### **Windows** (10/11)

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
```

**4. Add to PATH** (One-Time)
```powershell
[Environment]::SetEnvironmentVariable("Path", "$env:Path;$env:USERPROFILE\bin", "User")
```

## Quickstart
---

To run and chat with `llama3.1`:
```bash
delta run llama3.1
```

## Model library
---

delta support a list models available on [ollama](https://www.ollama.com/library).

Here are some examples of the models that can be downloaded
|Model|Parameter|Size|Dowload|
|-----|---------|----|-------|
|Gemma 3|1B|815MB|`delta pull gemma3:1b`|
|Gemma 3|4B|3.3GB|`delta pull gemma3`|
|Gemma 3|12B|8.1GB|`delta pull gemma3:12b`|
|DeepSeep-R1|7B|4.7GB|`delta pull deepseek-r1`|
|Llama 3.2|3B|2.0GB|`delta pull llama3.2`|
|Llama 3.2|1B|1.3GB|`delta pull llama3.2:1b`|
|Llama 3.1|8B|4.7GB|`delta pull llama3.1`|
|Phi 4|14B|9.1MB|`delta pull phi4`|
|Phi 4 Mini|3.8B|2.5GB|`delta pull phi4-mini`|
|Mistral|7B|4.1GB|`delta pull mistral`|
|Moondream 2|1.4B|829MB|`delta pull moondream`|
|Neural Chat|7B|4.1GB|`delta pull meural-chat`|
|Starling|7B|4.1GB|`delta pull starling-lm`|
|Code Llama|7B|3.8GB|`delta pull codellama`|
|Llama 2 Uncensored|7B|3.8GB|`delta pull llama2-uncensored`|
|LLaVA|7B|4.5GB|`delta pull llava`|
|Granite-3.3|8B|4.9GB|`delta pull granite3.3`|

```note
You should have at least 8GB of RAM available to run the 7B models, 16 GB to run 13B models, and 32 GB to run the 33B models.
```

## Use Delta
---

### **Help**

'''bash
delta -h
```

### **Check Models installed**

```bash
delta list
```

### **Chat with the Models only**

**Syntax** `delta run model_name`

```bash
delta run llama3.1
```

### **Search through Wikipedia then use model to answer**

**Syntax** `delta run model_name --wiki`

```bash
delta run llama3.1 llama3.1 --wiki
```

### **search through DuckduckGo (Browser) then use model to answer**

**Syntax** `delta run model_name --ddg`

```bash
delta run llama3.1 --ddg
```
