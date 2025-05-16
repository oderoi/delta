#!/usr/bin/env python3

import argparse
from rich.console import Console
from functools import lru_cache
import time
import sys
import threading
import os
from pathlib import Path
import shutil
import subprocess
import sysconfig

# Initialize rich console
console = Console()

# In-memory query history for personalization
query_history = []
query_streak = 0

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

@lru_cache(maxsize=128)
def fetch_wikipedia_context(query):
    """Fetch concise context from Wikipedia."""
    import wikipedia
    from requests.exceptions import RequestException
    try:
        search_results = wikipedia.search(query, results=1)
        if not search_results:
            return "", [], [], ""
        page = wikipedia.page(search_results[0], auto_suggest=False)
        summary = page.summary[:300] + "..."
        citations = page.references[:2]
        url = page.url
        console.print(f"📖 [yellow]Wiki: {page.title}[/yellow]")
        return summary, citations, [], url
    except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError, RequestException) as e:
        console.print(f"❌ [red]Wiki Error: {str(e)}[/red]")
        return "", [], [], ""

@lru_cache(maxsize=128)
def fetch_arxiv_context(query):
    """Fetch concise context from arXiv."""
    import arxiv
    try:
        search = arxiv.Search(query=query, max_results=1, sort_by=arxiv.SortCriterion.Relevance)
        results = list(search.results())
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

@lru_cache(maxsize=128)
def fetch_duckduckgo_context(query):
    """Fetch concise context from DuckDuckGo for current information."""
    from duckduckgo_search import DDGS
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=2)
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
        console.print(f"❌ [red]DuckDuckGo Error: {str(e)}[/red]")
        return "", [], [], ""

def get_context(query, use_wiki=False, use_arxiv=False, use_ddg=False):
    """Fetch context based on flags."""
    if use_wiki:
        return fetch_wikipedia_context(query)
    if use_arxiv:
        return fetch_arxiv_context(query)
    if use_ddg:
        return fetch_duckduckgo_context(query)
    return "", [], [], ""

def generate_dot_art(image_path, width=80, threshold=128):
    """Generate and print dot art from an image file using '.' dots."""
    from PIL import Image
    try:
        img = Image.open(image_path).convert("L")
        aspect_ratio = img.height / img.width
        height = int(width * aspect_ratio)
        img = img.resize((width, height))
        console.print("[bold green]Generating dot art...[/bold green]")
        for y in range(height):
            for x in range(width):
                pixel = img.getpixel((x, y))
                sys.stdout.write("." if pixel < threshold else " ")
            sys.stdout.write("\n")
        sys.stdout.flush()
    except Exception as e:
        console.print(f"[red]Error generating dot art: {e}[/red]")

def run_model(model_name, use_wiki=False, use_arxiv=False, use_ddg=False, draw=None):
    """Run interactive session with streamlined responses or generate dot art."""
    import ollama
    global query_streak
    console.print(f"🚀 [bold green]Delta with {model_name} (Wiki: {use_wiki}, arXiv: {use_arxiv}, DuckDuckGo: {use_ddg}, Draw: {draw})[/bold green]")
    
    if draw:
        generate_dot_art(draw)
        return

    messages = []
    while True:
        console.print(f"🔥 [bold]Streak: {query_streak}[/bold]")
        user_input = input("> ")
        if user_input.lower() == "exit":
            console.print("👋 [bold green]Session ended. Come back soon![/bold green]")
            break

        query_streak += 1
        query_history.append(user_input)

        # Run animation in a separate thread
        def animate():
            patterns = [" .", "..", ":.", "⋮.", "⋮⋮"]  # Animate :: one dot at a time
            i = 0
            while not stop_animation.is_set():
                sys.stdout.write(f"\r{patterns[i % len(patterns)]}")
                sys.stdout.flush()
                i += 1
                time.sleep(0.25)
            sys.stdout.write("\r" + " " * 30 + "\r")  # Clear the line
            sys.stdout.flush()

        stop_animation = threading.Event()
        animation_thread = threading.Thread(target=animate)
        animation_thread.start()

        # Analyze question
        thought = think_about_question(model_name, user_input)
        
        # Stop animation
        stop_animation.set()
        animation_thread.join()

        refined_query = f"{user_input} {thought}"

        context, citations, images, url = get_context(refined_query, use_wiki, use_arxiv, use_ddg)

        if not context:
            prompt = f"Question: {user_input}\nAnswer concisely using your knowledge."
        else:
            prompt = f"Context: {context}\nQuestion: {user_input}\nAnswer concisely."
            console.print("✅ [green]Using retrieved context[/green]")

        messages.append({'role': 'user', 'content': prompt})

        response_chunks = ollama.chat(
            model=model_name,
            messages=messages,
            options={'num_ctx': 512, 'max_tokens': 150},
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

        # Suggest related question
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
    table.add_column("Family")
    table.add_column("Parameters")
    table.add_column("Quantization")

    for model in models:
        # Extract model information
        name = model.get('model', 'N/A').split(':')[0]
        size = f"{model.get('size', 0)/1e9:.1f} GB" if model.get('size') else 'N/A'
        
        # Handle datetime conversion
        mod_at = model.get('modified_at')
        modified_at = mod_at.strftime('%Y-%m-%d %H:%M') if mod_at else 'N/A'
        
        # Handle details
        details = model.get('details', {})
        fmt = details.get('format', 'N/A')
        family = details.get('family', 'N/A')
        params = details.get('parameter_size', 'N/A').replace('B', '') + "B" if details.get('parameter_size') else 'N/A'
        quant = details.get('quantization_level', 'N/A')

        table.add_row(
            name,
            size,
            modified_at,
            fmt,
            family,
            params,
            quant
        )

    console.print("📋 [bold]Installed Models:[/bold]")
    console.print(table)

def pull_model(model_name):
    """Download a model with detailed progress display."""
    import ollama
    import time
    from rich.console import Console
    console = Console()

    try:
        start_time = time.time()
        layers = []
        downloaded = 0
        total_size = 0

        # Start download with streaming
        response = ollama.pull(model_name, stream=True)
        
        console.print(f"⬇️ [bold yellow]Downloading {model_name}[/bold yellow]")
        console.print("[grey50]Initializing download...[/grey50]", end="\r")

        for chunk in response:
            # Track layers and progress
            if chunk.get('status') == 'starting':
                layers.append({
                    'digest': chunk['digest'],
                    'total': chunk['total'],
                    'completed': 0
                })
                total_size += chunk['total']
            
            if chunk.get('status') == 'downloading':
                # Update layer progress
                for layer in layers:
                    if layer['digest'] == chunk['digest']:
                        layer['completed'] = chunk['completed']
                        break
                
                # Calculate totals
                downloaded = sum(l['completed'] for l in layers)
                elapsed = time.time() - start_time
                speed = downloaded / elapsed if elapsed > 0 else 0
                remaining = (total_size - downloaded) / speed if speed > 0 else 0

                # Progress calculations
                percent = (downloaded / total_size) * 100 if total_size > 0 else 0
                bar_width = 40
                filled = int(bar_width * percent / 100)
                progress_bar = f"[{'='*filled}{' '*(bar_width-filled)}]"

                # Format values
                downloaded_gb = downloaded / 1e9
                total_gb = total_size / 1e9
                speed_mbs = speed / 1e6
                remaining_str = f"{remaining:.1f}s" if remaining < 3600 else f"{remaining/60:.1f}m"

                # Construct status line
                status = (
                    f"[cyan]{model_name}[/cyan] "
                    f"[green]{percent:.1f}%[/green] "
                    f"{progress_bar} "
                    f"[yellow]{downloaded_gb:.2f}/{total_gb:.2f} GB[/yellow] "
                    f"[magenta]{speed_mbs:.2f} MB/s[/magenta] "
                    f"[grey50]ETA: {remaining_str}[/grey50]"
                )
                
                console.print(status, end="\r")

        console.print(f"\n✅ [bold green]{model_name} downloaded successfully![/bold green]")

    except Exception as e:
        console.print(f"\n❌ [bold red]Download failed: {str(e)}[/bold red]")
        raise

def remove_model(model_name):
    """Remove a model."""
    import ollama
    console.print(f"🗑️ [yellow]Removing {model_name}...[/yellow]")
    ollama.remove(model_name)
    console.print(f"✅ [green]{model_name} removed![/green]")

def setup_delta():
    """Set up Delta CLI with virtual environment for smooth execution."""
    bin_dir = Path.home() / "bin"
    env_dir = bin_dir / "delta_env"
    delta_path = bin_dir / "delta"
    
    # Check for Python 3 and venv
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
    
    # Create ~/bin if it doesn't exist
    bin_dir.mkdir(exist_ok=True)
    console.print(f"[green]Created {bin_dir} if it didn't exist[/green]")
    
    # Create virtual environment at ~/bin/delta_env
    if not env_dir.exists():
        subprocess.run(["python3", "-m", "venv", str(env_dir)], check=True)
        console.print(f"[green]Created virtual environment at {env_dir}[/green]")
    else:
        console.print(f"[yellow]Virtual environment at {env_dir} already exists[/yellow]")
    
    # Install required libraries in the virtual environment
    pip_path = env_dir / "bin" / "pip"
    libraries = ["rich", "ollama", "wikipedia-api", "arxiv", "Pillow", "duckduckgo_search"]
    try:
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        console.print("[green]Upgraded pip in virtual environment[/green]")
        subprocess.run([str(pip_path), "install"] + libraries, check=True)
        console.print(f"[green]Installed {', '.join(libraries)} in virtual environment[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error installing libraries: {e}[/red]")
        console.print("[yellow]Ensure internet connectivity and try again.[/yellow]")
        return
    
    # Check if running as a PyInstaller binary
    is_binary = getattr(sys, 'frozen', False)
    
    if is_binary:
        # Copy the binary to ~/bin/delta
        current_binary = Path(sys.executable).resolve()
        try:
            shutil.copy2(current_binary, delta_path)
            delta_path.chmod(0o755)  # Make executable
            console.print(f"[green]Copied Delta binary to {delta_path} and made executable[/green]")
        except Exception as e:
            console.print(f"[red]Error copying binary: {e}[/red]")
            return
    else:
        # Copy the source script to ~/bin/delta with updated shebang
        current_script = Path(__file__).resolve()
        try:
            with current_script.open("r") as f:
                content = f.readlines()
            shebang = f"#!{env_dir / 'bin' / 'python'}\n"
            if content[0].startswith("#!"):
                content[0] = shebang
            else:
                content.insert(0, shebang)
            
            with delta_path.open("w") as f:
                f.writelines(content)
            delta_path.chmod(0o755)  # Make executable
            console.print(f"[green]Copied Delta script to {delta_path} with updated shebang and made executable[/green]")
        except Exception as e:
            console.print(f"[red]Error copying script: {e}[/red]")
            return
    
    # Update shell configurations
    shell_configs = [
        (Path.home() / ".bashrc", 'export PATH="$HOME/bin:$PATH"', "# Delta CLI PATH"),
        (Path.home() / ".zshrc", 'export PATH="$HOME/bin:$PATH"', "# Delta CLI PATH"),
        (Path.home() / ".config" / "fish" / "config.fish", 'set -gx PATH $HOME/bin $PATH', "# Delta CLI PATH")
    ]
    
    for config_path, path_line, comment in shell_configs:
        config_dir = config_path.parent
        config_dir.mkdir(exist_ok=True)  # Create parent directory if needed
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
    
    # Provide instructions to source the shell configuration
    console.print("[bold green]Setup complete! To activate Delta, run one of the following:[/bold green]")
    console.print("[bold][cyan]Bash:[/cyan][/bold] source ~/.bashrc")
    console.print("[bold][cyan]Zsh:[/cyan][/bold] source ~/.zshrc")
    console.print("[bold][cyan]Fish:[/cyan][/bold] source ~/.config/fish/config.fish")
    console.print("[bold green]Then run 'delta' from anywhere! Example: 'delta run mistral'[/bold green]")

def main():
    """Parse arguments and execute commands."""
    parser = argparse.ArgumentParser(description="Delta CLI: Concise, Addictive Q&A")
    parser.add_argument("--version", action="version", version="delta v2.0")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run model with optional Wiki/arXiv or generate dot art")
    run_parser.add_argument("model", help="Model name")
    run_parser.add_argument("--wiki", action="store_true", help="Search Wikipedia")
    run_parser.add_argument("--arxiv", action="store_true", help="Search arXiv")
    run_parser.add_argument("--ddg", action="store_true", help="Search DuckDuckGo for current information")
    run_parser.add_argument("--draw", help="Generate dot art from an image file")

    subparsers.add_parser("list", help="List models")
    pull_parser = subparsers.add_parser("pull", help="Download model")
    pull_parser.add_argument("model", help="Model name")
    remove_parser = subparsers.add_parser("remove", help="Remove model")
    remove_parser.add_argument("model", help="Model name")
    
    subparsers.add_parser("setup", help="Set up Delta CLI with virtual environment for easy execution")

    args = parser.parse_args()

    if args.command == "run":
        if sum([args.wiki, args.arxiv, args.ddg]) > 1:
            console.print("❌ [red]Use only one: --wiki, --arxiv, or --ddg[/red]")
        else:
            run_model(args.model, use_wiki=args.wiki, use_arxiv=args.arxiv, use_ddg=args.ddg, draw=args.draw)
    elif args.command == "list":
        list_models()
    elif args.command == "pull":
        pull_model(args.model)
    elif args.command == "remove":
        remove_model(args.model)
    elif args.command == "setup":
        setup_delta()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
