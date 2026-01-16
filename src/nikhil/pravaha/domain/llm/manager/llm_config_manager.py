"""
LLM Configuration Manager.

Handles loading and resolving LLM configurations.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from pravaha.domain.logging.manager.logging_manager import PravahaLoggingManager
from pravaha.domain.config.cache_config import CachePathConfig

class LLMConfigManager:
    """Manager for LLM Configuration."""
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        cache_config: Optional[CachePathConfig] = None
    ):
        self.config_path = config_path
        self.cache_config = cache_config
        self.logger = PravahaLoggingManager.get_logger()
        self._config_cache: Optional[Dict[str, Any]] = None

    def get_config(self) -> Dict[str, Any]:
        """
        Get complete LLM configuration.
        """
        if self._config_cache:
            return self._config_cache
            
        if not self.config_path or not self.config_path.exists():
            self.logger.warning(f"LLM config path not set or invalid: {self.config_path}")
            return {}
            
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config_cache = yaml.safe_load(f) or {}
            return self._config_cache
        except Exception as e:
            self.logger.error(f"Failed to load LLM config: {e}")
            return {}

    def resolve_output_config(self, model_key: str) -> Dict[str, Any]:
        """
        Resolve output configuration for a specific model.
        """
        config = self.get_config()
        # Basic implementation: Look for model in config or return default
        models = config.get("models", {})
        if model_key in models:
            return models[model_key]
            
        # Default fallback
        return {"display_name": model_key}
