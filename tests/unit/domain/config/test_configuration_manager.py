"""
Unit Tests for PravahaConfigurationManager

Tests loading from dict, JSON, YAML, and the default factory.
"""

import pytest
import json
import yaml
from pathlib import Path

from pravaha.domain.config.application.configuration_manager import (
    PravahaConfigurationManager,
)
from pravaha.domain.config.models.pravaha_app_config import PravahaAppConfig


class TestPravahaConfigurationManager:
    def test_create_default(self):
        config = PravahaConfigurationManager.create_default()
        assert isinstance(config, PravahaAppConfig)
        assert config.mode == "production"

    def test_create_default_with_name(self):
        config = PravahaConfigurationManager.create_default(app_name="CustomApp")
        assert config.name == "CustomApp"

    def test_load_from_dict_valid(self):
        data = {
            "name": "TestApp",
            "mode": "development",
            "logging_level": "DEBUG",
        }
        config = PravahaConfigurationManager.load_from_dict(data)
        assert config.name == "TestApp"
        assert config.mode == "development"
        assert config.logging_level == "DEBUG"

    def test_load_from_dict_partial(self):
        """Partial dict should use defaults for missing fields."""
        data = {"name": "PartialApp"}
        config = PravahaConfigurationManager.load_from_dict(data)
        assert config.name == "PartialApp"
        assert config.mode == "production"  # default

    def test_load_from_dict_empty(self):
        """Empty dict should produce all-defaults config."""
        config = PravahaConfigurationManager.load_from_dict({})
        assert isinstance(config, PravahaAppConfig)

    def test_load_from_dict_invalid_graceful_fallback(self):
        """Invalid data should fall back to defaults gracefully."""
        data = "not_a_dict"
        config = PravahaConfigurationManager.load_from_dict(data)
        assert isinstance(config, PravahaAppConfig)

    def test_load_from_json(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_data = {"name": "JsonApp", "mode": "development"}
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        config = PravahaConfigurationManager.load_from_json(config_file)
        assert config.name == "JsonApp"
        assert config.mode == "development"

    def test_load_from_json_missing_file(self):
        with pytest.raises(FileNotFoundError):
            PravahaConfigurationManager.load_from_json("/nonexistent/config.json")

    def test_load_from_yaml(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_data = {"name": "YamlApp", "logging_level": "DEBUG"}
        config_file.write_text(
            yaml.dump(config_data, default_flow_style=False), encoding="utf-8"
        )

        config = PravahaConfigurationManager.load_from_yaml(config_file)
        assert config.name == "YamlApp"
        assert config.logging_level == "DEBUG"

    def test_load_from_yaml_missing_file(self):
        with pytest.raises(FileNotFoundError):
            PravahaConfigurationManager.load_from_yaml("/nonexistent/config.yaml")

    def test_load_from_yaml_with_nested_config(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_data = {
            "name": "NestedApp",
            "storage": {
                "output": "/custom/output",
                "intermediate": "/custom/intermediate",
                "knowledge": "/custom/knowledge",
            },
            "auth": {"enabled": False},
        }
        config_file.write_text(
            yaml.dump(config_data, default_flow_style=False), encoding="utf-8"
        )

        config = PravahaConfigurationManager.load_from_yaml(config_file)
        assert config.name == "NestedApp"
        assert config.storage.output == "/custom/output"
        assert config.auth.enabled is False
