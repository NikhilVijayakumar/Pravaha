"""
LLM Config Protocol

Protocol and typed models for LLM configuration management.
"""

from typing import Protocol, Dict, Any
from pravaha.domain.config.models.llm_config import LLMOutputConfigModel


class LLMConfigManagerProtocol(Protocol):
    def resolve_output_config(self, model_key: str) -> LLMOutputConfigModel:
        """
        Resolves output configuration for a model.
        """
        ...

    def get_all_config(self) -> Dict[str, Any]:
        """
        Returns the complete configuration dictionary.
        """
        ...
