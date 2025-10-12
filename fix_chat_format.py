#!/usr/bin/env python3
"""
Fix chat format for already downloaded models.
This script updates the chat format metadata for models that were downloaded
with incorrect chat format settings.
"""

import json
import os
from pathlib import Path

def fix_chat_format():
    """Fix chat format for already downloaded models."""
    print("🔧 Fixing Chat Format for Downloaded Models")
    print("=" * 50)
    
    # Define the correct chat formats for each model
    correct_formats = {
        "gemma3n:e2b": "gemma",
        "gemma3n:e4b": "gemma", 
        "gemma3:270m": "gemma",
        "gemma3:1b": "gemma",
        "gemma3:4b": "gemma",
        "gemma2:2b": "gemma",
        "llama3.2:1b": "llama3",
        "llama3.2:3b": "llama3",
        "llama3.1:8b": "llama3",
        "llama3": "llama3",
        "tinyllama": "llama3",
        "LFM2:700M": "chatml",
        "bitnet": "chatml",
        "deepseek-r1:1.5b": "chatml",
        "deepseek-r1:7b": "chatml",
        "phi3": "chatml",
        "phi4-mini": "chatml",
        "mistral": "chatml",
        "qwen3:0.6b": "chatml",
        "qwen3:1.7b": "chatml",
        "qwen3:4b": "chatml",
        "qwen3:8b": "chatml",
        "qwen2:0.5b": "chatml",
        "qwen2.5-coder:0.5b": "chatml",
        "qwen2.5-coder:1.5b": "chatml",
        "qwen2.5-coder:3b": "chatml",
        "qwen2.5-coder:7b": "chatml",
        "qwen2.5:3b": "chatml",
        "qwen2.5:7b": "chatml",
    }
    
    # Get the models directory
    models_dir = Path.home() / ".delta" / "models"
    
    if not models_dir.exists():
        print("❌ Models directory not found")
        return
    
    print(f"📁 Checking models in: {models_dir}")
    
    # Check each model directory
    fixed_count = 0
    for model_dir in models_dir.iterdir():
        if not model_dir.is_dir():
            continue
            
        # Look for metadata files
        metadata_files = list(model_dir.glob("*.json"))
        
        for metadata_file in metadata_files:
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                model_name = metadata.get('name', '')
                current_format = metadata.get('chat_format', '')
                
                if model_name in correct_formats:
                    correct_format = correct_formats[model_name]
                    
                    if current_format != correct_format:
                        print(f"🔧 Fixing {model_name}: {current_format} -> {correct_format}")
                        metadata['chat_format'] = correct_format
                        
                        with open(metadata_file, 'w') as f:
                            json.dump(metadata, f, indent=2)
                        
                        fixed_count += 1
                    else:
                        print(f"✅ {model_name}: already correct ({correct_format})")
                else:
                    print(f"⚠️  {model_name}: unknown model, skipping")
                    
            except Exception as e:
                print(f"❌ Error processing {metadata_file}: {e}")
    
    print(f"\n🎉 Fixed {fixed_count} models")
    print("\nYou can now run your models with the correct chat format!")
    print("Example: delta run gemma3n:e2b")

if __name__ == "__main__":
    fix_chat_format()
