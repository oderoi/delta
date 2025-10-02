# Delta: Standalone LLM Runner

Delta is a lightweight, Ollama-inspired CLI tool for running GGUF models directly via [llama.cpp](https://github.com/ggerganov/llama.cpp). No Ollama required—downloads from Hugging Face, chats locally on CPU/GPU.

## Why Delta?
- **Zero dependencies on Ollama**: Uses `llama-cpp-python` for inference.
- **Easy model pulls**: Like `ollama pull`, but from HF repos.
- **Extensible**: Built for features like Wikipedia search (included as example).
- **Lightweight**: ~10MB install, runs on Python 3.8+.

## Quick Start

1. **Install**:
pip install -e .

- For GPU (CUDA): `CMAKE_ARGS="-DLLAMA_CUDA=on" pip install -e .`
- For Metal (Mac): `CMAKE_ARGS="-DLLAMA_METAL=on" pip install -e .`

2. **Pull a model** (e.g., Llama-3 8B Q4):

delta pull llama3-8b --repo lmstudio-ai/Meta-Llama-3-8B-Instruct-GGUF --file Meta-Llama-3-8B-Instruct-Q4_K_M.gguf


3. **List models**:
delta list

4. **Chat**:
delta run llama3-8b

- Type queries; exit with "exit".

## Features
- **Pull**: Downloads and caches GGUF files in `~/.delta/models/`.
- **Run**: Interactive chat with system prompt.
- **Search**: `delta search "query"` – Uses Wikipedia (extendable to other APIs).

## Popular Models
| Model | Command |
|-------|---------|
| Llama-3-8B | `delta pull llama3-8b --repo lmstudio-ai/Meta-Llama-3-8B-Instruct-GGUF --file Meta-Llama-3-8B-Instruct-Q4_K_M.gguf` |
| Mistral-7B | `delta pull mistral-7b --repo TheBloke/Mistral-7B-Instruct-v0.1-GGUF --file mistral-7b-instruct-v0.1.Q4_K_M.gguf` |
| Phi-3-mini | `delta pull phi3-mini --repo microsoft/Phi-3-mini-4k-instruct-gguf --file Phi-3-mini-4k-instruct-q4.gguf` |

Models stored in `~/.delta/models/`. Sizes: ~4-5GB for 7-8B Q4 quants.

## Extending
- Add features in `delta/search.py` (e.g., call `inference.chat_with_model` with search context).
- For API server: Extend `cli.py` with `llm.create_server()`.

## Troubleshooting
- OOM? Use smaller quants (Q4_0.gguf).
- Slow? Set `n_threads` in `inference.py` to your CPU cores.
- License: MIT. Models per their HF licenses.

Built with ❤️ by xAI's Grok.