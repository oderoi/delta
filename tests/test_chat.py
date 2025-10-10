import pytest
import json
from unittest.mock import patch, MagicMock
from delta.chat import load_history, save_history, prepend_search, run_chat, HISTORY_FILE
from pathlib import Path

def test_load_history_empty(tmp_path):
    """Test loading an empty or non-existent history file."""
    temp_file = tmp_path / "history.json"
    with patch("delta.chat.HISTORY_FILE", temp_file):
        history = load_history()
        assert history == [], "Expected empty history list"

def test_load_history_existing(tmp_path):
    """Test loading an existing history file."""
    temp_file = tmp_path / "history.json"
    history_data = [{"id": "test-session", "messages": [{"user": "Hi", "assistant": "Hello", "timestamp": "2025-10-09"}]}]
    temp_file.write_text(json.dumps(history_data))
    with patch("delta.chat.HISTORY_FILE", temp_file):
        history = load_history()
        assert history == history_data, "Expected history to match written data"

def test_save_history(tmp_path):
    """Test saving history to a file."""
    temp_file = tmp_path / "history.json"
    history = [{"id": "test", "messages": [{"user": "Hi", "assistant": "Hello", "timestamp": "2025-10-09"}]}]
    with patch("delta.chat.HISTORY_FILE", temp_file):
        save_history(history)
        assert temp_file.exists(), "History file should be created"
        assert json.loads(temp_file.read_text()) == history, "Saved history should match input"

def test_prepend_search_no_flag():
    """Test prepend_search with no flag."""
    query = "What is AI?"
    result = prepend_search(query, None)
    assert result == "Question: What is AI?\nAnswer:", "Expected plain query without context"

@patch('delta.chat.wikipedia')
def test_prepend_search_wiki(mock_wiki):
    """Test prepend_search with --wiki flag."""
    query = "Artificial Intelligence"
    mock_page = MagicMock()
    mock_page.summary = "AI is the simulation of human intelligence in machines."
    mock_wiki.page.return_value = mock_page
    result = prepend_search(query, "--wiki")
    expected = "Context from Wikipedia: AI is the simulation of human intelligence in machines.\n\nQuestion: Artificial Intelligence\nAnswer:"
    assert result == expected, "Expected Wikipedia context in prompt"

@patch('delta.chat.wikipedia')
def test_prepend_search_wiki_error(mock_wiki):
    """Test prepend_search with --wiki when Wikipedia fails."""
    query = "Unknown Topic"
    mock_wiki.page.side_effect = Exception("Page not found")
    result = prepend_search(query, "--wiki")
    assert result == "Question: Unknown Topic\nAnswer:", "Expected fallback to plain query on Wiki error"

@patch('delta.chat.DDGS')
def test_prepend_search_ddg(mock_ddgs):
    """Test prepend_search with --ddg flag."""
    query = "AI ethics"
    mock_ddgs_instance = MagicMock()
    mock_ddgs.return_value = mock_ddgs_instance
    mock_ddgs_instance.text.return_value = [{"body": "AI ethics concerns moral issues in AI development."}]
    result = prepend_search(query, "--ddg")
    expected = "Context from DuckDuckGo: AI ethics concerns moral issues in AI development.\n\nQuestion: AI ethics\nAnswer:"
    assert result == expected, "Expected DuckDuckGo context in prompt"

@patch('delta.chat.PyPDF2')
def test_prepend_search_docs(mock_pypdf2, tmp_path):
    """Test prepend_search with --docs flag and PDF file."""
    query = "Summarize doc"
    doc_path = tmp_path / "test.pdf"
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "This is a test document about AI."
    mock_reader.pages = [mock_page]
    mock_pypdf2.PdfReader.return_value = mock_reader
    result = prepend_search(query, f"--docs {doc_path}")
    expected = "Document summary: This is a test document about AI.\n\nQuery: Summarize or answer about this doc.\nResponse:"
    assert result == expected, "Expected document context in prompt"

@patch('delta.chat.ensure_llama_binary')
@patch('delta.chat.subprocess.Popen')
def test_run_chat(mock_popen, mock_ensure_binary, tmp_path):
    """Test run_chat with mocked subprocess."""
    model_path = "/path/to/model.gguf"
    mock_ensure_binary.return_value = Path("/fake/bin/llama-main")
    mock_process = MagicMock()
    mock_process.stdout = ["Assistant response\n"]
    mock_popen.return_value = mock_process
    temp_file = tmp_path / "history.json"
    with patch("delta.chat.HISTORY_FILE", temp_file):
        # Mock user input to exit immediately
        with patch('builtins.input', side_effect=["exit"]):
            run_chat(model_path, [])
        history = load_history()
        assert len(history) == 1, "Expected one session in history"
        assert history[0]["messages"] == [], "Expected empty messages due to exit"