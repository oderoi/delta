<div align="center">

<picture>
  <source media="(prefers-color-scheme: light)" srcset="/img/delta-logo.png">
  <img alt="delta logo" src="/img/delta-logo.png" width="20%" height="20%">
</picture>

</div>

# Delta

> <img alt="nan corp inference file logo" src="/img/file.png" width="15%" height="15%">

> # Introduction to Delta

> In a world where cutting-edge AI often demands expensive hardware like M4 chips or DGX systems, Delta stands out as a game-changer, particularly for regions like Africa where many rely on older laptops with CPUs. This project is personal—it's about bridging the gap for those left behind by the rapid pace of technological advancement, empowering users to harness the power of large language models (LLMs) without needing costly devices. Delta transforms local AI inferencing with a single-file engine that runs open-source LLMs on your CPU using just a terminal command. With CLI support, it delivers efficiency, fast backend runtime with zero overhead and optimized memory usage, making powerful AI accessible on standard hardware. What sets Delta apart is its ability to support distributed inferencing—not from the cloud, but across local computers—unlocking their collective potential seamlessly. With Delta, you can chat with LLMs offline, search Wikipedia, GitHub, arXiv, the internet via DuckDuckGo, or your own files, and even control your system with natural language commands like creating files or opening apps. Designed to go beyond tools like vLLM, llama.cpp, llm.c, Jan, LMStudio, and Ollama, Delta brings AI to your fingertips with simplicity and flexibility, aiming to democratize access and close the global AI divide.

![macOS](https://img.shields.io/badge/macOS-兼容-success)
![Windows](https://img.shields.io/badge/Windows-兼容-success)
![Linux](https://img.shields.io/badge/Linux-兼容-success)

## Delta Installation Guide

Delta is an AI assistant that runs locally on your machine. This guide will help you install Delta on your preferred operating system.

## Prerequisites

Before installing Delta, ensure your system meets these requirements:
- 4GB RAM minimum (8GB or more recommended)
- 10GB free disk space
- Internet connection for initial setup

## Installation Instructions

### Windows

<!-- 1. Download the installer from [https://nileagi.com/products/delta/installable/delta-installer.exe](https://nileagi.com/products/delta/installable/delta-installer.exe)

2. Run the installer:
   - Double-click `delta-installer.exe`
   - If you see a security warning, click "More info" and then "Run anyway"
   - The installer will automatically:
     - Install Python if not present
     - Install Git if not present
     - Install Ollama if not present
     - Set up Delta in your user directory

3. After installation:
   - Open a new Command Prompt or PowerShell window
   - Type `delta` to start the application
   - The first run will download the default AI model (deepseek-r1:1.5b)
-->

**Coming Soon ...**

### macOS
1. Download **delta δ** Installer

i. Using Link:
- Download [δ](https://nileagi.com/delta-installer-v1-macos.sh)
    - This will download **delta-installer-v1-macos.sh**

ii. Open Terminal and run:
- In Terminal navigate to the folder with **delta-installer-v1-macos.sh**
    ```bash
    cd navigate/to/the/folder/with/delta-installer-v1-macos.sh
    ```

**then**
- Run the installation script
   ```bash
   chmod +x delta-installer-v1-macos.sh
   ./delta-installer-v1-macos.sh
   ```

2. Dowload and Install via Terminal
**Open terminal**

- Make sure you have *curl*
    ```bash
    curl --version
    ```
- If you see *curl* version continue to the next step if not, download *curl*.
    ```bash
    brew install curl
    ```

- Download the installer
    ```bash
    curl -O https://nileagi.com/delta-installer-v1-macos.sh
    ```

- Make the script executable
    ```bash
    chmod +x curl delta-installer-v1-macos.sh
    ```

- Run the installation script
    ```bash
    ./delta-installer-v1-macos.sh
    ```


### Linux
1. Download **delta δ** Installer

i. Using Link:
- Download [δ](https://nileagi.com/delta-installer-v1-linux.sh)
    - This will download **delta-installer-v1-linux.sh**

ii. Open Terminal and run:
- In Terminal navigate to the folder with **delta-installer-v1-linux.sh**

    ```bash
    cd navigate/to/the/folder/with/delta-installer-v1-linux.sh
    ```

**then**
- Run the installation script
   ```bash
   chmod +x delta-installer-v1-linux.sh
   ./delta-installer-v1-linux.sh
   ```

2. Dowload and Install via Terminal
**Open terminal**
- Make sure you have *curl*
    ```bash
    curl --version
    ```
- If you see *curl* version continue to the next step if not, download *curl*.
    ```bash
    sudo apt update && sudo apt install curl -y
    ```

- Download the installer
    ```bash
    curl -O https://nileagi.com/delta-installer-v1-linux.sh
    ```

- Make the script executable
    ```bash
    chmod +x curl delta-installer-v1-linux.sh
    ```

- Run the installation script
    ```bash
    ./delta-installer-v1-linux.sh
    ``` 

**The installer will:**

   - Install Homebrew if not present - `for macos`
   - Install Python 3 if not present
   - Install Git if not present
   - Install Ollama if not present
   - Set up Delta in your home directory

**After installation:**

   - Open a new Terminal window
   - Type `delta` to start the application
   - The first run will download the default AI model (deepseek-r1:1.5b)

## Quickstart
---

To run and chat with `deepseek-r1:1.5b`:
```bash
delta run deepseek-r1:1.5b
```

## Troubleshooting

### Common Issues

1. **"Command not found: delta"**
   - Try restarting your terminal
   - On Windows, restart your computer to ensure PATH changes take effect

2. **Installation fails**
   - Ensure you have administrator privileges
   - Check your internet connection
   - Make sure you have enough disk space

3. **Ollama not starting**
   - On Windows: Run `ollama serve` in a separate terminal
   - On macOS/Linux: Run `sudo systemctl start ollama`

### Getting Help

If you encounter any issues:
1. Check the [FAQ](https://nileagi.com/products/delta/faq)
2. Visit our [GitHub repository](https://github.com/oderoi/delta)
3. Contact support at support@nileagi.com

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

```bash
delta -h
```
### **Install model**

**Syntax** `delta pull model_name`

```bash
delta pull llama3.2:1b
```

### **Check Models installed**

```bash
delta list
```

### **Remove / Delete model**

**Syntax** `delta remove model_name`

```bash
delta remove llama3.2:1b
```

### **Chat with the Models only**

**Syntax** `delta run model_name`

```bash
delta run llama3.1
```

### **Search through Wikipedia then use model to answer**

**Syntax** `delta run model_name --wiki`

```bash
delta run llama3.1 --wiki
```

### **search through DuckduckGo (Browser) then use model to answer**

**Syntax** `delta run model_name --ddg`

```bash
delta run llama3.1 --ddg
```

### **Search through your local documents or summarize**

**Syntax** `delta run model_name --docs /location/to/your/document`

**Linux or MacOs**
```bash
delta run llama3.1:latest --docs /home/Documents/computer_vision_nlp.pdf
```

**Windows**
```bash
delta run llama3.1:latest --docs C:\Users\home\Documents\computer_vision_nlp.pdf
```

### **View your Chat History**

```bash
delta hist
```

### **Clear Chat History**

```bash
delta hist --clear
```

### **Delta Version**

```bash
delta --version
```

## Run Delta

**At the `>` prompt**

- **Enter:** Adds a new line.

- **Shift + Arrow Keys:** Select text (left, right, up, down).

- **Ctrl + C:** Copies selected text to the clipboard or exits if no selection.

- **Ctrl + V:** Pastes clipboard content at the cursor.

- **Ctrl + j:** Submits the input.

- **Ctrl + D:** or type `"exit"`Exits the session.

- **Arrow Keys:** move your coursor left, right, up and down on delta.

## Uninstallation

### Windows
1. Delete the `.delta` folder in your user directory
2. Remove Delta from your PATH environment variable

### macOS/Linux
1. Delete the `.delta` folder in your home directory
2. Remove the Delta entry from your shell's configuration file (.bashrc, .zshrc, etc.)

## System Requirements

- **Operating System:**
  - Windows 10/11
  - macOS 10.15 or later
  - Ubuntu 20.04 or later, or equivalent Linux distribution

- **Hardware:**
  - CPU: 2GHz dual-core processor or better
  - RAM: 4GB minimum (8GB recommended)
  - Storage: 10GB free space
  - Internet: Required for initial setup and model downloads

## Privacy and Security

Delta runs completely locally on your machine. No data is sent to external servers except for:
- Initial package downloads
- Model downloads from Ollama
- Optional telemetry (can be disabled)

## License

Delta is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
