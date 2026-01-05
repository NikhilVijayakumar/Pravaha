import pytest
from unittest.mock import MagicMock, patch
from pravaha.domain.storage.manager.llm_config_manager import LLMConfigManager

@pytest.fixture
def mock_config_data():
    return {
        "llm": {
            "creative": {
                "models": {
                    "gemma": {
                        "model": "lm_studio/gemma-3-12b-it",
                        "output_config": {
                            "alias": "gemma-3-12b",
                            "display_name": "Gemma 3 12B"
                        }
                    },
                    "gemini": {
                         "model": "gemini/gemini-2.5-flash",
                         "output_config": {
                             "alias": "gemini-2.5-flash",
                             "display_name": "Gemini 2.5 Flash"
                         }
                    }
                }
            }
        }
    }

@pytest.fixture
def manager(mock_config_data):
    # Patch the open/json.load part or just inject the cache directly
    # Since _load_config happens in init, we can patch json.load
    with patch("json.load", return_value=mock_config_data):
        # We also need to patch open, or existence check won't work if file is missing in reality
        with patch("pathlib.Path.exists", return_value=True): 
             with patch("builtins.open", MagicMock()):
                mgr = LLMConfigManager()
                # Ensure cache is set (mock might not propagate if _load_config logic is complex, 
                # strictly safer to set it manually if we rely on _config_cache)
                mgr._config_cache = mock_config_data
                return mgr

def test_resolve_exact_key_match(manager):
    # Existing behavior: match the key in "models" dict
    config = manager.resolve_output_config("gemma")
    assert config["display_name"] == "Gemma 3 12B"

def test_resolve_by_alias_case_insensitive(manager):
    # New behavior: match by alias
    # "gemma-3-12b" is the alias for the "gemma" key
    config = manager.resolve_output_config("gemma-3-12b")
    assert config["display_name"] == "Gemma 3 12B"
    
    # Case insensitive
    config_upper = manager.resolve_output_config("GEMMA-3-12B")
    assert config_upper["display_name"] == "Gemma 3 12B"

def test_resolve_by_model_name_part(manager):
    # New behavior: match by model name stem
    # model: "lm_studio/gemma-3-12b-it" -> "gemma-3-12b-it"
    config = manager.resolve_output_config("gemma-3-12b-it")
    assert config["display_name"] == "Gemma 3 12B"

def test_fallback_behavior(manager):
    # Unknown model
    config = manager.resolve_output_config("unknown_model_123")
    assert config["display_name"] == "Unknown Model 123"
