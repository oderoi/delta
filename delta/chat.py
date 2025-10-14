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

def run_chat(model_path: str, chat_format: str = "default", flags: list | None = None):
    """Run interactive chat session with the specified model."""
    binary_name = "bitnet-main" if "bitnet" in model_path else "llama-main"
    if platform.system() == "Windows":
        binary_name += ".exe"
    binary_path = ensure_llama_binary("bitnet" if "bitnet" in model_path else None)
    
    # Construct command with simplified arguments for compatibility
    cmd = [str(binary_path), "-m", str(model_path), "-i"]  # -i for interactive mode
    # Suppress startup output but keep it simple
    cmd.extend(["--no-display-prompt", "--no-warmup"])
    
    # Handle chat format - use compatible arguments
    if chat_format in ["llama3", "llama2"]:
        # llama3/llama2 format is the default, no special argument needed
        pass
    elif chat_format in ["chatml", "gemma", "phi3", "phi4", "deepseek", "mistral-v1", "mistral-v3"]:
        # Use supported chat templates
        cmd.append("--chat-template")
        cmd.append(chat_format)
    elif chat_format != "default":
        # For any other supported format, try it
        cmd.append("--chat-template")
        cmd.append(chat_format)
    
    if flags is None:
        flags = []
    cmd.extend([f for f in flags if f])  # Only include non-empty flags
    
    session_id = str(uuid.uuid4())
    messages = []
    current_conversation = {"user": "", "assistant": ""}
    
    # No preamble; start directly at prompt
    
    try:
        # Manage stdin ourselves so we can intercept 'exit' and terminate
        print("> ", end="", flush=True)

        # Use a simpler approach - let llama.cpp handle everything
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,  # We control stdin to detect 'exit'
            stdout=None,            # Let stdout go to terminal for responses
            stderr=None,            # Let stderr go to terminal (startup noise will show)
            text=True,
            bufsize=1
        )

        # Simple REPL loop: forward user input to llama.cpp, intercept exit
        while True:
            try:
                user_input = input().strip()
            except EOFError:
                # End of input (e.g., Ctrl+D) -> terminate
                break

            if user_input.lower() in {"exit", "quit", "q"}:
                print("Exiting chat...")
                break

            if process.poll() is not None:
                # Process ended unexpectedly
                break

            if process.stdin is not None:
                # Store user input for history
                current_conversation["user"] = user_input
                process.stdin.write(user_input + "\n")
                process.stdin.flush()
                print("> ", end="", flush=True)

        # Gracefully terminate the subprocess
        if process.poll() is None:
            try:
                process.terminate()
            except Exception:
                pass
            try:
                process.wait(timeout=5)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass

    except KeyboardInterrupt:
        print("\nChat session ended.")
        try:
            if 'process' in locals() and process and process.poll() is None:
                process.terminate()
        except Exception:
            pass
    except Exception as e:
        print(f"Error running chat: {e}")

    # Save session to history (even if empty, so exits are logged)
    if current_conversation["user"]:
        messages.append(current_conversation)
    save_history(session_id, messages)
