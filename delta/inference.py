import os
from typing import List, Dict, Any

from llama_cpp import Llama
from .config import MODELS_DIR

def load_model(model_path: str, **kwargs) -> Llama:
    return Llama(
        model_path=model_path,
        n_ctx=4096,  # Increased for better convos
        n_threads=os.cpu_count() or 4,
        verbose=False,
        chat_format="llama-3",  # Updated default
        **kwargs
    )

def chat_with_model(llm: Llama, messages: List[Dict[str, str]], **gen_kwargs) -> str:
    response = llm.create_chat_completion(
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
        top_p=0.9,
        stop=["<|im_end|>", "\n\nHuman:", "\nAssistant:"],
        **gen_kwargs
    )
    return response["choices"][0]["message"]["content"]

def interactive_chat(model_path: str):
    llm = load_model(model_path)
    messages: List[Dict[str, str]] = [{"role": "system", "content": "You are a helpful assistant."}]
    
    print("Delta chat: Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break
        
        messages.append({"role": "user", "content": user_input})
        try:
            response = chat_with_model(llm, messages)
            print(f"Delta: {response}\n")
            messages.append({"role": "assistant", "content": response})
        except Exception as e:
            print(f"Error generating response: {e}")