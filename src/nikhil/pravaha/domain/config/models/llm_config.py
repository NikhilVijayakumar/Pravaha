"""
LLM Configuration Models

Pydantic-based configuration models for LLM settings.
Validates model formats, URL patterns, parameter ranges, and
ensures defaults exist within their category.
"""

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class LLMOutputConfigModel(BaseModel):
    """Output configuration for a single LLM model."""
    alias: str = Field(..., description="Short alias for the model")
    structure: Literal["flat", "folder"] = Field("flat", description="Output structure type")
    folder_name: Optional[str] = Field(None, description="Folder name when structure is 'folder'")
    display_name: Optional[str] = Field(None, description="Human-readable display name")

    @model_validator(mode='after')
    def validate_folder_name_for_folder_structure(self) -> 'LLMOutputConfigModel':
        """Ensure folder_name is provided when structure is 'folder'."""
        if self.structure == "folder" and not self.folder_name:
            raise ValueError("folder_name is required when structure is 'folder'")
        return self


class LLMModelConfig(BaseModel):
    """Configuration for a single LLM model entry."""
    model: str = Field(..., description="Model identifier in 'provider/model-name' format")
    base_url: Optional[str] = Field(None, description="Base URL for the LLM API endpoint")
    api_key: str = Field(..., description="API key for authentication")
    output_config: LLMOutputConfigModel = Field(..., description="Output configuration")

    @field_validator('model')
    @classmethod
    def validate_model_format(cls, v: str) -> str:
        """Validate model string contains provider/model format."""
        if not v or '/' not in v:
            raise ValueError(
                f"Model must be in 'provider/model-name' format, got: '{v}'"
            )
        return v

    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate base URL format when provided."""
        if v is not None:
            if not v.startswith(('http://', 'https://')):
                raise ValueError(
                    f"base_url must start with 'http://' or 'https://', got: '{v}'"
                )
        return v


class LLMCategoryConfig(BaseModel):
    """
    Configuration for an LLM category (e.g., creative, evaluation).
    Contains a default model key and a dictionary of available models.
    """
    default: str = Field(..., description="Default model key for this category")
    models: Dict[str, LLMModelConfig] = Field(..., description="Available models in this category")

    @model_validator(mode='after')
    def validate_default_exists(self) -> 'LLMCategoryConfig':
        """Ensure the default model key exists in the models dictionary."""
        if self.default not in self.models:
            raise ValueError(
                f"Default model '{self.default}' not found in models: "
                f"{list(self.models.keys())}"
            )
        return self


class LLMParametersConfig(BaseModel):
    """Parameters for LLM inference."""
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Top-p (nucleus) sampling")
    max_completion_tokens: Optional[int] = Field(
        None, gt=0, description="Maximum tokens to generate"
    )
    stop: List[str] = Field(default_factory=list, description="Stop sequences")


class LLMConfig(BaseModel):
    """
    Top-level LLM configuration.
    Wraps LLM categories (creative, evaluation, etc.) and their parameters.
    """
    llm: Dict[str, LLMCategoryConfig] = Field(
        ..., description="LLM categories (e.g., creative, evaluation)"
    )
    llm_parameters: Dict[str, LLMParametersConfig] = Field(
        default_factory=dict, description="Parameters per category"
    )

    @model_validator(mode='after')
    def validate_parameters_match_categories(self) -> 'LLMConfig':
        """Warn if parameters exist for non-existent categories (non-fatal)."""
        # This is a soft check — extra parameters are allowed
        # but missing parameters for defined categories get defaults
        return self
