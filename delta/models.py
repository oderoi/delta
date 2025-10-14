import os
import json
import subprocess
import requests
from huggingface_hub import hf_hub_download
from pathlib import Path
import shutil
import platform
from tqdm import tqdm
from datetime import datetime
import time

HOME_DIR = Path.home() / ".delta"
MODELS_DIR = HOME_DIR / "models"
BIN_DIR = HOME_DIR / "bin"
CONFIG_FILE = HOME_DIR / "config.json"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
BIN_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = "qwen2:0.5b"

# Define model_map at module scope for use in pull_model and list_models
model_map = {
    "LFM2:700m": {
        "repo_id": "LiquidAI/LFM2-700M-GGUF",
        "filename": "LFM2-700M-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "LFM2:350m": {
        "repo_id": "LiquidAI/LFM2-350M-Extract-GGUF",
        "filename": "LFM2-350M-Extract-F16.gguf",
        "chat_format": "chatml"
    },  
    "LFM2:1.2b": {
        "repo_id": "LiquidAI/LFM2-1.2B-RAG-GGUF",
        "filename": "LFM2-1.2B-RAG-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "LFM2-VL:1.6b": {
        "repo_id": "LiquidAI/LFM2-VL-1.6B-GGUF",
        "filename": "LFM2-VL-1.6B-Q8_0.gguf",
        "chat_format": "chatml"
    },
    "LFM2-VL:450m": {
        "repo_id": "LiquidAI/LFM2-VL-450M-GGUF",
        "filename": "LFM2-VL-450M-F16.gguf",
        "chat_format": "chatml"
    },
    "LFM2:8b": {
        "repo_id": "LiquidAI/LFM2-8B-A1B-GGUF",
        "filename": "LFM2-8B-A1B-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "llama3.1:8b": {
        "repo_id": "unsloth/Llama-3.1-8B-Instruct-GGUF",
        "filename": "Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "chat_format": "llama3"
    },
    "llama3.2:3b": {
        "repo_id": "unsloth/Llama-3.2-3B-Instruct-GGUF",
        "filename": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "chat_format": "llama3"
    },
    "llama3.2:1b": {
        "repo_id": "unsloth/Llama-3.2-1B-Instruct-GGUF",
        "filename": "Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        "chat_format": "llama3"
    },
    "tinyllama": {
        "repo_id": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
        "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "bitnet": {
        "repo_id": "microsoft/bitnet-b1.58-2B-4T-gguf",
        "filename": "ggml-model-i2_s.gguf",
        "chat_format": "chatml",
        "requires_special": True
    },
    "deepseek-r1:1.5b": {
        "repo_id": "unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
        "filename": "DeepSeek-R1-Distill-Qwen-1.5B-Q4_K_M.gguf",
        "chat_format": "deepseek"
    },
    "deepseek-r1:7b": {
        "repo_id": "unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF",
        "filename": "DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf",
        "chat_format": "deepseek"
    },
    "phi3": {
        "repo_id": "microsoft/Phi-3-mini-4k-instruct-gguf",
        "filename": "Phi-3-mini-4k-instruct-q4.gguf",
        "chat_format": "phi3"
    },
    "phi4-mini": {
        "repo_id": "unsloth/Phi-4-mini-reasoning-GGUF",
        "filename": "Phi-4-mini-reasoning-Q4_K_M.gguf",
        "chat_format": "phi4"
    },
    "llama3": {
        "repo_id": "bartowski/Meta-Llama-3-8B-Instruct-GGUF",
        "filename": "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
        "chat_format": "llama3"
    },
    "mistral": {
        "repo_id": "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
        "filename": "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        "chat_format": "mistral-v1"
    },
    "gemma2:2b": {
        "repo_id": "unsloth/gemma-2-it-GGUF",
        "filename": "gemma-2-2b-it.q4_k_m.gguf",
        "chat_format": "gemma"
    },
    "gemma3:270m": {
        "repo_id": "unsloth/gemma-3-270m-it-GGUF",
        "filename": "gemma-3-270m-it-Q4_K_M.gguf",
        "chat_format": "gemma"
    },
    "gemma3:1b": {
        "repo_id": "unsloth/gemma-3-1b-it-GGUF",
        "filename": "gemma-3-1b-it-Q4_K_M.gguf",
        "chat_format": "gemma"
    },
    "gemma3:4b": {
        "repo_id": "unsloth/gemma-3-4b-it-GGUF",
        "filename": "gemma-3-4b-it-Q4_K_M.gguf",
        "chat_format": "gemma"
    },
    "gemma3n:e4b": {
        "repo_id": "unsloth/gemma-3n-E4B-it-GGUF",
        "filename": "gemma-3n-E4B-it-Q4_K_M.gguf",
        "chat_format": "gemma"
    },
    "gemma3n:e2b": {
        "repo_id": "unsloth/gemma-3n-E2B-it-GGUF",
        "filename": "gemma-3n-E2B-it-Q4_K_M.gguf",
        "chat_format": "gemma"
    },
    "qwen3:0.6b": {
        "repo_id": "unsloth/Qwen3-0.6B-GGUF",
        "filename": "Qwen3-0.6B-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "qwen3:1.7b": {
        "repo_id": "unsloth/Qwen3-1.7B-GGUF",
        "filename": "Qwen3-1.7B-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "qwen3:4b": {
        "repo_id": "unsloth/Qwen3-4B-GGUF",
        "filename": "Qwen3-4B-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "qwen3:8b": {
        "repo_id": "unsloth/Qwen3-8B-GGUF",
        "filename": "Qwen3-8B-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "qwen2:0.5b": {
        "repo_id": "Qwen/Qwen2-0.5B-Instruct-GGUF",
        "filename": "qwen2-0_5b-instruct-q4_k_m.gguf",
        "chat_format": "chatml"
    },
    "qwen2.5-coder:0.5b": {
        "repo_id": "unsloth/Qwen2.5-Coder-0.5B-Instruct-GGUF",
        "filename": "Qwen2.5-Coder-0.5B-Instruct-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "qwen2.5-coder:1.5b": {
        "repo_id": "unsloth/Qwen2.5-Coder-1.5B-Instruct-GGUF",
        "filename": "Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "qwen2.5-coder:3b": {
        "repo_id": "unsloth/Qwen2.5-Coder-3B-Instruct-GGUF",
        "filename": "Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "qwen2.5-coder:7b": {
        "repo_id": "unsloth/Qwen2.5-Coder-7B-Instruct-GGUF",
        "filename": "Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "qwen2.5:3b": {
        "repo_id": "unsloth/Qwen2.5-VL-3B-Instruct-GGUF",
        "filename": "Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "qwen2.5:7b": {
        "repo_id": "unsloth/Qwen2.5-VL-7B-Instruct-GGUF",
        "filename": "Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
}

def init_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps({"default_model": DEFAULT_MODEL}))

def ensure_llama_binary(model_name: str = None, quiet: bool = False):
    """Ensure appropriate binary (llama.cpp or bitnet.cpp) is available, preferring source build."""
    is_bitnet = model_name and model_name == "bitnet"
    
    # First, try to find the real binary (llama-cli.exe)
    if not is_bitnet:
        real_binary_path = BIN_DIR / "llama-cli.exe"
        if real_binary_path.exists():
            if not quiet:
                pass  # print(f"llama.cpp binary found at {real_binary_path}")  # Suppressed for clean output
            return real_binary_path
    
    # Fallback to the old naming convention
    binary_name = "llama-main" if not is_bitnet else "bitnet-main"
    if platform.system() == "Windows":
        binary_name += ".exe"
    binary_path = BIN_DIR / binary_name
    
    # Check if source-built binary exists
    if binary_path.exists():
        if not quiet:
            pass  # print(f"{'bitnet.cpp' if is_bitnet else 'llama.cpp'} binary found at {binary_path}")  # Suppressed for clean output
        return binary_path

    # Try Homebrew for llama.cpp (not bitnet)
    if shutil.which("brew") and not is_bitnet:
        try:
            subprocess.run(["brew", "list", "llama.cpp"], check=True, capture_output=True, text=True)
            if not quiet:
                print("llama.cpp is already installed via brew")
            brew_bin = shutil.which("llama-cli")
            if brew_bin:
                if not quiet:
                    print(f"Using brew-installed llama-cli at {brew_bin}")
                return Path(brew_bin)
        except subprocess.CalledProcessError:
            if not quiet:
                print("llama.cpp not installed via brew. Falling back to build from source.")

    # Build from source
    if not quiet:
        print(f"Building {'bitnet.cpp' if is_bitnet else 'llama.cpp'} binary from source for {platform.system()}...")
    build_dir = HOME_DIR / ("bitnet.cpp" if is_bitnet else "llama.cpp")
    repo_url = "https://github.com/microsoft/bitnet.cpp.git" if is_bitnet else "https://github.com/ggerganov/llama.cpp.git"

    # Check for required build tools
    build_tools = ["git", "cmake"]
    if platform.system() != "Windows":
        build_tools.append("make")
        build_tools.append("clang")
    missing_tools = []
    for tool in build_tools:
        if not shutil.which(tool):
            missing_tools.append(tool)
    if missing_tools:
        tool_install_instructions = {
            "git": {
                "Windows": "Install Git from https://git-scm.com/download/win or use 'winget install Git.Git'",
                "Darwin": "Install Git via Homebrew: 'brew install git' or Xcode Command Line Tools: 'xcode-select --install'",
                "Linux": "Install Git: 'sudo apt-get install git' (Ubuntu) or 'sudo yum install git' (CentOS)",
                "Android": "Install Git in Termux: 'pkg install git'",
                "iOS": "Install Git in a-Shell/iSH: 'apk add git' (iSH) or 'pkg install git' (a-Shell)",
            },
            "cmake": {
                "Windows": "Install CMake from https://cmake.org/download/ or use 'winget install Kitware.CMake'",
                "Darwin": "Install CMake via Homebrew: 'brew install cmake'",
                "Linux": "Install CMake: 'sudo apt-get install cmake' (Ubuntu) or 'sudo yum install cmake' (CentOS)",
                "Android": "Install CMake in Termux: 'pkg install cmake'",
                "iOS": "Install CMake in a-Shell/iSH: 'apk add cmake' (iSH) or 'pkg install cmake' (a-Shell)",
            },
            "make": {
                "Windows": "Not required on Windows",
                "Darwin": "Install make via Homebrew: 'brew install make' or Xcode Command Line Tools: 'xcode-select --install'",
                "Linux": "Install make: 'sudo apt-get install make' (Ubuntu) or 'sudo yum install make' (CentOS)",
                "Android": "Install make in Termux: 'pkg install make'",
                "iOS": "Install make in a-Shell/iSH: 'apk add make' (iSH) or 'pkg install make' (a-Shell)",
            },
            "clang": {
                "Windows": "Not required on Windows",
                "Darwin": "Install clang via Homebrew: 'brew install llvm' or Xcode Command Line Tools: 'xcode-select --install'",
                "Linux": "Install clang: 'sudo apt-get install clang' (Ubuntu) or 'sudo yum install clang' (CentOS)",
                "Android": "Install clang in Termux: 'pkg install clang'",
                "iOS": "Install clang in a-Shell/iSH: 'apk add clang' (iSH) or 'pkg install clang' (a-Shell)",
            }
        }
        platform_name = "iOS" if platform.system() == "Darwin" and "ios" in platform.uname().release.lower() else platform.system()
        platform_name = "Android" if platform.system() == "Linux" and "android" in platform.uname().release.lower() else platform_name
        print(f"Missing build tools: {', '.join(missing_tools)}")
        for tool in missing_tools:
            print(f"To install {tool}: {tool_install_instructions[tool].get(platform_name, 'Please install manually')}")
        raise RuntimeError(f"Cannot build {'bitnet.cpp' if is_bitnet else 'llama.cpp'}: missing {', '.join(missing_tools)}")

    # Configure Git for cloning
    try:
        subprocess.run(["git", "config", "--global", "http.version", "HTTP/1.1"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "config", "--global", "http.postBuffer", "524288000"], check=True, capture_output=True, text=True)
        if not quiet:
            print("Configured Git to use HTTP/1.1 and increased postBuffer to 500MB")
    except subprocess.CalledProcessError as e:
        print(f"Failed to configure Git: {e.stderr}")
        raise RuntimeError("Failed to configure Git for cloning")

    # Clone repository with retries and shallow clone
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        if build_dir.exists():
            shutil.rmtree(build_dir)
        try:
            if not quiet:
                print(f"Attempt {attempt}/{max_retries}: Cloning {'bitnet.cpp' if is_bitnet else 'llama.cpp'} with --depth 1...")
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(build_dir)],
                check=True,
                capture_output=True,
                text=True
            )
            if not quiet:
                print(f"Cloned {'bitnet.cpp' if is_bitnet else 'llama.cpp'} to {build_dir}")
            break
        except subprocess.CalledProcessError as e:
            print(f"Attempt {attempt}/{max_retries} failed: {e.stderr}")
            if attempt < max_retries:
                if not quiet:
                    print(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                if not quiet:
                    print(f"Failed to clone {'bitnet.cpp' if is_bitnet else 'llama.cpp'} after {max_retries} attempts")
                    print("Possible solutions:")
                    print("1. Check your internet connection")
                    print("2. Try cloning manually: git clone --depth 1 https://github.com/ggerganov/llama.cpp.git ~/.delta/llama.cpp")
                    print("3. Ensure Git is up-to-date: brew upgrade git")
                    print("4. Clear Git cache: git cache clear")
                    print("5. Try a different network or VPN")
                raise RuntimeError(f"Failed to clone {'bitnet.cpp' if is_bitnet else 'llama.cpp'} repository")

    # Build with Metal support (first attempt)
    try:
        os.chdir(build_dir)
        build_subdir = build_dir / "build"
        build_subdir.mkdir(exist_ok=True)
        os.chdir(build_subdir)
        cmake_args = ["cmake", "..", "-DCMAKE_BUILD_TYPE=Release"]
        if platform.system() == "Darwin" and not is_bitnet:
            cmake_args.extend([
                "-DCMAKE_C_COMPILER=/usr/bin/clang",
                "-DCMAKE_CXX_COMPILER=/usr/bin/clang++",
                "-DGGML_METAL=ON",
                "-DGGML_BUILD_SERVER=ON",
                "-DCMAKE_OSX_ARCHITECTURES=arm64",
                "-DCMAKE_OSX_DEPLOYMENT_TARGET=13.0",
                "-DCMAKE_EXE_LINKER_FLAGS=-framework Metal -framework Foundation"
            ])
        result = subprocess.run(cmake_args, check=True, capture_output=True, text=True)
        if not quiet:
            print(f"CMake configuration output:\n{result.stdout}")
            if result.stderr:
                print(f"CMake warnings:\n{result.stderr}")
        result = subprocess.run(["make"], check=True, capture_output=True, text=True)
        if not quiet:
            print(f"Make output:\n{result.stdout}")
            if result.stderr:
                print(f"Make warnings:\n{result.stderr}")
        binary_source = build_dir / "main"
        
        if not binary_source.exists():
            raise FileNotFoundError("Build succeeded but 'main' binary not found")
        
        shutil.copy(binary_source, binary_path)
        if platform.system() != "Windows":
            binary_path.chmod(0o755)
        if not quiet:
            print(f"{'bitnet.cpp' if is_bitnet else 'llama.cpp'} binary built and installed to {binary_path}")
        return binary_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        if not quiet:
            print(f"Failed to build {'bitnet.cpp' if is_bitnet else 'llama.cpp'} with Metal support:")
            if isinstance(e, subprocess.CalledProcessError):
                print(f"Error output:\n{e.stderr}")
            else:
                print(f"Error: {str(e)}")
            print("Falling back to CPU-only build...")

    # Fallback to CPU-only build
    try:
        os.chdir(build_dir)
        shutil.rmtree(build_subdir, ignore_errors=True)
        build_subdir.mkdir(exist_ok=True)
        os.chdir(build_subdir)
        cmake_args = ["cmake", "..", "-DCMAKE_BUILD_TYPE=Release", "-DGGML_METAL=OFF"]
        if platform.system() == "Darwin" and not is_bitnet:
            cmake_args.extend([
                "-DCMAKE_C_COMPILER=/usr/bin/clang",
                "-DCMAKE_CXX_COMPILER=/usr/bin/clang++",
                "-DCMAKE_OSX_ARCHITECTURES=arm64",
                "-DCMAKE_OSX_DEPLOYMENT_TARGET=13.0"
            ])
        result = subprocess.run(cmake_args, check=True, capture_output=True, text=True)
        if not quiet:
            print(f"CMake configuration output (CPU-only):\n{result.stdout}")
            if result.stderr:
                print(f"CMake warnings (CPU-only):\n{result.stderr}")
        result = subprocess.run(["make"], check=True, capture_output=True, text=True)
        if not quiet:
            print(f"Make output (CPU-only):\n{result.stdout}")
            if result.stderr:
                print(f"Make warnings (CPU-only):\n{result.stderr}")
        binary_source = build_dir / "main"
        
        if not binary_source.exists():
            raise FileNotFoundError("CPU-only build succeeded but 'main' binary not found")
        
        shutil.copy(binary_source, binary_path)
        if platform.system() != "Windows":
            binary_path.chmod(0o755)
        if not quiet:
            print(f"{'bitnet.cpp' if is_bitnet else 'llama.cpp'} CPU-only binary built and installed to {binary_path}")
            print("Note: This binary uses CPU only (no Metal/GPU acceleration).")
        return binary_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        if not quiet:
            print(f"Failed to build {'bitnet.cpp' if is_bitnet else 'llama.cpp'} (CPU-only):")
            if isinstance(e, subprocess.CalledProcessError):
                print(f"Error output:\n{e.stderr}")
            else:
                print(f"Error: {str(e)}")
            if platform.system() == "Darwin":
                print("This may be due to missing Xcode Command Line Tools or incompatible compiler.")
                print("Ensure Xcode Command Line Tools are installed: 'xcode-select --install'")
                print("Or install dependencies via Homebrew: 'brew install llvm'")
                print("If using Homebrew LLVM, update PATH: 'export PATH=\"/opt/homebrew/opt/llvm/bin:$PATH\"'")
                print("Alternatively, install llama.cpp via Homebrew: 'brew install llama.cpp'")
        raise RuntimeError(f"Failed to build {'bitnet.cpp' if is_bitnet else 'llama.cpp'}")
    finally:
        os.chdir(HOME_DIR)
        shutil.rmtree(build_dir, ignore_errors=True)

def pull_model(repo_id: str, quant: str = "Q4_K_M", quiet: bool = True):
    init_config()
    model_info = model_map.get(repo_id, {"repo_id": repo_id, "filename": None, "chat_format": "chatml"})
    full_repo = model_info["repo_id"]
    filename = model_info.get("filename", f"{repo_id.split('/')[-1].lower()}-{quant.lower()}.gguf")
    model_dir = MODELS_DIR / full_repo.split('/')[-1]
    model_dir.mkdir(exist_ok=True)
    gguf_path = model_dir / filename

    if gguf_path.exists():
        return str(gguf_path), model_info.get("chat_format", "chatml")

    # Ensure appropriate binary
    ensure_llama_binary(repo_id, quiet=quiet)

    if not quiet:
        print(f"Downloading {full_repo} ({filename})...")
    try:
        hf_hub_download(repo_id=full_repo, filename=filename, local_dir=model_dir)
    except Exception as e:
        print(f"Failed to download {filename} from {full_repo}: {e}")
        print(f"Check the repo for available files: https://huggingface.co/{full_repo}/tree/main")
        print("Try a different model or quantization (e.g., Q4_0, Q5_K_M).")
        raise
    if not quiet:
        print("Download complete!")
    return str(gguf_path), model_info.get("chat_format", "chatml")

def list_models():
    """Return installed and available models with detailed metadata."""

    model_metadata = {
        "LFM2:700m": {"family": "lfm", "parameters": "742M", "quant": "Q4_K_M"},
        "LFM2:350m": {"family": "lfm", "parameters": "354M", "quant": "F16"},
        "LFM2:1.2b": {"family": "lfm", "parameters": "1.17B", "quant": "Q4_K_M"},
        "LFM2-VL:1.6b": {"family": "lfm", "parameters": "1.17B", "quant": "Q8_0"},
        "LFM2-VL:450m": {"family": "lfm", "parameters": "354M", "quant": "F16"},
        "LFM2:8b": {"family": "lfm", "parameters": "8.34B", "quant": "Q4_K_M"},
        "llama3.1:8b": {"family": "llama", "parameters": "8.0B", "quant": "Q4_K_M"},
        "llama3.2:3b": {"family": "llama", "parameters": "3.2B", "quant": "Q4_K_M"},
        "llama3.2:1b": {"family": "llama", "parameters": "1.2B", "quant": "Q4_K_M"},
        "tinyllama": {"family": "llama", "parameters": "1.1B", "quant": "Q4_K_M"},
        "bitnet": {"family": "bitnet", "parameters": "1.58B", "quant": "Q4_K_M"},
        "deepseek-r1:1.5b": {"family": "qwen", "parameters": "1.5B", "quant": "Q4_K_M"},
        "deepseek-r1:7b": {"family": "qwen", "parameters": "7.0B", "quant": "Q4_K_M"},
        "phi3": {"family": "phi", "parameters": "3.8B", "quant": "Q4_K_M"},
        "phi4-mini": {"family": "phi", "parameters": "3.8B", "quant": "Q4_K_M"},
        "llama3": {"family": "llama", "parameters": "8.0B", "quant": "Q4_K_M"},
        "mistral": {"family": "llama", "parameters": "7.2B", "quant": "Q4_K_M"},
        "gemma2:2b": {"family": "gemma", "parameters": "2.0B", "quant": "Q4_K_M"},
        "gemma3:270m": {"family": "gemma", "parameters": "270M", "quant": "Q4_K_M"},
        "gemma3:1b": {"family": "gemma", "parameters": "1.0B", "quant": "Q4_K_M"},
        "gemma3:4b": {"family": "gemma", "parameters": "4.0B", "quant": "Q4_K_M"},
        "gemma3n:e4b": {"family": "gemma", "parameters": "4.0B", "quant": "Q4_K_M"},
        "gemma3n:e2b": {"family": "gemma", "parameters": "2.0B", "quant": "Q4_K_M"},
        "qwen3:0.6b": {"family": "qwen", "parameters": "0.6B", "quant": "Q4_K_M"},
        "qwen3:1.7b": {"family": "qwen", "parameters": "1.7B", "quant": "Q4_K_M"},
        "qwen3:4b": {"family": "qwen", "parameters": "4.0B", "quant": "Q4_K_M"},
        "qwen3:8b": {"family": "qwen", "parameters": "8.0B", "quant": "Q4_K_M"},
        "qwen2:0.5b": {"family": "qwen", "parameters": "0.5B", "quant": "Q4_K_M"},
        "qwen2.5-coder:0.5b": {"family": "qwen", "parameters": "0.5B", "quant": "Q4_K_M"},
        "qwen2.5-coder:1.5b": {"family": "qwen", "parameters": "1.5B", "quant": "Q4_K_M"},
        "qwen2.5-coder:3b": {"family": "qwen", "parameters": "3.0B", "quant": "Q4_K_M"},
        "qwen2.5-coder:7b": {"family": "qwen", "parameters": "7.0B", "quant": "Q4_K_M"},
        "qwen2.5:3b": {"family": "qwen", "parameters": "3.0B", "quant": "Q4_K_M"},
        "qwen2.5:7b": {"family": "qwen", "parameters": "7.0B", "quant": "Q4_K_M"},
    }

    installed = []
    for model_dir in MODELS_DIR.iterdir():
        if model_dir.is_dir():
            ggufs = list(model_dir.glob("*.gguf"))
            if ggufs:
                gguf_path = ggufs[0]
                # Match model name exactly to model_metadata key
                model_name = next((k for k in model_metadata if gguf_path.parent.name in model_map.get(k, {}).get('repo_id', '')), gguf_path.parent.name)
                metadata = model_metadata.get(model_name, {"family": "unknown", "parameters": "unknown", "quant": gguf_path.name.split('.')[-2]})
                installed.append({
                    "name": model_name,
                    "size": f"{gguf_path.stat().st_size / (1024**3):.1f} GB",
                    "modified_at": datetime.fromtimestamp(gguf_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "format": "gguf",
                    "family": metadata["family"],
                    "parameters": metadata["parameters"],
                    "quant": metadata["quant"],
                })

    available = [
        {"name": k, "repo_id": v["repo_id"], "quant": model_metadata[k]["quant"], "size": v["size"]} for k, v in {
            "LFM2:700m": {"repo_id": "LiquidAI/LFM2-700M-GGUF", "size": "0.4 GB"},
            "LFM2:350m": {"repo_id": "LiquidAI/LFM2-350M-Extract-GGUF", "size": "711 MB"},
            "LFM2:1.2b": {"repo_id": "LiquidAI/LFM2-1.2B-RAG-GGUF", "size": "731 MB"},
            "LFM2-VL:1.6b": {"repo_id": "LiquidAI/LFM2-VL-1.6B-GGUF", "size": "1.25 GB"},
            "LFM2-VL:450m": {"repo_id": "LiquidAI/LFM2-VL-450M-GGUF", "size": "711 MB"},
            "LFM2:8b": {"repo_id": "LiquidAI/LFM2-8B-A1B-GGUF", "size": "5.04 GB"},
            "llama3.1:8b": {"repo_id": "unsloth/Llama-3.1-8B-Instruct-GGUF", "size": "4.7 GB"},
            "llama3.2:3b": {"repo_id": "unsloth/Llama-3.2-3B-Instruct-GGUF", "size": "1.8 GB"},
            "llama3.2:1b": {"repo_id": "unsloth/Llama-3.2-1B-Instruct-GGUF", "size": "0.8 GB"},
            "tinyllama": {"repo_id": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF", "size": "0.6 GB"},
            "bitnet": {"repo_id": "microsoft/bitnet-b1.58-2B-4T-gguf", "size": "1.2 GB"},
            "deepseek-r1:1.5b": {"repo_id": "unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF", "size": "0.9 GB"},
            "deepseek-r1:7b": {"repo_id": "unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF", "size": "4.1 GB"},
            "phi3": {"repo_id": "microsoft/Phi-3-mini-4k-instruct-gguf", "size": "2.3 GB"},
            "phi4-mini": {"repo_id": "unsloth/Phi-4-mini-reasoning-GGUF", "size": "2.1 GB"},
            "llama3": {"repo_id": "bartowski/Meta-Llama-3-8B-Instruct-GGUF", "size": "4.7 GB"},
            "mistral": {"repo_id": "TheBloke/Mistral-7B-Instruct-v0.1-GGUF", "size": "4.1 GB"},
            "gemma2:2b": {"repo_id": "unsloth/gemma-2-it-GGUF", "size": "1.2 GB"},
            "gemma3:270m": {"repo_id": "unsloth/gemma-3-270m-it-GGUF", "size": "0.2 GB"},
            "gemma3:1b": {"repo_id": "unsloth/gemma-3-1b-it-GGUF", "size": "0.6 GB"},
            "gemma3:4b": {"repo_id": "unsloth/gemma-3-4b-it-GGUF", "size": "2.3 GB"},
            "gemma3n:e4b": {"repo_id": "unsloth/gemma-3n-E4B-it-GGUF", "size": "2.1 GB"},
            "gemma3n:e2b": {"repo_id": "unsloth/gemma-3n-E2B-it-GGUF", "size": "1.1 GB"},
            "qwen3:0.6b": {"repo_id": "unsloth/Qwen3-0.6B-GGUF", "size": "0.4 GB"},
            "qwen3:1.7b": {"repo_id": "unsloth/Qwen3-1.7B-GGUF", "size": "1.0 GB"},
            "qwen3:4b": {"repo_id": "unsloth/Qwen3-4B-GGUF", "size": "2.3 GB"},
            "qwen3:8b": {"repo_id": "unsloth/Qwen3-ts-GGUF", "size": "4.7 GB"},
            "qwen2:0.5b": {"repo_id": "Qwen/Qwen2-0.5B-Instruct-GGUF", "size": "0.3 GB"},
            "qwen2.5-coder:0.5b": {"repo_id": "unsloth/Qwen2.5-Coder-0.5B-Instruct-GGUF", "size": "0.3 GB"},
            "qwen2.5-coder:1.5b": {"repo_id": "unsloth/Qwen2.5-Coder-1.5B-Instruct-GGUF", "size": "0.9 GB"},
            "qwen2.5-coder:3b": {"repo_id": "unsloth/Qwen2.5-Coder-3B-Instruct-GGUF", "size": "1.8 GB"},
            "qwen2.5-coder:7b": {"repo_id": "unsloth/Qwen2.5-Coder-7B-Instruct-GGUF", "size": "4.1 GB"},
            "qwen2.5:3b": {"repo_id": "unsloth/Qwen2.5-VL-3B-Instruct-GGUF", "size": "1.8 GB"},
            "qwen2.5:7b": {"repo_id": "unsloth/Qwen2.5-VL-7B-Instruct-GGUF", "size": "4.1 GB"},
        }.items()
    ]

    return {"installed": installed, "available": available}

def remove_model(repo_id: str):
    """Remove a model by name, finding the actual directory."""
    # First try to find the model in our model_map to get the repo_id
    model_info = model_map.get(repo_id)
    if model_info:
        # Use the repo_id from model_map
        repo_id = model_info["repo_id"]
    
    # Try different possible directory names
    possible_dirs = [
        MODELS_DIR / repo_id.split('/')[-1],  # Original logic
        MODELS_DIR / repo_id.replace('/', '-'),  # Replace / with -
    ]
    
    # Also try to find by model name in installed models
    installed_models = list_models()['installed']
    for model in installed_models:
        if model['name'] == repo_id:
            # Find the actual directory by looking for GGUF files
            for model_dir in MODELS_DIR.iterdir():
                if model_dir.is_dir() and list(model_dir.glob("*.gguf")):
                    # Check if this matches our model
                    gguf_files = list(model_dir.glob("*.gguf"))
                    if gguf_files:
                        possible_dirs.append(model_dir)
                        break
    
    # Try to remove any matching directory
    removed = False
    for model_dir in possible_dirs:
        if model_dir.exists():
            shutil.rmtree(model_dir)
            print(f"Removed {model_dir.name}.")
            removed = True
            break
    
    if not removed:
        print(f"Model {repo_id} not found.")
        print("Available models:")
        for model in installed_models:
            print(f"  - {model['name']}")