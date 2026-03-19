"""
LLM Configuration Manager

Manages LLM configurations with typed Pydantic models.
Supports loading from YAML/JSON with validation and model resolution.
"""

from pathlib import Path
from typing import Dict, Any, Optional

from pravaha.domain.llm.protocol.llm_config_protocol import LLMConfigManagerProtocol
from pravaha.domain.config.models.llm_config import LLMOutputConfigModel
from pravaha.domain.logging.manager.logging_manager import PravahaLoggingManager
from pravaha.domain.config.cache_config import CachePathConfig
from pravaha.domain.llm.protocol.llm_config_repository_protocol import LLMConfigRepositoryProtocol
from pravaha.domain.llm.repository.json_llm_config_repository import JsonLLMConfigRepository


class LLMConfigManager(LLMConfigManagerProtocol):
    def __init__(
        self,
        config_path: Optional[Path] = None,
        cache_config: Optional[CachePathConfig] = None,
        config_repository: Optional[LLMConfigRepositoryProtocol] = None,
    ):
        self.project_root = Path.cwd()

        # Use configurable cache path (defaults to .Pravaha for backwards compatibility)
        if cache_config is None:
            cache_config = CachePathConfig.default()

        # Use provided repository or create default JSON repository
        if config_repository is None:
            config_repository = JsonLLMConfigRepository(
                cache_config=cache_config, source_config_path=config_path
            )

        self.config_repository = config_repository

        # Load config into cache
        self._config_cache: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from repository."""
        try:
            self._config_cache = self.config_repository.get_config() or {}
        except Exception as e:
            logger = PravahaLoggingManager.get_logger()
            logger.error(f"Error loading LLM config: {e}")
            self._config_cache = {}

    def resolve_output_config(self, model_key: str) -> LLMOutputConfigModel:
        """
        Resolves output configuration for a model key.
        Searches recursively for 'models' -> {model_key}.
        Returns a validated LLMOutputConfigModel.
        """
        llm_block = self._config_cache.get("llm", {})

        # Normalize input key for comparison
        search_key = model_key.lower()

        for category, details in llm_block.items():
            if "models" in details:
                models = details["models"]
                for key, model_config in models.items():
                    # Check 1: Exact key match (or case-insensitive)
                    if key.lower() == search_key:
                        output_config = model_config.get("output_config", {})
                        return self._build_output_config(output_config, key)

                    # Check 2: Alias match from output_config
                    output_config = model_config.get("output_config", {})
                    alias = output_config.get("alias", "").lower()
                    if alias and alias == search_key:
                        return self._build_output_config(output_config, key)

                    # Check 3: Model specific name match (last part of model string)
                    model_str = model_config.get("model", "")
                    if model_str:
                        parts = model_str.rsplit("/", 1)
                        model_name = (
                            parts[-1].lower()
                            if len(parts) > 1
                            else model_str.lower()
                        )
                        if model_name == search_key:
                            return self._build_output_config(output_config, key)

        # Fallback if not found
        return LLMOutputConfigModel(
            alias=model_key,
            structure="flat",
            display_name=model_key.replace("_", " ").title(),
        )

    def _build_output_config(
        self, output_config: Dict[str, Any], default_key: str
    ) -> LLMOutputConfigModel:
        """Build a validated LLMOutputConfigModel from raw config dict."""
        try:
            return LLMOutputConfigModel(
                alias=output_config.get("alias", default_key),
                structure=output_config.get("structure", "flat"),
                folder_name=output_config.get("folder_name"),
                display_name=output_config.get("display_name", default_key),
            )
        except Exception:
            # Fallback if validation fails
            return LLMOutputConfigModel(
                alias=default_key,
                structure="flat",
                display_name=default_key,
            )

    def get_all_config(self) -> Dict[str, Any]:
        """Returns the complete LLM configuration."""
        return self._config_cache
