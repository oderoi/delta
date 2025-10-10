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

HOME_DIR = Path.home() / ".delta"
MODELS_DIR = HOME_DIR / "models"
BIN_DIR = HOME_DIR / "bin"
CONFIG_FILE = HOME_DIR / "config.json"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
BIN_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = "qwen2:0.5b"

def init_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps({"default_model": DEFAULT_MODEL}))

def ensure_llama_binary():
    """Ensure llama.cpp binary is available, preferring brew on supported platforms."""
    binary_name = "llama-main" if platform.system() != "Windows" else "llama-main.exe"
    binary_path = BIN_DIR / binary_name
    if binary_path.exists():
        print(f"llama.cpp binary found at {binary_path}")
        return binary_path

    # Prefer brew if available on macOS or Linux
    if shutil.which("brew"):
        try:
            # Check if llama.cpp is installed
            subprocess.run(["brew", "list", "llama.cpp"], check=True, capture_output=True, text=True)
            print("llama.cpp is already installed via brew")
        except subprocess.CalledProcessError:
            print("Installing llama.cpp via brew...")
            subprocess.run(["brew", "install", "llama.cpp"], check=True, capture_output=True, text=True)
            print("llama.cpp installed via brew")
        # Use brew-installed binary (llama-cli)
        brew_bin = shutil.which("llama-cli")
        if brew_bin:
            print(f"Using brew-installed llama-cli at {brew_bin}")
            return Path(brew_bin)
        else:
            print("brew install succeeded, but llama-cli not found. Falling back to build from source.")
    else:
        print("brew not found. Falling back to build from source.")

    # Build from source if brew not available or failed
    print(f"Building llama.cpp binary from source for {platform.system()}...")
    build_dir = HOME_DIR / "llama.cpp"
    repo_url = "https://github.com/ggerganov/llama.cpp.git"

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
        raise RuntimeError(f"Cannot build llama.cpp: missing {', '.join(missing_tools)}")

    # Clone llama.cpp repository
    if build_dir.exists():
        shutil.rmtree(build_dir)
    try:
        subprocess.run(["git", "clone", repo_url, str(build_dir)], check=True, capture_output=True, text=True)
        print(f"Cloned llama.cpp to {build_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone llama.cpp: {e.stderr}")
        raise RuntimeError("Failed to clone llama.cpp repository")

    # Build llama.cpp using CMake
    try:
        os.chdir(build_dir)
        build_subdir = build_dir / "build"
        build_subdir.mkdir(exist_ok=True)
        os.chdir(build_subdir)
        # Configure CMake
        cmake_args = ["cmake", ".."]
        if platform.system() == "Darwin":
            cmake_args.extend([
                "-DCMAKE_C_COMPILER=clang",
                "-DCMAKE_CXX_COMPILER=clang++",
                "-DLLAMA_METAL=ON",
                "-DLLAMA_BUILD_SERVER=ON",
                "-DCMAKE_APPLE_SILICON_PROCESSOR=arm64",
                "-DLLAMA_METAL_MACOSX_VERSION_MIN=13.0",
                "-DCMAKE_EXE_LINKER_FLAGS=-framework Metal -framework Foundation -stdlib=libc++",
                "-DCMAKE_CXX_FLAGS=-stdlib=libc++"
            ])
        subprocess.run(cmake_args, check=True, capture_output=True, text=True)
        # Build
        if platform.system() == "Windows":
            subprocess.run(["cmake", "--build", ".", "--config", "Release"], check=True, capture_output=True, text=True)
            binary_source = build_subdir / "Release" / "main.exe"
            if not binary_source.exists():
                binary_source = build_subdir / "main.exe"
        else:
            subprocess.run(["make"], check=True, capture_output=True, text=True)
            binary_source = build_dir / "main"
        
        if not binary_source.exists():
            raise FileNotFoundError("Build succeeded but 'main' binary not found")
        
        # Copy and set permissions
        shutil.copy(binary_source, binary_path)
        if platform.system() != "Windows":
            binary_path.chmod(0o755)
        print(f"llama.cpp binary built and installed to {binary_path}")
        return binary_path
    except subprocess.CalledProcessError as e:
        print(f"Failed to build llama.cpp: {e.stderr}")
        if platform.system() == "Darwin":
            print("This may be due to missing Metal framework or C++ standard library.")
            print("Ensure Xcode Command Line Tools are installed: 'xcode-select --install'")
            print("Or install dependencies via Homebrew: 'brew install llvm'")
            print("If using Homebrew LLVM, update PATH: 'export PATH=\"/opt/homebrew/opt/llvm/bin:$PATH\"'")
            print("Then rerun 'delta setup'")
        raise RuntimeError("Failed to build llama.cpp")
    finally:
        # Clean up
        os.chdir(HOME_DIR)
        shutil.rmtree(build_dir, ignore_errors=True)

def pull_model(repo_id: str, quant: str = "Q4_K_M"):
    init_config()
    model_map = {
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
            "requires_special": True  # Needs bitnet.cpp
        },
        "deepseek-r1:1.5b": {
            "repo_id": "unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
            "filename": "DeepSeek-R1-Distill-Qwen-1.5B-Q4_K_M.gguf",
            "chat_format": "chatml"
        },
        "deepseek-r1:7b": {
            "repo_id": "unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF",
            "filename": "DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf",
            "chat_format": "chatml"
        },
        "phi3": {
            "repo_id": "microsoft/Phi-3-mini-4k-instruct-gguf",
            "filename": "Phi-3-mini-4k-instruct-q4.gguf",
            "chat_format": "chatml"
        },
        "phi4-mini": {
            "repo_id": "unsloth/Phi-4-mini-reasoning-GGUF",
            "filename": "Phi-4-mini-reasoning-Q4_K_M.gguf",
            "chat_format": "chatml"
        },
        "llama3": {
            "repo_id": "bartowski/Meta-Llama-3-8B-Instruct-GGUF",
            "filename": "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
            "chat_format": "llama3"
        },
        "mistral": {
            "repo_id": "TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
            "filename": "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            "chat_format": "chatml"
        },
        "gemma2:2b": {
            "repo_id": "unsloth/gemma-2-it-GGUF",
            "filename": "gemma-2-2b-it.q4_k_m.gguf",
            "chat_format": "chatml"
        },
        "gemma3:270m": {
            "repo_id": "unsloth/gemma-3-270m-it-GGUF",
            "filename": "gemma-3-270m-it-Q4_K_M.gguf",
            "chat_format": "chatml"
        },
        "gemma3:1b": {
            "repo_id": "unsloth/gemma-3-1b-it-GGUF",
            "filename": "gemma-3-1b-it-Q4_K_M.gguf",
            "chat_format": "chatml"
        },
        "gemma3:4b": {
            "repo_id": "unsloth/gemma-3-4b-it-GGUF",
            "filename": "gemma-3-4b-it-Q4_K_M.gguf",
            "chat_format": "chatml"
        },
        "gemma3n:e4b": {
            "repo_id": "unsloth/gemma-3n-E4B-it-GGUF",
            "filename": "gemma-3n-E4B-it-Q4_K_M.gguf",
            "chat_format": "chatml"
        },
        "gemma3n:e2b": {
            "repo_id": "unsloth/gemma-3n-E2B-it-GGUF",
            "filename": "gemma-3n-E2B-it-Q4_K_M.gguf",
            "chat_format": "chatml"
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
            "filename": "Qqwen2-0_5b-instruct-q4_k_m.gguf",
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
    model_info = model_map.get(repo_id, {"repo": repo_id, "filename": None})
    full_repo = model_info["repo"]
    filename = model_info.get("filename", f"{repo_id.split('/')[-1].lower()}-{quant.lower()}.gguf")
    model_dir = MODELS_DIR / full_repo.split('/')[-1]
    model_dir.mkdir(exist_ok=True)
    gguf_path = model_dir / filename

    if gguf_path.exists():
        print(f"Model {repo_id} already exists.")
        return str(gguf_path)

    print(f"Downloading {full_repo} ({filename})...")
    try:
        hf_hub_download(repo_id=full_repo, filename=filename, local_dir=model_dir)
    except Exception as e:
        print(f"Failed to download {filename} from {full_repo}: {e}")
        print("Check the repo for available files: https://huggingface.co/{full_repo}/tree/main")
        print("Try a different model or quantization (e.g., Q4_0, Q5_K_M).")
        raise
    print("Download complete!")
    return str(gguf_path)

def list_models():
    """Return installed and available models with detailed metadata."""
    # Model metadata map
    model_metadata = {
        "llama3.1:8b": {
            "family": "llama",
            # "parameters": "8.0B",
            "quant": "Q4_K_M"
        },
        "llama3.2:3b": {
            "family": "llama",
            # "parameters": "3.2B",
            "quant": "Q4_K_M"
        },
        "llama3.2:1b": {
            "family": "llama",
            # "parameters": "1.2B",
            "quant": "Q4_K_M"
        },
        "tinyllama": {
            "family": "llama",
            # "parameters": "8.1B",
            "quant": "Q4_K_M"
        },
        "bitnet": {
            "family": "bitnet",
            # "parameters": "1.19B",
            "quant": "Q4_K_M"
        },
        "deepseek-r1:1.5b": {
            "family": "qwen",
            # "parameters": "1.78B",
            "quant": "Q4_K_M"
        },
        "deepseek-r1:7b": {
            "family": "qwen",
            # "parameters": "7.62B",
            "quant": "Q4_K_M"
        },
        "phi3": {
            "family": "phi",
            # "parameters": "3.82B",
            "quant": "Q4_K_M"
        },
        "phi4-mini": {
            "family": "phi",
            # "parameters": "3.84B",
            "quant": "Q4_K_M"
        },
        "llama3": {
            "family": "llama",
            # "parameters": "8.03B",
            "quant": "Q4_K_M"
        },
        "mistral": {
            "family": "llama",
            # "parameters": "7.24B",
            "quant": "Q4_K_M"
        },
        "gemma2:2b": {
            "family": "gemma",
            # "parameters": "2.61B",
            "quant": "Q4_K_M"
        },
        "gemma3:270m": {
            "family": "gemma",
            # "parameters": "268M",
            "quant": "Q4_K_M"
        },
        "gemma3:1b": {
            "family": "gemma",
            # "parameters": "674M",
            "quant": "Q4_K_M"
        },
        "gemma3:4b": {
            "family": "gemma",
            # "parameters": "3.88B",
            "quant": "Q4_K_M"
        },
        "gemma3n:e4b": {
            "family": "gemma",
            # "parameters": "6.87B",
            "quant": "Q4_K_M"
        },
        "gemma3n:e2b": {
            "family": "gemma",
            # "parameters": "4.46B",
            "quant": "Q4_K_M"
        },
        "qwen3:0.6b": {
            "family": "qwen",
            # "parameters": "392M",
            "quant": "Q4_K_M"
        },
        "qwen3:1.7b": {
            "family": "qwen",
            # "parameters": "1.72B",
            "quant": "Q4_K_M"
        },
        "qwen3:4b": {
            "family": "qwen",
            # "parameters": "4.02B",
            "quant": "Q4_K_M"
        },
        "qwen3:8b": {
            "family": "qwen",
            # "parameters": "8.19B",
            "quant": "Q4_K_M"
        },
        "qwen2:0.5b": {
            "family": "qwen",
            # "parameters": "494B",
            "quant": "Q4_K_M"
        },
        "qwen2.5-coder:0.5b": {
            "family": "qwen",
            # "parameters": "494M",
            "quant": "Q4_K_M"
        },
        "qwen2.5-coder:1.5b": {
            "family": "qwen",
            # "parameters": "1.54B",
            "quant": "Q4_K_M"
        },
        "qwen2.5-coder:3b": {
            "family": "qwen",
            # "parameters": "3.09B",
            "quant": "Q4_K_M"
        },
        "qwen2.5-coder:7b": {
            "family": "qwen",
            # "parameters": "7.62B",
            "quant": "Q4_K_M"
        },
        "qwen2.5:3b": {
            "family": "qwen",
            # "parameters": "3.09B",
            "quant": "Q4_K_M"
        },
        "qwen2.5:7b": {
            "family": "qwen",
            # "parameters": "7.62B",
            "quant": "Q4_K_M"
        },
    }

    # Installed models
    installed = []
    for model_dir in MODELS_DIR.iterdir():
        if model_dir.is_dir():
            ggufs = list(model_dir.glob("*.gguf"))
            if ggufs:
                gguf_path = ggufs[0]
                model_name = next((k for k, v in model_metadata.items() if gguf_path.parent.name in v.get('repo_id', k)), gguf_path.parent.name)
                metadata = model_metadata.get(model_name, {"family": "unknown", "parameters": "unknown", "quant": gguf_path.name.split('.')[-2]})
                installed.append({
                    "name": model_name,
                    "size": f"{gguf_path.stat().st_size / (1024**3):.1f} GB",
                    "modified_at": datetime.fromtimestamp(gguf_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                    # "format": "gguf",
                    # "family": metadata["family"],
                    # "parameters": metadata["parameters"],
                    # "quant": metadata["quant"],
                })

    # Available models
    available = [
        {"name": k, "repo_id": v["repo"], "quant": model_metadata[k]["quant"]} for k, v in {
            "llama3.1:8b": {
        "repo": "unsloth/Llama-3.1-8B-Instruct-GGUF"
        },
        "llama3.2:3b": {
            "repo": "unsloth/Llama-3.2-3B-Instruct-GGUF"
        },
        "llama3.2:1b": {
            "repo": "unsloth/Llama-3.2-1B-Instruct-GGUF"
        },
        "tinyllama": {
            "repo": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
        },
        "bitnet": {
            "repo": "microsoft/bitnet-b1.58-2B-4T-gguf"
        },
        "deepseek-r1:1.5b": {
            "repo": "unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF"
        },
        "deepseek-r1:7b": {
            "repo": "unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF"
        },
        "phi3": {
            "repo": "microsoft/Phi-3-mini-4k-instruct-gguf"
        },
        "phi4-mini": {
            "repo": "unsloth/Phi-4-mini-reasoning-GGUF"
        },
        "llama3": {
            "repo": "bartowski/Meta-Llama-3-8B-Instruct-GGUF"
        },
        "mistral": {
            "repo": "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
        },
        "gemma2:2b": {
            "repo": "unsloth/gemma-2-it-GGUF"
        },
        "gemma3:270m": {
            "repo": "unsloth/gemma-3-270m-it-GGUF"
        },
        "gemma3:1b": {
            "repo": "unsloth/gemma-3-1b-it-GGUF"
        },
        "gemma3:4b": {
            "repo": "unsloth/gemma-3-4b-it-GGUF"
        },
        "gemma3n:e4b": {
            "repo": "unsloth/gemma-3n-E4B-it-GGUF"
        },
        "gemma3n:e2b": {
            "repo": "unsloth/gemma-3n-E2B-it-GGUF"
        },
        "qwen3:0.6b": {
            "repo": "unsloth/Qwen3-0.6B-GGUF"
        },
        "qwen3:1.7b": {
            "repo": "unsloth/Qwen3-1.7B-GGUF"
        },
        "qwen3:4b": {
            "repo": "unsloth/Qwen3-4B-GGUF"
        },
        "qwen3:8b": {
            "repo": "unsloth/Qwen3-8B-GGUF"
        },
        "qwen2:0.5b": {
            "repo": "Qwen/Qwen2-0.5B-Instruct-GGUF"
        },
        "qwen2.5-coder:0.5b": {
            "repo": "unsloth/Qwen2.5-Coder-0.5B-Instruct-GGUF"
        },
        "qwen2.5-coder:1.5b": {
            "repo": "unsloth/Qwen2.5-Coder-1.5B-Instruct-GGUF"
        },
        "qwen2.5-coder:3b": {
            "repo": "unsloth/Qwen2.5-Coder-3B-Instruct-GGUF"
        },
        "qwen2.5-coder:7b": {
            "repo": "unsloth/Qwen2.5-Coder-7B-Instruct-GGUF"
        },
        "qwen2.5:3b": {
            "repo": "unsloth/Qwen2.5-VL-3B-Instruct-GGUF"
        },
        "qwen2.5:7b": {
            "repo": "unsloth/Qwen2.5-VL-7B-Instruct-GGUF"
        },
        }.items()
    ]

    return {"installed": installed, "available": available}

def remove_model(repo_id: str):
    model_dir = MODELS_DIR / repo_id.split('/')[-1]
    if model_dir.exists():
        shutil.rmtree(model_dir)
        print(f"Removed {repo_id}.")
    else:
        print(f"Model {repo_id} not found.")