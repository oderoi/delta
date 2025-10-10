import pytest
from unittest.mock import patch
from delta.models import pull_model, list_models, remove_model, DEFAULT_MODEL
from datetime import datetime

@patch('delta.models.hf_hub_download')
@patch('delta.models.Path.mkdir')
def test_pull_model(mock_mkdir, mock_hf_download, tmp_path):
    """Test pulling a model from Hugging Face."""
    with patch('delta.models.MODELS_DIR', tmp_path):
        with patch('delta.models.BIN_DIR', tmp_path / "bin"):
            with patch('delta.models.CONFIG_FILE', tmp_path / "config.json"):
                model_path = pull_model("qwen2:0.5b")
                assert str(model_path).startswith(str(tmp_path)), "Model path should be in tmp_path"
                mock_hf_download.assert_called_once()

def test_list_models_empty(tmp_path):
    """Test listing models when none are installed."""
    with patch('delta.models.MODELS_DIR', tmp_path):
        models = list_models()
        assert models['installed'] == [], "Expected empty installed model list"
        assert len(models['available']) > 0, "Expected non-empty available model list"
        assert any(m['name'] == "qwen2:0.5b" for m in models['available']), "Expected qwen2:0.5b in available models"

def test_list_models_metadata(tmp_path):
    """Test listing models with metadata."""
    with patch('delta.models.MODELS_DIR', tmp_path):
        model_dir = tmp_path / "Qwen2-0.5B-Instruct"
        model_dir.mkdir()
        gguf = model_dir / "Qwen2-0.5B-Instruct.Q4_0.gguf"
        gguf.touch()
        models = list_models()
        assert len(models['installed']) == 1, "Expected one installed model"
        model = models['installed'][0]
        assert model['name'] == "qwen2:0.5b"
        assert model['family'] == "qwen2"
        assert model['parameters'] == "494.03MB"
        assert model['quant'] == "Q4_0"
        assert model['format'] == "gguf"

def test_remove_model_nonexistent(tmp_path):
    """Test removing a non-existent model."""
    with patch('delta.models.MODELS_DIR', tmp_path):
        remove_model("nonexistent")
        assert not (tmp_path / "nonexistent").exists(), "Non-existent model directory should not be created"