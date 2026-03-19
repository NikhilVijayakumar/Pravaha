import pytest
import shutil
import json
import yaml
from pathlib import Path
from pravaha.domain.llm.repository.json_llm_config_repository import JsonLLMConfigRepository
from pravaha.domain.config.cache_config import CachePathConfig

class TestJsonLLMConfigRepository:
    """
    Test suite for JSON LLM Config Repository.
    Target: tests/unit/domain/llm/infrastructure/test_json_llm_repository.py
    """
    
    @pytest.fixture
    def cache_config(self, tmp_path):
        """Mock CachePathConfig to use temporary directory."""
        # We mock get_llm_cache_dir relative to cwd
        # So we need to ensure cwd is tmp_path
        return CachePathConfig(cache_root=tmp_path / ".Pravaha")

    @pytest.fixture
    def repo(self, tmp_path, monkeypatch, cache_config):
        monkeypatch.chdir(tmp_path)
        return JsonLLMConfigRepository(cache_config=cache_config)

    def test_initialization_creates_file(self, repo, tmp_path):
        # Should create empty config if none exists
        config = repo.get_config()
        assert config == {}
        
        # Verify file creation
        expected_file = tmp_path / ".Pravaha/config/llm_config.json"
        assert expected_file.exists()

    def test_save_and_load(self, repo):
        data = {"llm": {"models": {"foo": "bar"}}}
        repo._save_config(data)
        
        loaded = repo.get_config()
        assert loaded == data

    def test_resolve_output_config(self, repo):
        # Setup config with output settings
        data = {
            "llm_config": {
                "default": {
                    "output": {
                        "alias": "def_mod",
                        "structure": "folder"
                    }
                }
            }
        }
        repo._save_config(data)
        
        # Test resolution
        output_config = repo.resolve_output_config("default")
        assert output_config["alias"] == "def_mod"
        assert output_config["structure"] == "folder"
        
        # Test missing key
        assert repo.resolve_output_config("missing") == {}

    def test_load_from_yaml_source(self, tmp_path, monkeypatch, cache_config):
        monkeypatch.chdir(tmp_path)
        
        # Create dummy YAML source
        yaml_source = tmp_path / "source_llm.yaml"
        yaml_data = {"source": "yaml"}
        with open(yaml_source, "w") as f:
            yaml.dump(yaml_data, f)
            
        # Initialize repo with source
        repo = JsonLLMConfigRepository(
            cache_config=cache_config,
            source_config_path=yaml_source
        )
        
        # Verify it converted to JSON
        config = repo.get_config()
        assert config["source"] == "yaml"
        
        # Verify persistence file
        json_file = tmp_path / ".Pravaha/config/llm_config.json"
        assert json_file.exists()
        with open(json_file, "r") as f:
            assert json.load(f)["source"] == "yaml"
