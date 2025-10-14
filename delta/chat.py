import subprocess
import json
import uuid
import platform
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from .models import ensure_llama_binary, HOME_DIR

HISTORY_FILE = HOME_DIR / "chat_history.json"
SETTINGS_FILE = HOME_DIR / "chat_session_settings.json"

def load_settings() -> dict:
    defaults = {
        "system_message": None,
        "history_enabled": True,
        "wordwrap_enabled": True,
        "json_mode": False,
        "verbose_stats": False,
        "think_enabled": False,
    }
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text())
            defaults.update({k: data.get(k, defaults[k]) for k in defaults})
        except Exception:
            pass
    return defaults

def save_settings(settings: dict) -> None:
    try:
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2))
    except Exception:
        pass

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
    settings = load_settings()
    binary_name = "bitnet-main" if "bitnet" in model_path else "llama-main"
    if platform.system() == "Windows":
        binary_name += ".exe"
    binary_path = ensure_llama_binary("bitnet" if "bitnet" in model_path else None)
    
    # Construct command with simplified arguments for compatibility
    cmd = [str(binary_path), "-m", str(model_path), "-i"]  # -i for interactive mode
    # Suppress startup output but keep it simple
    cmd.extend(["--no-display-prompt", "--no-warmup"])
    
    # Apply system message if persisted (applies for this session)
    if settings.get("system_message"):
        cmd.extend(["-sys", settings["system_message"]])
    
    # Handle chat format - use compatible arguments
    if chat_format in ["llama3", "llama2"]:
        pass
    elif chat_format in ["chatml", "gemma", "phi3", "phi4", "deepseek", "mistral-v1", "mistral-v3"]:
        cmd.append("--chat-template"); cmd.append(chat_format)
    elif chat_format != "default":
        cmd.append("--chat-template"); cmd.append(chat_format)
    
    if flags is None:
        flags = []
    cmd.extend([f for f in flags if f])  # Only include non-empty flags
    
    session_id = str(uuid.uuid4())
    messages: list[dict[str, str]] = []
    
    try:
        # POSIX PTY setup (for macOS/Linux) so interactive output is produced while we can filter it
        use_pty = platform.system() != "Windows"
        master_fd = None
        # Capture startup metadata from llama.cpp to support '/show' commands
        startup_meta: dict = {
            "architecture": None,
            "parameters": None,
            "context_length": None,
            "embedding_length": None,
            "quantization": None,
            "sampler": {},
            "template": None,
            "stop": None,
        }
        
        if use_pty:
            import pty, fcntl, termios
            master_fd, slave_fd = pty.openpty()
            # Disable ECHO on the slave to avoid local echoing of user input
            try:
                attrs = termios.tcgetattr(slave_fd)
                attrs[3] = attrs[3] & ~termios.ECHO  # lflag: turn off ECHO
                termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)
            except Exception:
                pass
            process = subprocess.Popen(
                cmd,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                text=False,  # raw bytes via PTY
                bufsize=0
            )
            os.close(slave_fd)
            # set master non-blocking
            fl = fcntl.fcntl(master_fd, fcntl.F_GETFL)
            fcntl.fcntl(master_fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        else:
            # Fallback: capture stdout (Windows)
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        
        # Regex helpers for parsing startup metadata
        arch_re = re.compile(r"print_info:\s*arch\s*=\s*(\S+)")
        params_re = re.compile(r"model params\s*=\s*([0-9.]+\s*[MkG]?)")
        ctx_train_re = re.compile(r"n_ctx_train\s*=\s*([0-9]+)")
        n_embd_re = re.compile(r"n_embd\s*=\s*([0-9]+)")
        filetype_re = re.compile(r"file type\s*=\s*([A-Za-z0-9_]+)")
        sampler_line_re = re.compile(r"\s*(top_k|top_p|temp(?:erature)?|typical_p|min_p)\s*=\s*([0-9.]+)")
        chat_template_re = re.compile(r"tokenizer\.chat_template\s+str\s*=\s*(.*)$")
        eot_re = re.compile(r"EOT token\s*=\s*\d+\s*'([^']+)'")

        def parse_meta_from_line(line: str) -> None:
            m = arch_re.search(line)
            if m:
                startup_meta["architecture"] = m.group(1)
            m = params_re.search(line)
            if m:
                startup_meta["parameters"] = m.group(1)
            m = ctx_train_re.search(line)
            if m:
                startup_meta["context_length"] = m.group(1)
            m = n_embd_re.search(line)
            if m:
                startup_meta["embedding_length"] = m.group(1)
            m = filetype_re.search(line)
            if m:
                startup_meta["quantization"] = m.group(1)
            m = sampler_line_re.search(line)
            if m:
                key = m.group(1)
                val = m.group(2)
                # Normalize temperature key
                if key.startswith("temp"):
                    key = "temperature"
                startup_meta["sampler"][key] = val
            m = chat_template_re.search(line)
            if m and startup_meta.get("template") is None:
                startup_meta["template"] = m.group(1).strip()
            m = eot_re.search(line)
            if m and startup_meta.get("stop") is None:
                startup_meta["stop"] = m.group(1)

        # Drain startup output until interactive mode is ready
        def _read_line() -> str:
            if use_pty:
                import select
                r, _, _ = select.select([master_fd], [], [], 0.2)
                if r:
                    try:
                        data = os.read(master_fd, 8192)
                        return data.decode(errors='ignore')
                    except OSError:
                        return ""
                return ""
            else:
                if process.stdout is None:
                    return ""
                try:
                    return process.stdout.readline()
                except Exception:
                    return ""
        
        try:
            while True:
                line = _read_line()
                if not line:
                    # keep draining until banner passes
                    continue
                # Parse metadata from startup lines
                try:
                    parse_meta_from_line(line)
                except Exception:
                    pass
                if "interactive mode on" in line or "== Running in interactive mode." in line:
                    break
        except Exception:
            pass

        # Placeholder-aware input reader (POSIX)
        def read_user_input() -> str:
            ph_text = "Send a message (/? for help)"
            prompt = ">>> "
            if platform.system() == "Windows":
                # Fallback: no dynamic placeholder on Windows
                print(prompt, end="", flush=True)
                try:
                    return input()
                except EOFError:
                    return ""
            # POSIX raw char input
            import sys as _sys
            import termios as _termios
            import tty as _tty
            _stdout = _sys.stdout
            _stdin = _sys.stdin
            faint_start = "\x1b[2m"  # ANSI faint (dim)
            faint_end = "\x1b[22m"    # ANSI normal intensity
            _stdout.write(prompt + faint_start + ph_text + faint_end)
            _stdout.flush()
            fd = _stdin.fileno()
            old = _termios.tcgetattr(fd)
            buf = []
            placeholder_visible = True
            try:
                _tty.setraw(fd)
                while True:
                    ch = _stdin.read(1)
                    if ch in ('\r', '\n'):
                        _stdout.write("\n")
                        _stdout.flush()
                        return ''.join(buf)
                    if placeholder_visible:
                        # clear placeholder on first keypress
                        _stdout.write("\x1b[{}D".format(len(ph_text)))  # move left
                        _stdout.write(" " * len(ph_text))               # clear
                        _stdout.write("\x1b[{}D".format(len(ph_text)))  # move back
                        _stdout.flush()
                        placeholder_visible = False
                    if ch in ('\x7f', '\b'):
                        if buf:
                            buf.pop()
                            _stdout.write("\b \b")
                            _stdout.flush()
                        continue
                    # ignore other control chars
                    if ord(ch) < 32 and ch not in ('\t',):
                        continue
                    buf.append(ch)
                    _stdout.write(ch)
                    _stdout.flush()
            finally:
                _termios.tcsetattr(fd, _termios.TCSADRAIN, old)

        # Helper: read model response until short inactivity timeout
        def read_response(current_user: str, timeout_seconds: float = 1.5, max_duration: float = 12.0):
            import select, time
            response_chunks: list[str] = []
            last_read = time.time()
            start_time = last_read
            first_token_time: float | None = None
            started_stream = False
            
            while True:
                line = ""
                if use_pty:
                    r, _, _ = select.select([master_fd], [], [], 0.2)
                    if r:
                        try:
                            data = os.read(master_fd, 8192)
                            line = data.decode(errors='ignore')
                        except OSError:
                            line = ""
                else:
                    if process.stdout is not None:
                        r, _, _ = select.select([process.stdout], [], [], 0.2)
                        if r:
                            try:
                                line = process.stdout.readline()
                            except Exception:
                                line = ""
                
                if line:
                    for raw in line.splitlines(True):
                        stripped = raw.strip()
                        lower = stripped.lower()
                        # Normalize helper to compare against user input robustly
                        def _strip_ansi(s: str) -> str:
                            return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", s)
                        def _norm(s: str) -> str:
                            s2 = _strip_ansi(s)
                            s2 = re.sub(r"[\s\t\n\r\v\f]+", "", s2)
                            s2 = re.sub(r"[^0-9a-zA-Z]+", "", s2)
                            return s2.lower()
                        norm_line = _norm(stripped)
                        norm_user = _norm(current_user)
                        if (
                            stripped == "" or
                            stripped == current_user or
                            lower == current_user.lower() or
                            stripped.lstrip() == current_user or
                            stripped.lstrip().lower() == current_user.lower() or
                            norm_line == norm_user or
                            (norm_line.startswith(norm_user) and len(norm_line) <= len(norm_user) + 2) or
                            lower.startswith("> ") or
                            lower.startswith("== running in interactive mode.") or
                            lower.startswith("main:") or
                            lower.startswith("system_info:") or
                            lower.startswith("sampler") or
                            lower.startswith("generate:") or
                            lower.startswith("repeat_last_n") or
                            lower.startswith("dry_multiplier") or
                            lower.startswith("top_k") or
                            lower.startswith("mirostat") or
                            lower.startswith("- press ctrl+c") or
                            lower.startswith("- press return") or
                            lower.startswith("- to return control") or
                            lower.startswith("- if you want to submit") or
                            lower.startswith("- not using system message") or
                            lower.startswith("llama_") or
                            lower.startswith("ggml_") or
                            # drop banner fragments regardless of prefix
                            "return control" in lower or
                            "end your input with '/'" in lower or
                            "if you want to submit another line" in lower or
                            "not using system message" in lower
                        ):
                            last_read = time.time()
                            continue
                        # If verbose stats are disabled, drop perf/statistic-looking lines
                        if not settings.get("verbose_stats", False):
                            if lower.startswith("llama_perf") or lower.startswith("llama_memory_breakdown"):
                                last_read = time.time();
                                continue
                        if first_token_time is None and stripped:
                            first_token_time = time.time()
                        # Stream print when first content token arrives; add a blank separator line before content
                        if not started_stream:
                            print("")
                            started_stream = True
                        # Avoid printing trailing '>' artifacts within a chunk if they appear at end
                        to_print = re.sub(r">\s*$", "", raw)
                        print(to_print, end="", flush=True)
                        response_chunks.append(raw)
                        last_read = time.time()
                else:
                    now = time.time()
                    if now - last_read >= timeout_seconds or now - start_time >= max_duration:
                        break
            text = ''.join(response_chunks).strip()
            # Final cleanup: strip any trailing '>' from aggregated text
            cleaned_text = re.sub(r"\s*>\s*$", "", text)
            # If we streamed any content, ensure a blank line separation after answer
            if started_stream:
                print("\n")
            end_time = time.time()
            meta = {
                "start_time": start_time,
                "first_token_time": first_token_time or end_time,
                "end_time": end_time,
                "duration": end_time - start_time,
                "bytes": len(cleaned_text.encode('utf-8')),
                "lines": cleaned_text.count('\n') + (1 if cleaned_text else 0),
            }
            return cleaned_text, meta

        # Helpers to render '/show' output blocks
        def render_show_root() -> None:
            print("Available Commands:\n  /set            Set session variables\n  /show           Show model information\n  /load <model>   Load a session or model\n  /save <model>   Save your current session\n  /clear          Clear session context\n  /bye            Exit\n  /?, /help       Help for a command\n  /? shortcuts    Help for keyboard shortcuts\n\nUse \"\"\" to begin a multi-line message.\n")

        def render_show_info() -> None:
            arch = startup_meta.get("architecture") or "unknown"
            params = startup_meta.get("parameters") or "unknown"
            ctx = startup_meta.get("context_length") or "unknown"
            emb = startup_meta.get("embedding_length") or "unknown"
            qtz = startup_meta.get("quantization") or "unknown"
            # Capabilities: assume completion for basic llama.cpp usage
            print("  Model\n"
                  f"    architecture        {arch:<12}\n"
                  f"    parameters          {params:<12}\n"
                  f"    context length      {ctx:<12}\n"
                  f"    embedding length    {emb:<12}\n"
                  f"    quantization        {qtz:<12}\n\n"
                  "  Capabilities\n"
                  "    completion    \n\n"
                  "  Parameters")
            sp = startup_meta.get("sampler", {})
            stop_tok = startup_meta.get("stop") or "n/a"
            temperature = sp.get("temperature", "n/a")
            top_k = sp.get("top_k", "n/a")
            top_p = sp.get("top_p", "n/a")
            print(f"\n    stop           \"{stop_tok}\"    \n"
                  f"    temperature    {temperature:<18}\n"
                  f"    top_k          {top_k:<18}\n"
                  f"    top_p          {top_p:<18}\n")

        def render_show_license() -> None:
            print("No license information is available for this model.\n")

        def render_show_modelfile() -> None:
            print("No Modelfile is available for this model.\n")

        def render_show_parameters() -> None:
            sp = startup_meta.get("sampler", {})
            top_k = sp.get("top_k", "n/a")
            top_p = sp.get("top_p", "n/a")
            temperature = sp.get("temperature", "n/a")
            stop_tok = startup_meta.get("stop") or "n/a"
            print("Model defined parameters:")
            print(f"  top_k                          {top_k}")
            print(f"  top_p                          {top_p}")
            print(f"  stop                           \"{stop_tok}\"")
            print(f"  temperature                    {temperature}\n")

        def render_show_system() -> None:
            if settings.get("system_message"):
                print(settings["system_message"] + "\n")
            else:
                print("No system message was specified for this model.\n")

        def render_show_template() -> None:
            if startup_meta.get("template"):
                print(startup_meta["template"] + "\n")
            else:
                print("No prompt template available.\n")

        # Simple REPL loop: forward user input to llama.cpp, intercept exit
        while True:
            try:
                user_input = read_user_input().strip()
            except EOFError:
                break
            
            # If user pressed Enter with no input, do nothing and keep the same prompt
            if user_input == "":
                continue
            
            # Slash commands (client-side)
            lower_cmd = user_input.lower()
            if lower_cmd in ("/?, /help",):
                print("Available Commands:\n  /set            Set session variables\n  /show           Show model information\n  /load <model>   Load a session or model\n  /save <model>   Save your current session\n  /clear          Clear session context\n  /bye            Exit\n  /?, /help       Help for a command\n  /? shortcuts    Help for keyboard shortcuts\n\nUse \"\"\" to begin a multi-line message.\n")
                continue
            if lower_cmd in ("/?,", "/?", "/help"):
                print("Available Commands:\n  /set            Set session variables\n  /show           Show model information\n  /load <model>   Load a session or model\n  /save <model>   Save your current session\n  /clear          Clear session context\n  /bye            Exit\n  /?, /help       Help for a command\n  /? shortcuts    Help for keyboard shortcuts\n\nUse \"\"\" to begin a multi-line message.\n")
                continue
            if lower_cmd.startswith("/? shortcuts"):
                print("Keyboard Shortcuts:\n  Enter         Send message\n  Ctrl+C        Interrupt generation\n  Ctrl+D        End input\n  /?            Help\n")
                continue
            if lower_cmd.startswith("/? set") or lower_cmd == "/? set":
                print("Available Commands:\n  /set parameter ...     Set a parameter\n  /set system <string>   Set system message\n  /set history           Enable history\n  /set nohistory         Disable history\n  /set wordwrap          Enable wordwrap\n  /set nowordwrap        Disable wordwrap\n  /set format json       Enable JSON mode\n  /set noformat          Disable formatting\n  /set verbose           Show LLM stats\n  /set quiet             Disable LLM stats\n  /set think             Enable thinking\n  /set nothink           Disable thinking\n")
                continue
            if lower_cmd.startswith("/show"):
                # /show root and subcommands
                parts = user_input.split()
                if len(parts) == 1:
                    # '/show'
                    print("Available Commands:\n  /show info         Show details for this model\n  /show license      Show model license\n  /show modelfile    Show Modelfile for this model\n  /show parameters   Show parameters for this model\n  /show system       Show system message\n  /show template     Show prompt template\n")
                    continue
                sub = parts[1].lower()
                if sub == "info":
                    render_show_info(); continue
                if sub == "license":
                    render_show_license(); continue
                if sub == "modelfile":
                    render_show_modelfile(); continue
                if sub == "parameters":
                    render_show_parameters(); continue
                if sub == "system":
                    render_show_system(); continue
                if sub == "template":
                    render_show_template(); continue
                print("> Invalid /show usage. Try '/show'.\n"); continue

            if lower_cmd.strip() == "/set":
                print("Available Commands:\n  /set parameter ...     Set a parameter\n  /set system <string>   Set system message\n  /set history           Enable history\n  /set nohistory         Disable history\n  /set wordwrap          Enable wordwrap\n  /set nowordwrap        Disable wordwrap\n  /set format json       Enable JSON mode\n  /set noformat          Disable formatting\n  /set verbose           Show LLM stats\n  /set quiet             Disable LLM stats\n  /set think             Enable thinking\n  /set nothink           Disable thinking\n")
                continue

            if lower_cmd.startswith("/set "):
                # Parse set commands
                parts = user_input.split()
                if len(parts) >= 2:
                    sub = parts[1].lower()
                    if sub == "system":
                        new_msg = user_input[user_input.lower().find("system") + len("system"):].strip()
                        settings["system_message"] = new_msg or None
                        save_settings(settings)
                        print("> System message updated. It will apply the next time you start a session.\n")
                        continue
                    if sub == "history":
                        settings["history_enabled"] = True; save_settings(settings)
                        print("> History enabled.\n"); continue
                    if sub == "nohistory":
                        settings["history_enabled"] = False; save_settings(settings)
                        print("> History disabled.\n"); continue
                    if sub == "wordwrap":
                        settings["wordwrap_enabled"] = True; save_settings(settings)
                        print("> Wordwrap enabled.\n"); continue
                    if sub == "nowordwrap":
                        settings["wordwrap_enabled"] = False; save_settings(settings)
                        print("> Wordwrap disabled.\n"); continue
                    if sub == "format" and len(parts) >= 3:
                        mode = parts[2].lower()
                        if mode == "json":
                            settings["json_mode"] = True; save_settings(settings)
                            print("> JSON mode enabled.\n"); continue
                    if sub == "noformat":
                        settings["json_mode"] = False; save_settings(settings)
                        print("> Formatting disabled.\n"); continue
                    if sub == "verbose":
                        settings["verbose_stats"] = True; save_settings(settings)
                        print("> Verbose stats enabled.\n"); continue
                    if sub == "quiet":
                        settings["verbose_stats"] = False; save_settings(settings)
                        print("> Verbose stats disabled.\n"); continue
                    if sub == "think":
                        settings["think_enabled"] = True; save_settings(settings)
                        print("> Thinking enabled.\n"); continue
                    if sub == "nothink":
                        settings["think_enabled"] = False; save_settings(settings)
                        print("> Thinking disabled.\n"); continue
                    # generic parameter setter: /set parameter key value
                    if sub == "parameter" and len(parts) >= 4:
                        key = parts[2]
                        val = " ".join(parts[3:])
                        settings[key] = val
                        save_settings(settings)
                        print(f"> Parameter '{key}' set.\n"); continue
                print("> Invalid /set usage. Try '/? set'.\n")
                continue
            if lower_cmd in ("/bye", "/exit"):
                print("Exiting chat...")
                break
            
            if user_input.lower() in {"exit", "quit", "q"}:
                print("Exiting chat...")
                break
            
            if process.poll() is not None:
                break
            
            # Compose message according to settings
            send_text = user_input
            if settings.get("think_enabled"):
                send_text = send_text + "\nLet's think step by step."
            if settings.get("json_mode"):
                send_text = send_text + "\nPlease respond in strict JSON format without additional commentary."
            
            if use_pty:
                os.write(master_fd, (send_text + "\n").encode())
            else:
                if process.stdin is None:
                    break
                process.stdin.write(send_text + "\n")
                process.stdin.flush()
            
            # Read model response and print while capturing
            assistant_text, meta = read_response(user_input)
            
            if (settings.get("history_enabled", True)) and (user_input or assistant_text):
                messages.append({"user": user_input, "assistant": assistant_text})
            
            # Optional verbose stats
            if settings.get("verbose_stats", False):
                total_s = meta.get("duration", 0.0)
                load_s = 0.0  # unknown here; we only measure per-turn
                first_token_latency = max(0.0, (meta.get("first_token_time", meta.get("end_time", 0)) - meta.get("start_time", 0)))
                # Token count/rate are not available without a tokenizer; approximate by words
                word_count = len(assistant_text.split()) if assistant_text else 0
                eval_count = word_count
                eval_rate = (eval_count / max(1e-6, total_s)) if total_s > 0 else 0.0
                print(f"total duration:       {total_s:.9f}s")
                print(f"load duration:        {load_s*1000:.6f}ms")
                print(f"first token latency:  {first_token_latency*1000:.6f}ms")
                print(f"eval count:           {eval_count} token(s)")
                print(f"eval duration:        {total_s:.9f}s")
                print(f"eval rate:            {eval_rate:.2f} tokens/s")
            
            # Next loop iteration will render the prompt via read_user_input()
        
    except KeyboardInterrupt:
        print("\nChat session ended.")
        try:
            if 'process' in locals() and process and process.poll() is None:
                process.terminate()
        except Exception:
            pass
    except Exception as e:
        print(f"Error running chat: {e}")
    
    # Save session to history
    if settings.get("history_enabled", True):
        save_history(session_id, messages)
