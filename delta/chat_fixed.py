import subprocess
import json
import uuid
import platform
import sys
import os
from pathlib import Path
from datetime import datetime
from .models import ensure_llama_binary, HOME_DIR

HISTORY_FILE = HOME_DIR / "chat_history.json"

def save_history(session_id, messages):
    """Save chat session to history file."""
    history = load_history()
    history.append({"id": session_id, "messages": messages, "timestamp": datetime.now().isoformat()})
    with HISTORY_FILE.open('w') as f:
        json.dump(history, f, indent=2)

def load_history():
    """Load chat history from file."""
    if HISTORY_FILE.exists():
        with HISTORY_FILE.open('r') as f:
            return json.load(f)
    return []

def run_chat(model_path: str, chat_format: str, flags: list):
    """Run interactive chat session with the specified model."""
    binary_name = "bitnet-main" if "bitnet" in model_path else "llama-main"
    if platform.system() == "Windows":
        binary_name += ".exe"
    binary_path = ensure_llama_binary("bitnet" if "bitnet" in model_path else None)
    
    # Construct command with simplified arguments for compatibility
    cmd = [str(binary_path), "-m", str(model_path), "-i"]  # -i for interactive mode
    
    # Handle chat format - use compatible arguments
    if chat_format == "chatml":
        cmd.append("--chatml")
    elif chat_format == "llama3":
        # llama3 format is the default, no special argument needed
        pass
    elif chat_format == "llama2":
        # llama2 format is also default, no special argument needed
        pass
    elif chat_format != "default" and chat_format not in ["llama3", "llama2"]:
        # Only add format for non-default formats that are supported
        cmd.append(f"--prompt-format={chat_format}")
    
    cmd.extend([f for f in flags if f])  # Only include non-empty flags
    
    session_id = str(uuid.uuid4())
    messages = []
    
    print(f"Starting chat with model: {model_path}")
    print(f"Command: {' '.join(cmd)}")
    print("Type your message and press Enter. Type 'exit' to quit.")
    
    try:
        # For interactive mode, we need to pass through stdin/stdout/stderr
        # This allows the llama.cpp binary to run in true interactive mode
        process = subprocess.Popen(
            cmd,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )
        
        # Wait for the process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\nChat session ended.")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"Error running chat: {e}")
    
    # Save session to history
    if messages:
        save_history(session_id, messages)
