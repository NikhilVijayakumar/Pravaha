"""
Unit Tests for LLM Configuration Models

Tests validation logic for LLMOutputConfigModel, LLMModelConfig,
LLMCategoryConfig, LLMParametersConfig, and LLMConfig.
"""

import pytest
from pydantic import ValidationError

from pravaha.domain.config.models.llm_config import (
    LLMOutputConfigModel,
    LLMModelConfig,
    LLMCategoryConfig,
    LLMParametersConfig,
    LLMConfig,
)


# --- LLMOutputConfigModel Tests ---

class TestLLMOutputConfigModel:
    def test_valid_flat_structure(self):
        config = LLMOutputConfigModel(alias="gemma-3", structure="flat")
        assert config.alias == "gemma-3"
        assert config.structure == "flat"
        assert config.folder_name is None

    def test_valid_folder_structure(self):
        config = LLMOutputConfigModel(
            alias="gemma-3", structure="folder", folder_name="gemma"
        )
        assert config.folder_name == "gemma"

    def test_folder_structure_requires_folder_name(self):
        with pytest.raises(ValidationError, match="folder_name is required"):
            LLMOutputConfigModel(alias="test", structure="folder")

    def test_invalid_structure_value(self):
        with pytest.raises(ValidationError):
            LLMOutputConfigModel(alias="test", structure="invalid")


# --- LLMModelConfig Tests ---

class TestLLMModelConfig:
    def test_valid_model_config(self):
        config = LLMModelConfig(
            model="gemini/gemini-2.5-flash",
            api_key="test-key",
            output_config=LLMOutputConfigModel(alias="gemini", structure="flat"),
        )
        assert config.model == "gemini/gemini-2.5-flash"
        assert config.base_url is None

    def test_valid_with_base_url(self):
        config = LLMModelConfig(
            model="lm_studio/gemma-3-12b-it",
            base_url="http://localhost:1234/v1",
            api_key="lm_studio",
            output_config=LLMOutputConfigModel(
                alias="gemma-3-12b", structure="folder", folder_name="gemma"
            ),
        )
        assert config.base_url == "http://localhost:1234/v1"

    def test_invalid_model_format_no_slash(self):
        with pytest.raises(ValidationError, match="provider/model-name"):
            LLMModelConfig(
                model="just-a-name",
                api_key="key",
                output_config=LLMOutputConfigModel(alias="test", structure="flat"),
            )

    def test_invalid_base_url(self):
        with pytest.raises(ValidationError, match="http://"):
            LLMModelConfig(
                model="provider/model",
                base_url="ftp://invalid",
                api_key="key",
                output_config=LLMOutputConfigModel(alias="test", structure="flat"),
            )

    def test_missing_required_api_key(self):
        with pytest.raises(ValidationError):
            LLMModelConfig(
                model="provider/model",
                output_config=LLMOutputConfigModel(alias="test", structure="flat"),
            )


# --- LLMCategoryConfig Tests ---

class TestLLMCategoryConfig:
    def _make_model(self, alias: str = "test"):
        return LLMModelConfig(
            model="provider/model-name",
            api_key="key",
            output_config=LLMOutputConfigModel(alias=alias, structure="flat"),
        )

    def test_valid_category(self):
        config = LLMCategoryConfig(
            default="gpt",
            models={"gpt": self._make_model("gpt"), "gemma": self._make_model("gemma")},
        )
        assert config.default == "gpt"
        assert len(config.models) == 2

    def test_default_not_in_models(self):
        with pytest.raises(ValidationError, match="not found in models"):
            LLMCategoryConfig(
                default="nonexistent",
                models={"gpt": self._make_model("gpt")},
            )


# --- LLMParametersConfig Tests ---

class TestLLMParametersConfig:
    def test_valid_parameters(self):
        config = LLMParametersConfig(temperature=0.8, top_p=0.9)
        assert config.temperature == 0.8
        assert config.max_completion_tokens is None
        assert config.stop == []

    def test_temperature_out_of_range(self):
        with pytest.raises(ValidationError):
            LLMParametersConfig(temperature=3.0, top_p=0.9)

    def test_top_p_out_of_range(self):
        with pytest.raises(ValidationError):
            LLMParametersConfig(temperature=0.5, top_p=1.5)

    def test_with_stop_sequences(self):
        config = LLMParametersConfig(
            temperature=0.0, top_p=0.5, stop=["###"]
        )
        assert config.stop == ["###"]


# --- LLMConfig Tests ---

class TestLLMConfig:
    def _make_category(self):
        model = LLMModelConfig(
            model="provider/model-name",
            api_key="key",
            output_config=LLMOutputConfigModel(alias="test", structure="flat"),
        )
        return LLMCategoryConfig(default="test_model", models={"test_model": model})

    def test_valid_llm_config(self):
        config = LLMConfig(
            llm={"creative": self._make_category()},
            llm_parameters={"creative": LLMParametersConfig(temperature=0.8, top_p=0.9)},
        )
        assert "creative" in config.llm
        assert "creative" in config.llm_parameters

    def test_empty_parameters_allowed(self):
        config = LLMConfig(llm={"creative": self._make_category()})
        assert config.llm_parameters == {}
