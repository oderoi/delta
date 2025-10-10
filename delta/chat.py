import subprocess
import json
from datetime import datetime
from pathlib import Path
import sys
import os
from .models import HOME_DIR, ensure_llama_binary

HISTORY_FILE = HOME_DIR / "history.json"

def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []

def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history, indent=2))

def prepend_search(query: str, flag: str = None):
    if flag == "--wiki":
        import wikipedia
        try:
            page = wikipedia.page(query)
            return f"Context from Wikipedia: {page.summary[:500]}...\n\nQuestion: {query}\nAnswer:"
        except:
            return f"Question: {query}\nAnswer:"
    elif flag == "--ddg":
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=1)]
            if results:
                return f"Context from DuckDuckGo: {results[0]['body'][:500]}...\n\nQuestion: {query}\nAnswer:"
            return f"Question: {query}\nAnswer:"
    elif flag.startswith("--docs"):
        doc_path = flag.split(' ', 1)[1] if len(flag.split()) > 1 else None
        if doc_path and doc_path.endswith('.pdf'):
            import PyPDF2
            with open(doc_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ''.join(page.extract_text() for page in reader.pages[:5])
                return f"Document summary: {text[:1000]}...\n\nQuery: Summarize or answer about this doc.\nResponse:"
        return f"Question: {query}\nAnswer:"
    return f"Question: {query}\nAnswer:"

def run_chat(model_path: str, flags: list):
    binary_path = ensure_llama_binary()
    history = load_history()
    session_id = datetime.now().isoformat()
    session = {"id": session_id, "messages": []}

    print("Delta Chat (Ctrl+C to exit, Ctrl+D or 'exit' to quit)")
    print(">" * 20)

    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input:
                continue

            # Prepend search if flag
            prompt = prepend_search(user_input, ' '.join(flags) if flags else None)
            prompt += f"\nUser: {user_input}\nAssistant:"

            # Run llama.cpp binary
            cmd = [
                str(binary_path),
                "-m", str(model_path),
                "--prompt", prompt,
                "--ctx-size", "2048",
                "--threads", str(os.cpu_count()),
                "--temp", "0.7",
                "--no-display-prompt",  # Cleaner output
                "--interactive",
                "--color",  # For colored output
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )

            response = ""
            print("Assistant: ", end="", flush=True)
            for line in process.stdout:
                if line.strip() and not line.startswith("["):  # Skip metadata
                    print(line, end="", flush=True)
                    response += line
            print("\n")
            process.terminate()

            # Save to history
            session["messages"].append({
                "user": user_input,
                "assistant": response.strip(),
                "timestamp": datetime.now().isoformat()
            })

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

    history.append(session)
    save_history(history)
    print("Session saved to history.")