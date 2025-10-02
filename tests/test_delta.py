import pytest
from pathlib import Path
from delta.models import pull_model, list_models, get_model_path
from delta.config import MODELS_DIR

def test_pull_model(tmp_path):
    # Mock HF download would require internet; test config instead
    Path(MODELS_DIR).mkdir(exist_ok=True)
    model_path = pull_model("test", "test/repo", "test.gguf")
    assert model_path.exists()
    assert list_models()["test"] == str(model_path)
    assert get_model_path("test") == model_path

if __name__ == "__main__":
    pytest.main([__file__])