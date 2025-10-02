import wikipedia
from .inference import load_model, chat_with_model
from .models import get_model_path

def search_and_ask(model_name: str, query: str):
    """Search Wikipedia, then ask model about it"""
    try:
        # Search Wikipedia
        summary = wikipedia.summary(query, sentences=3)
        print(f"Search result: {summary}\n")
        
        # Load model and chat with context
        model_path = get_model_path(model_name)
        if not model_path:
            raise ValueError(f"Model '{model_name}' not found. Pull it first.")
        
        llm = load_model(str(model_path))
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer."},
            {"role": "user", "content": f"Context: {summary}\n\nQuestion: What can you tell me about this?"}
        ]
        response = chat_with_model(llm, messages)
        return response
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Ambiguous query. Suggestions: {e.options[:3]}")
        return None
    except Exception as e:
        print(f"Search error: {e}")
        return None