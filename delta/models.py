import json
from pathlib import Path
from typing import Dict, Optional

from huggingface_hub import hf_hub_download
from .config import MODELS_DIR, MODEL_CONFIG_FILE

def load_model_config() -> Dict[str, str]:
    if MODEL_CONFIG_FILE.exists():
        with open(MODEL_CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_model_config(config: Dict[str, str]):
    with open(MODEL_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def pull_model(model_name: str, repo_id: str, filename: str) -> Path:
    config = load_model_config()
    if model_name in config:
        print(f"Model '{model_name}' already exists at {config[model_name]}")
        return Path(config[model_name])
    
    local_path = MODELS_DIR / f"{model_name}.gguf"
    print(f"Downloading {filename} from {repo_id}...")
    hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=MODELS_DIR,
        local_dir_use_symlinks=False,
        cache_dir=str(MODELS_DIR),
    )
    
    downloaded_path = MODELS_DIR / filename
    if downloaded_path != local_path:
        downloaded_path.rename(local_path)
    
    config[model_name] = str(local_path)
    save_model_config(config)
    print(f"Model '{model_name}' pulled successfully!")
    return local_path

def list_models() -> Dict[str, str]:
    return load_model_config()

def get_model_path(model_name: str) -> Optional[Path]:
    config = load_model_config()
    return Path(config.get(model_name)) if model_name in config else None