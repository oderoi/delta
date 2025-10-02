#!/usr/bin/env python3

import argparse
from rich.console import Console
from functools import lru_cache
import time
import random
import sys
import threading
import os
from pathlib import Path
import shutil
import subprocess
import sysconfig
import PyPDF2
from docx import Document
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
import pyperclip
import pynvml
import psutil
import cpuinfo
import re
from difflib import SequenceMatcher

# Initialize rich console
console = Console()

# In-memory query history for personalization
query_history = []
query_streak = 0

# Path to the history file
HISTORY_FILE = Path.home() / ".delta" / "history.json"

def save_interaction(user_input, response):
    """Save a chat interaction to the history file."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    interaction = {
        "timestamp": timestamp,
        "user_input": user_input,
        "response": response
    }
    
    # Ensure the directory exists
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    
    # Initialize the file if it doesn't exist
    if not HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)
    
    # Append the new interaction
    with open(HISTORY_FILE, 'r+') as f:
        history = json.load(f)
        history.append(interaction)
        f.seek(0)
        f.truncate()
        json.dump(history, f, indent=4)

def display_history():
    """Display the chat history from the history file."""
    if not HISTORY_FILE.exists():
        console.print("[yellow]No chat history found.[/yellow]")
        return
    
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
        for interaction in history:
            console.print(f"[bold cyan]{interaction['timestamp']}[/bold cyan]")
            console.print(f"[bold]User:[/bold] {interaction['user_input']}")
            console.print(f"[bold]Assistant:[/bold] {interaction['response']}")
            console.print("---")

def clear_history():
    """Clear the chat history file."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)
        console.print("[green]Chat history cleared.[/green]")
    else:
        console.print("[yellow]No chat history to clear.[/yellow]")

def think_about_question(model_name, question):
    """Analyze question for key concepts and intent (minimal output)."""
    import ollama
    think_prompt = f"Analyze this question and identify key concepts, intent and potential ambiguities without answering it: '{question}'"
    response = ollama.generate(model=model_name, prompt=think_prompt, options={'num_ctx': 512}, stream=True)
    thought = ""
    for chunk in response:
        content = chunk.get('message', {}).get('content', '')
        console.print(content, end="", style="italic grey50")
        thought += content
    console.print()
    return thought

def preprocess_query(query):
    """Clean and optimize query for better Wikipedia search."""
    # Remove stop words and normalize
    stop_words = {'a', 'was', 'an', 'the', 'is', 'are', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
    query = query.lower().strip()
    query = re.sub(r'[^\w\s]', '', query)  # Remove punctuation
    words = [word for word in query.split() if word not in stop_words]
    return ' '.join(words)

def similarity_score(a, b):
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

@lru_cache(maxsize=128)
def fetch_wikipedia_context(query):
    """Fetch concise context from Wikipedia with improved relevance and disambiguation handling."""
    import wikipedia
    from requests.exceptions import RequestException

    try:
        # Search for up to 3 results to find the most relevant
        processed_query = preprocess_query(query)
        search_results = wikipedia.search(processed_query, results=3)
        if not search_results:
            console.print("[yellow]\nNo Wikipedia results found.[/yellow]")
            return "", [], [], ""

        best_result = None
        best_score = 0
        best_summary = ""
        best_citations = []
        best_url = ""

        for result in search_results:
            try:
                page = wikipedia.page(result, auto_suggest=False)
                summary = wikipedia.summary(result, sentences=3, auto_suggest=False)
                score = similarity_score(processed_query, page.title)
                if score > best_score:
                    best_score = score
                    best_result = page
                    best_summary = summary[:1000] + "..." if len(summary) > 1000 else summary
                    best_citations = page.references[:3]
                    best_url = page.url
            except wikipedia.exceptions.DisambiguationError as e:
                # Try the first option from disambiguation
                if e.options:
                    try:
                        page = wikipedia.page(e.options[0], auto_suggest=False)
                        summary = wikipedia.summary(e.options[0], sentences=3, auto_suggest=False)
                        score = similarity_score(processed_query, page.title)
                        if score > best_score:
                            best_score = score
                            best_result = page
                            best_summary = summary[:1000] + "..." if len(summary) > 1000 else summary
                            best_citations = page.references[:3]
                            best_url = page.url
                    except Exception:
                        continue
            except wikipedia.exceptions.PageError:
                continue

        if best_result:
            console.print(f"\n📖 [yellow]Wiki: {best_result.title}[/yellow]")
            return best_summary, best_citations, [], best_url
        else:
            console.print("[yellow]\nNo relevant Wikipedia page found after trying multiple results.[/yellow]")
            return "", [], [], ""
    except RequestException as e:
        console.print(f"❌ [red]Wiki Error: {str(e)}[/red]")
        return "", [], [], ""

@lru_cache(maxsize=128)
def fetch_arxiv_context(query):
    """Fetch concise context from arXiv."""
    import arxiv
    client = arxiv.Client()
    try:
        search = arxiv.Search(query=query, max_results=1, sort_by=arxiv.SortCriterion.Relevance)
        results = list(client.results(search))
        if results:
            paper = results[0]
            context = f"{paper.title}: {paper.summary[:200]}..."
            citations = [paper.entry_id]
            console.print(f"📄 [yellow]arXiv: {paper.title}[/yellow]")
            return context, citations, [], paper.entry_id
        return "", [], [], ""
    except Exception as e:
        console.print(f"❌ [red]arXiv Error: {str(e)}[/red]")
        return "", [], [], ""

# Rate limiting parameters
MIN_INTERVAL = 300  # 5 minutes between requests
RATE_LIMIT_FILE = Path.home() / ".delta" / "ddg_last_request.txt"

def update_last_request_time():
    """Update the timestamp of the last DuckDuckGo request."""
    RATE_LIMIT_FILE.parent.mkdir(exist_ok=True)
    with open(RATE_LIMIT_FILE, "w") as f:
        f.write(str(time.time()))

def get_last_request_time():
    """Read the timestamp of the last DuckDuckGo request."""
    if RATE_LIMIT_FILE.exists():
        with open(RATE_LIMIT_FILE, "r") as f:
            try:
                return float(f.read().strip())
            except ValueError:
                return 0
    return 0

@lru_cache(maxsize=128)
def fetch_duckduckgo_context(query):
    """Fetch concise context from DuckDuckGo with strict rate limiting."""
    current_time = time.time()
    last_request_time = get_last_request_time()
    time_since_last = current_time - last_request_time

    # Enforce minimum interval between requests
    if time_since_last < MIN_INTERVAL:
        wait_time = MIN_INTERVAL - time_since_last
        console.print(f"[yellow]Rate limit: Waiting {wait_time:.1f} seconds before next request...[/yellow]")
        time.sleep(wait_time)

    # Update timestamp before making the request
    update_last_request_time()

    from duckduckgo_search import DDGS

    try:
        # Enhanced browser-like headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive"
        }
        with DDGS(timeout=20, headers=headers) as ddgs:
            results = ddgs.text(query, region='wt-wt', safesearch='off', timelimit='y', max_results=2)
        if results:
            context = ""
            citations = []
            for i, result in enumerate(results, 1):
                snippet = result['body'][:200] + "..." if len(result['body']) > 200 else result['body']
                context += f"Result {i}: {snippet}\n"
                citations.append(result['href'])
            console.print(f"🌐 [yellow]DuckDuckGo: {query}[/yellow]")
            return context, citations, [], citations[0] if citations else ""
        return "", [], [], ""
    except Exception as e:
        error_msg = str(e)
        if "Ratelimit" in error_msg:
            console.print(f"[yellow]Rate limit hit: {error_msg}. Please wait {MIN_INTERVAL/60:.1f} minutes before trying again.[/yellow]")
            return "", [], [], ""
        else:
            console.print(f"❌ [red]DuckDuckGo Error: {error_msg}[/red]")
            return "", [], [], ""

def read_text_file(file_path):
    """Read content from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")
        return ""

def read_pdf_file(file_path):
    """Read content from a PDF file."""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")
        return ""

def read_docx_file(file_path):
    """Read content from a DOCX file."""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        console.print(f"[red]Error reading {file_path}: {e}[/red]")
        return ""

def fetch_document_context(doc_path):
    """Fetch content from a single document file."""
    doc_path = Path(doc_path)
    if not doc_path.is_file():
        console.print(f"[red]Error: {doc_path} is not a valid file[/red]")
        return "", [], [], ""
    
    supported_extensions = {'.txt', '.pdf', '.docx'}
    if doc_path.suffix.lower() not in supported_extensions:
        console.print(f"[red]Error: Unsupported file extension {doc_path.suffix}. Supported: .txt, .pdf, .docx[/red]")
        return "", [], [], ""
    
    content = ""
    try:
        if doc_path.suffix.lower() == '.txt':
            content = read_text_file(doc_path)
        elif doc_path.suffix.lower() == '.pdf':
            content = read_pdf_file(doc_path)
        elif doc_path.suffix.lower() == '.docx':
            content = read_docx_file(doc_path)
    except Exception as e:
        console.print(f"[red]Error reading {doc_path}: {e}[/red]")
        return "", [], [], ""
    
    if content:
        context = f"Document: {doc_path.name}\n{content[:500]}...\n" if len(content) > 500 else f"Document: {doc_path.name}\n{content}\n"
        citations = [str(doc_path)]
        return context, citations, [], ""
    else:
        console.print(f"[yellow]No content found in {doc_path}[/yellow]")
        return "", [], [], ""

def get_context(query, use_wiki=False, use_arxiv=False, use_ddg=False, doc_path=None):
    """Fetch context based on flags or document file path."""
    if doc_path:
        return fetch_document_context(doc_path)
    if use_wiki:
        return fetch_wikipedia_context(query)
    if use_arxiv:
        return fetch_arxiv_context(query)
    if use_ddg:
        return fetch_duckduckgo_context(query)
    return "", [], [], ""

def run_model(model_name, use_wiki=False, use_arxiv=False, use_ddg=False, doc_path=None, use_think=False):
    """Run interactive session with streamlined responses or generate dot art."""
    import ollama
    from rich.progress import Progress, SpinnerColumn, TextColumn
    global query_streak
    console.print(f"🚀 [bold green]Delta with {model_name} (Wiki: {use_wiki}, arXiv: {use_arxiv}, DuckDuckGo: {use_ddg}, Docs: {doc_path})[/bold green]")

    # Create key bindings
    bindings = KeyBindings()

    # Submit input with Ctrl+J
    @bindings.add('c-j')
    def _(event):
        event.app.current_buffer.validate_and_handle()

    # Selection with Shift+Arrow keys
    @bindings.add('s-left')
    def _(event):
        buffer = event.app.current_buffer
        if not buffer.selection_state:
            buffer.start_selection()
        buffer.cursor_left()

    @bindings.add('s-right')
    def _(event):
        buffer = event.app.current_buffer
        if not buffer.selection_state:
            buffer.start_selection()
        buffer.cursor_right()

    @bindings.add('s-up')
    def _(event):
        buffer = event.app.current_buffer
        if not buffer.selection_state:
            buffer.start_selection()
        buffer.cursor_up()

    @bindings.add('s-down')
    def _(event):
        buffer = event.app.current_buffer
        if not buffer.selection_state:
            buffer.start_selection()
        buffer.cursor_down()

    # Copy with Ctrl+C (or exit if no selection)
    @bindings.add('c-c')
    def _(event):
        buffer = event.app.current_buffer
        if buffer.selection_state:
            selected_text = buffer.copy_selection()
            pyperclip.copy(selected_text)
            console.print("[green]Text copied to clipboard.[/green]")
            buffer.exit_selection()
        else:
            raise KeyboardInterrupt

    # Paste with Ctrl+V
    @bindings.add('c-v')
    def _(event):
        clipboard_content = pyperclip.paste()
        event.app.current_buffer.insert_text(clipboard_content)

    # Initialize prompt with instructions
    console.print("[yellow]Type your question. Use Enter for new lines, Ctrl+J to send, Shift+Arrows to select, Ctrl+C to copy/exit, Ctrl+V to paste.[/yellow]")
    session = PromptSession(multiline=True, key_bindings=bindings)

    messages = []
    while True:
        console.print(f"🔥 [bold]Streak: {query_streak}[/bold]")
        try:
            user_input = session.prompt('> ')
        except KeyboardInterrupt:
            console.print("👋 [bold green]Session ended. Come back soon![/bold green]")
            break
        except EOFError:
            console.print("👋 [bold green]Session ended. Come back soon![/bold green]")
            break
        if user_input.lower() == "exit":
            console.print("👋 [bold green]Session ended. Come back soon![/bold green]")
            break

        query_streak += 1
        query_history.append(user_input)
        
        if use_think:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            ) as progress:
                task = progress.add_task("Processing query...", total=None)
                thought = think_about_question(model_name, user_input)
                progress.update(task, completed=True)  # Ensure spinner stops
            refined_query = f"{user_input} {thought}"
        else:
            refined_query = user_input

        # Add spinner for context fetching
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("Fetching context...", total=None)
            context, citations, images, url = get_context(refined_query, use_wiki, use_arxiv, use_ddg, doc_path)
            progress.update(task, completed=True)  # Ensure spinner stops

        if not context:
            prompt = f"Question: {user_input}\nAnswer concisely using your knowledge."
        else:
            prompt = f"Context: {context}\nQuestion: {user_input}\nAnswer concisely."
            console.print("✅ [green]Using retrieved context[/green]")

        messages.append({'role': 'user', 'content': prompt})

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("Generating response...", total=None)
            response_chunks = ollama.chat(
                model=model_name,
                messages=messages,
                options={'num_ctx': 2048, 'max_tokens': 250},
                stream=True
            )

        full_response = ""
        start_time = time.time()
        for chunk in response_chunks:
            content = chunk.get('message', {}).get('content', '')
            console.print(content, end="", style="cyan")
            full_response += content

        console.print()
        end_time = time.time()

        elapsed_time = end_time - start_time
        token_count = len(full_response.split())
        if elapsed_time > 0:
            console.print(f"⚡ [bold]Speed: {token_count / elapsed_time:.2f} tokens/s[/bold]")

        if context and citations:
            console.print("📚 [bold]Sources:[/bold]")
            for i, citation in enumerate(citations, 1):
                console.print(f"{i}. {citation}")
            if url:
                console.print(f"🔗 [bold]Link:[/bold] {url}")

        messages.append({'role': 'assistant', 'content': full_response})
        save_interaction(user_input, full_response)

        if query_history:
            console.print(f"💡 [italic]Try: {query_history[-1]}[/italic]")

def list_models():
    """List available models with detailed information."""
    import ollama
    from rich.table import Table
    
    try:
        response = ollama.list()
        models = response.get('models', [])
    except Exception as e:
        console.print(f"❌ [red]Error listing models: {str(e)}[/red]")
        return

    if not models:
        console.print("ℹ️ [yellow]No models installed. Use 'delta pull <model>' to download one.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Model Name", style="cyan", no_wrap=True)
    table.add_column("Size", justify="right")
    table.add_column("Modified At", justify="right")
    table.add_column("Format")
    table.add_column("Parameters")
    table.add_column("Quantization")

    for model in models:
        name = model.get('model', 'N/A')
        size = f"{model.get('size', 0)/1e9:.1f} GB" if model.get('size') else 'N/A'
        mod_at = model.get('modified_at')
        modified_at = mod_at.strftime('%Y-%m-%d %H:%M') if mod_at else 'N/A'
        details = model.get('details', {})
        fmt = details.get('format', 'N/A')
        params = details.get('parameter_size', 'N/A').replace('B', '') + "B" if details.get('parameter_size') else 'N/A'
        quant = details.get('quantization_level', 'N/A')

        table.add_row(name, size, modified_at, fmt, params, quant)

    console.print("📋 [bold]Installed Models:[/bold]")
    console.print(table)

def pull_model(model_name):
    import ollama
    from rich.progress import Progress, SpinnerColumn, BarColumn, DownloadColumn, TextColumn, TimeRemainingColumn
    from rich.console import Console
    console = Console()

    try:
        console.print(f"⬇️ Downloading {model_name}")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            transient=True
        ) as progress:
            task = progress.add_task(f"Downloading {model_name}", total=None)
            response = ollama.pull(model_name, stream=True)
            layers = {}
            total_size = 0
            for chunk in response:
                if chunk.get('status') == 'downloading':
                    digest = chunk.get('digest', '')
                    total = int(chunk.get('total', 0))
                    completed = int(chunk.get('completed', 0))
                    if digest not in layers:
                        layers[digest] = {'total': total, 'completed': completed}
                        total_size += total
                        if progress.tasks[task].total is None:
                            progress.update(task, total=total_size)
                    else:
                        layers[digest]['completed'] = completed
                    downloaded = sum(l['completed'] for l in layers.values())
                    progress.update(task, completed=downloaded)
            progress.update(task, completed=total_size or 0)
        console.print(f"✅ {model_name} downloaded successfully!")
    except Exception as e:
        console.print(f"❌ Download failed: {str(e)}")
        raise

def remove_model(model_name):
    """Remove a model."""
    import ollama
    console.print(f"🗑️ [yellow]Removing {model_name}...[/yellow]")
    ollama.delete(model_name)
    console.print(f"✅ [green]{model_name} removed![/green]")

def setup_delta():
    """Set up Delta CLI with virtual environment for smooth execution."""
    bin_dir = Path.home() / "bin"
    env_dir = bin_dir / "delta_env"
    delta_path = bin_dir / "delta"
    
    try:
        python_version = subprocess.run(["python3", "--version"], capture_output=True, text=True, check=True)
        console.print(f"[green]Python found: {python_version.stdout.strip()}[/green]")
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[red]Error: Python 3 is required. Please install Python 3 and try again.[/red]")
        console.print("[yellow]On Ubuntu: sudo apt update && sudo apt install python3 python3-venv[/yellow]")
        console.print("[yellow]On macOS: brew install python[/yellow]")
        return
    
    try:
        subprocess.run(["python3", "-m", "venv", "--help"], capture_output=True, check=True)
        console.print("[green]Python venv module found[/green]")
    except subprocess.CalledProcessError:
        console.print("[red]Error: Python venv module is missing. Please ensure Python 3 includes venv.[/red]")
        return
    
    bin_dir.mkdir(exist_ok=True)
    console.print(f"[green]Created {bin_dir} if it didn't exist[/green]")
    
    if not env_dir.exists():
        subprocess.run(["python3", "-m", "venv", str(env_dir)], check=True)
        console.print(f"[green]Created virtual environment at {env_dir}[/green]")
    else:
        console.print(f"[yellow]Virtual environment at {env_dir} already exists[/yellow]")
    
    if sys.platform.startswith('win'):
        pip_path = env_dir / "Scripts" / "pip.exe"
        python_path = env_dir / "Scripts" / "python.exe"
    else:
        pip_path = env_dir / "bin" / "pip"
        python_path = env_dir / "bin" / "python"
    
    libraries = ["rich", "ollama", "wikipedia", "arxiv", "Pillow", "duckduckgo_search", "PyPDF2", "python-docx", "prompt_toolkit", "pyperclip", "pynvml", "psutil", "py-cpuinfo"]
    try:
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        console.print("[green]Upgraded pip in virtual environment[/green]")
        subprocess.run([str(pip_path), "install"] + libraries, check=True)
        console.print(f"[green]Installed {', '.join(libraries)} in virtual environment[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error installing libraries: {e}[/red]")
        console.print("[yellow]Ensure internet connectivity and try again.[/yellow]")
        return
    
    is_binary = getattr(sys, 'frozen', False)
    if is_binary:
        current_binary = Path(sys.executable).resolve()
        try:
            shutil.copy2(current_binary, delta_path)
            if not sys.platform.startswith('win'):
                delta_path.chmod(0o755)
            console.print(f"[green]Copied Delta binary to {delta_path} and made executable[/green]")
        except Exception as e:
            console.print(f"[red]Error copying binary: {e}[/red]")
            return
    else:
        current_script = Path(__file__).resolve()
        try:
            with current_script.open("r") as f:
                content = f.readlines()
            if not sys.platform.startswith('win'):
                shebang = f"#!{python_path}\n"
                if content[0].startswith("#!"):
                    content[0] = shebang
                else:
                    content.insert(0, shebang)
            with delta_path.open("w") as f:
                f.writelines(content)
            if not sys.platform.startswith('win'):
                delta_path.chmod(0o755)
            console.print(f"[green]Copied Delta script to {delta_path} and made executable[/green]")
        except Exception as e:
            console.print(f"[red]Error copying script: {e}[/red]")
            return
    
    if not sys.platform.startswith('win'):
        shell_configs = [
            (Path.home() / ".bashrc", 'export PATH="$HOME/bin:$PATH"', "# Delta CLI PATH"),
            (Path.home() / ".zshrc", 'export PATH="$HOME/bin:$PATH"', "# Delta CLI PATH"),
        ]
        
        for config_path, path_line, comment in shell_configs:
            config_dir = config_path.parent
            config_dir.mkdir(exist_ok=True)
            if config_path.exists():
                with config_path.open("r") as f:
                    content = f.read()
                if path_line not in content:
                    with config_path.open("a") as f:
                        f.write(f"\n{comment}\n{path_line}\n")
                    console.print(f"[green]Updated {config_path} with PATH for Delta[/green]")
                else:
                    console.print(f"[yellow]{config_path} already contains PATH for Delta[/yellow]")
            else:
                with config_path.open("w") as f:
                    f.write(f"{comment}\n{path_line}\n")
                console.print(f"[green]Created {config_path} with PATH for Delta[/green]")
        
        console.print("[bold green]Setup complete! To activate Delta, run one of the following:[/bold green]")
        console.print("[bold][cyan]Bash:[/cyan][/bold] source ~/.bashrc")
        console.print("[bold][cyan]Zsh:[/cyan][/bold] source ~/.zshrc")
        console.print("[bold green]Then run 'delta' from anywhere! Example: 'delta run mistral --docs /path/to/document.pdf'[/bold green]")
    else:
        console.print("[bold green]Setup complete! On Windows, run: 'python delta.py run mistral --docs C:\\path\\to\\document.pdf'[/bold green]")

def is_model_available(model_name):
    """Check if the specified model is available locally."""
    import ollama
    try:
        response = ollama.list()
        models = response.get('models', [])
        for model in models:
            if model.get('model') == model_name:
                return True
        return False
    except Exception as e:
        console.print(f"❌ [red]Error checking models: {str(e)}[/red]")
        return False

def get_max_category(P_billion):
    if P_billion < 1:
        return "Nano/Tiny (<1B)"
    elif P_billion <= 7:
        return "Small (1B–7B)"
    elif P_billion <= 30:
        return "Medium (8B–30B)"
    elif P_billion <= 70:
        return "Large (30B–70B)"
    elif P_billion <= 180:
        return "X-Large (70B–180B)"
    else:
        return "Frontier/Trillion (>200B)"

def check_hardware():
    # Check GPU
    gpu_available = False
    max_vram = 0
    try:
        pynvml.nvmlInit()
        deviceCount = pynvml.nvmlDeviceGetCount()
        if deviceCount > 0:
            gpu_available = True
            vram_list = []
            for i in range(deviceCount):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                memoryInfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
                vram = memoryInfo.total / 1e9  # Convert bytes to GB
                vram_list.append(vram)
            max_vram = max(vram_list)
            console.print(f"[green]Found {deviceCount} NVIDIA GPU(s). The GPU with the most VRAM has {max_vram:.2f} GB.[/green]")
        else:
            console.print("[yellow]No NVIDIA GPUs found.[/yellow]")
    except ImportError:
        console.print("[red]pynvml is not installed. Please run 'delta setup' to install dependencies.[/red]")
    except pynvml.NVMLError:
        console.print("[yellow]No NVIDIA GPUs found or drivers not installed.[/yellow]")
    finally:
        try:
            pynvml.nvmlShutdown()
        except:
            pass

    # Check CPU details
    try:
        cpu_info = cpuinfo.get_cpu_info()
        cpu_model = cpu_info.get('brand_raw', 'Unknown')
        l3_cache = cpu_info.get('l3_cache_size', 'Unknown')
        if l3_cache != 'Unknown':
            l3_cache = int(l3_cache) / (1024 * 1024)  # Convert bytes to MB
            l3_cache = f"{l3_cache:.1f} MB"
    except Exception as e:
        console.print(f"[yellow]Could not retrieve detailed CPU information: {e}[/yellow]")
        cpu_model = "Unknown"
        l3_cache = "Unknown"

    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)
    if physical_cores and logical_cores:
        threads_per_core = logical_cores / physical_cores
    else:
        threads_per_core = "Unknown"

    cpu_freq = psutil.cpu_freq().current / 1000 if psutil.cpu_freq() else "Unknown"  # Convert to GHz
    ram_total = psutil.virtual_memory().total / 1e9  # Convert to GB

    # Display hardware info
    console.print(f"[green]CPU Model: {cpu_model}[/green]")
    console.print(f"[green]CPU Cores: {physical_cores}[/green]")
    console.print(f"[green]Threads per Core: {threads_per_core:.1f}" if threads_per_core != "Unknown" else "[yellow]Threads per Core: Unknown[/yellow]")
    console.print(f"[green]CPU Frequency: {cpu_freq:.2f} GHz[/green]" if cpu_freq != "Unknown" else "[yellow]CPU Frequency: Unknown[/yellow]")
    console.print(f"[green]RAM: {ram_total:.2f} GB[/green]")

    # Provide recommendations with speed estimations
    console.print("\n**Recommendations for Running LLMs:**")
    if gpu_available:
        bandwidth = 30e9 * max_vram  # Estimated bandwidth in B/s
        console.print("**With your GPU:**")
        for precision, bytes_per_param in [("16-bit", 2), ("8-bit", 1), ("4-bit", 0.5)]:
            P = (max_vram * 1e9) / bytes_per_param  # Maximum parameters
            P_billion = P / 1e9
            if P_billion < 0.1:
                console.print(f"- In {precision} precision, your GPU VRAM is too small for most LLMs.")
                continue
            category = get_max_category(P_billion)
            tokens_sec = (0.5 * bandwidth) / P  # Estimated tokens/sec
            console.print(f"- In {precision} precision, you can run models up to ~{P_billion:.1f}B parameters ({category}), with estimated speed of ~{tokens_sec:.1f} tokens/sec for such a model.")
    else:
        bandwidth = 50e9  # Default CPU bandwidth in B/s
        effective_memory = ram_total / 2  # Assume 50% of RAM for model
        console.print("**Without GPU, using CPU and RAM:**")
        for precision, bytes_per_param in [("16-bit", 2), ("8-bit", 1), ("4-bit", 0.5)]:
            P = (effective_memory * 1e9) / bytes_per_param  # Maximum parameters
            P_billion = P / 1e9
            if P_billion < 0.1:
                console.print(f"- In {precision} precision, your RAM is too small for most LLMs.")
                continue
            category = get_max_category(P_billion)
            tokens_sec = (0.5 * bandwidth) / P  # Estimated tokens/sec
            console.print(f"- In {precision} precision, you can load models up to ~{P_billion:.1f}B parameters ({category}), with estimated speed of ~{tokens_sec:.1f} tokens/sec for such a model. Note that CPU inference is slower than GPU.")

    console.print("\n[italic]Note: These are estimates based on typical hardware performance and model characteristics. Actual speeds may vary depending on specific model architecture, batch size, and sequence length.[/italic]")

def main():
    """Parse arguments and execute commands.""" 
    custom_help_message = """Delta CLI:
        A local Inferencing tool, brings powerful language models to your CPU.

Usage:
        delta    [command]    [Flags]
        delta    [command]

Available Commands:
        run                    Run model with [Flags]
        list                   List models
        pull                   Download model
        remove                 Remove model
        hist                   Display or clear chat history
        check                  Check hardware capabilities for running LLMs

Available Flags:
        --wiki                 Searching Wikipedia
        --ddg                  Searching DuckDuckGo
        --arxiv                Search arXiv paper
        --docs                 Searching through local documents
        --think                Allow delta to take some time to think
        --clear                Clear all the history
        --version              Show Delta version
        --help/-h              help for delta"""

    # Define the custom action
    class CustomHelpAction(argparse.Action):
        def __call__(self, parser, namespace, values=None, option_string=None):
            print(custom_help_message)
            sys.exit(0)
    
    # Create the parser with add_help=False to disable default help
    parser = argparse.ArgumentParser(add_help=False)

    # Add custom --help and -h options
    parser.add_argument("--help", "-h", action=CustomHelpAction, nargs=0, help=argparse.SUPPRESS)

    # Add --version flag
    parser.add_argument("--version", action="version", version="delta v2.0")

    # Add subparsers for commands
    subparsers = parser.add_subparsers(dest="command")

    # Define subcommands with their help messages
    run_parser = subparsers.add_parser("run", help="Run model with [Flags] Wiki/arXiv/DuckDuckGo/docs")
    run_parser.add_argument("model", help="Model name")
    run_parser.add_argument("--wiki", action="store_true", help="Search Wikipedia")
    run_parser.add_argument("--arxiv", action="store_true", help="Search arXiv")
    run_parser.add_argument("--ddg", action="store_true", help="Search DuckDuckGo for current information")
    run_parser.add_argument("--docs", help="Path to a document file (.txt, .pdf, .docx)")
    run_parser.add_argument("--think", action="store_true", help="Include thinking step to analyze the question")

    subparsers.add_parser("list", help="List models")
    pull_parser = subparsers.add_parser("pull", help="Download model")
    pull_parser.add_argument("model", help="Model name")
    remove_parser = subparsers.add_parser("remove", help="Remove model")
    remove_parser.add_argument("model", help="Model name")
    subparsers.add_parser("setup", help="Set up Delta CLI with virtual environment for easy execution")
    
    hist_parser = subparsers.add_parser("hist", help="Display or clear chat history")
    hist_parser.add_argument("--clear", action="store_true", help="Clear chat history")
    check_parser = subparsers.add_parser("check", help="Check hardware capabilities for running LLMs")

    # Parse arguments
    args = parser.parse_args()

    # Placeholder for command execution logic
    if not args.command:
        print(custom_help_message)
        sys.exit(0) 
    
    if args.command == "run":
        if not is_model_available(args.model):
            console.print(f"❌ [red]Sorry, this model '{args.model}' is not yet downloaded, Please check available models with 'delta list' or download a new model'.[/red]")
        else:
            if sum([args.wiki, args.arxiv, args.ddg, bool(args.docs)]) > 1:
                console.print("❌ [red]Use only one: --wiki, --arxiv, --ddg, or --docs[/red]")
            else:
                run_model(args.model, use_wiki=args.wiki, use_arxiv=args.arxiv, use_ddg=args.ddg, doc_path=args.docs, use_think=args.think)
    elif args.command == "list":
        list_models()
    elif args.command == "pull":
        pull_model(args.model)
    elif args.command == "remove":
        remove_model(args.model)
    elif args.command == "setup":
        setup_delta()
    elif args.command == "hist":
        if args.clear:
            clear_history()
        else:
            display_history()
    elif args.command == "check":
        check_hardware()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
