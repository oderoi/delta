Delta CLI
A lightweight, privacy-focused CLI for running local LLMs using llama.cpp.
Installation
Desktop (Windows, macOS, Linux)

Install Python 3.8+ and pip.
Create a virtual environment to avoid conflicts:python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate


Install Delta via pip:pip install delta


Run setup to download llama.cpp binary and configure:delta setup


Follow prompts to add ~/.delta/bin and ~/bin/delta_env/bin to PATH.
Linux/macOS: Add export PATH="$PATH:$HOME/.delta/bin:$HOME/bin/delta_env/bin" to .bashrc or .zshrc and run source ~/.bashrc.
Windows: Add C:\Users\<YourUser>\.delta\bin;C:\Users\<YourUser>\bin\delta_env\Scripts to System PATH via Settings or setx PATH "%PATH%;C:\Users\<YourUser>\.delta\bin;C:\Users\<YourUser>\bin\delta_env\Scripts".



Mobile (Android: Termux, iOS: a-Shell/iSH)
Android (Termux)

Install Termux from F-Droid or GitHub (not Play Store).
Install dependencies:pkg install python git make clang
pip install delta


Build llama.cpp:git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
mkdir -p ~/.delta/bin
cp main ~/.delta/bin/llama-main


Run setup:delta setup



iOS (a-Shell or iSH)

Install a-Shell or iSH from App Store.
Install dependencies:apk add python3 git make clang  # iSH
pkg install python git make clang  # a-Shell
pip3 install delta


Build llama.cpp:git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
mkdir -p ~/.delta/bin
cp main ~/.delta/bin/llama-main


Run setup:delta setup



Usage

Download a model: delta pull qwen2:0.5b
List models: delta list
Run chat: delta run qwen2:0.5b
Chat with search: delta run --ddg "AI ethics"
Check system: delta check
View history: delta hist
Clear history: delta hist --clear
Show version: delta version

Notes

Models are GGUF format from Hugging Face (e.g., meta-llama/Llama-3.1-8B-Instruct).
Default model: Qwen/Qwen2-0.5B-Instruct (lightweight for mobile).
For GPU support (Linux/Windows only), build llama.cpp with CUDA/OpenCL.
Mobile: Use small models (0.5B-1.3B) due to limited RAM (4GB+ recommended).
If delta command fails, ensure ~/.delta/bin and virtual environment bin are in PATH.

License
MIT