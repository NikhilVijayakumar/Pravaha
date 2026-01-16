import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import HTTPException
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager
from pravaha.domain.config.cache_config import CachePathConfig
from pravaha.domain.storage.protocol.storage_config_repository_protocol import StorageConfigRepositoryProtocol
from pravaha.domain.storage.repository.json_storage_config_repository import JsonStorageConfigRepository


class LocalStorageManager:
    def __init__(
        self, 
        defaults: Optional[dict[str, str]] = None, 
        config_path: Optional[Path] = None,
        cache_config: Optional[CachePathConfig] = None,
        config_repository: Optional[StorageConfigRepositoryProtocol] = None
    ):
        self.project_root = Path(os.getcwd())
        
        # Use configurable cache path (defaults to .Pravaha for backwards compatibility)
        if cache_config is None:
            cache_config = CachePathConfig.default()
        
        # Use provided repository or create default JSON repository
        if config_repository is None:
            config_repository = JsonStorageConfigRepository(cache_config)
        
        self.config_repository = config_repository
        
        # Caching Logic for external config files
        if config_path and config_path.exists():
            try:
                # Use repository to load and store config
                import json
                with open(config_path, 'r') as f:
                    external_config = json.load(f)
                self.config_repository.update_config(external_config)
            except Exception as e:
                # Log warning using Nibandha logger
                logger = PravphaLoggingManager.get_logger()
                logger.warning(f"Failed to cache Storage config from {config_path}: {e}")

        if defaults:
            self.defaults = defaults
        else:
            self.defaults = {
                "output": "output",
                "intermediate": "intermediate",
                "knowledge": "knowledge"
            }
        
        self._ensure_defaults()

    def _ensure_defaults(self):
        """Sets up default paths relative to project root if no config exists."""
        existing_config = self.config_repository.get_config()
        
        if not existing_config:
            # Create directories for defaults
            for path_str in self.defaults.values():
                (self.project_root / path_str).mkdir(parents=True, exist_ok=True)

            # Save defaults via repository
            self.config_repository.update_config(self.defaults)

    def update_config(self, output: str, intermediate: str, knowledge: str):
        """Allows API to override defaults with absolute or other relative paths."""
        config = {
            "output": str(Path(output)),
            "intermediate": str(Path(intermediate)),
            "knowledge": str(Path(knowledge))
        }
        self.config_repository.update_config(config)

    def get_path(self, category: str) -> Path:
        path_str = self.config_repository.get_path(category)
        
        if not path_str:
            raise HTTPException(status_code=400, detail=f"Category {category} missing.")

        path = Path(path_str)
        if not path.is_absolute():
            path = (self.project_root / path).resolve()
            
        if not path.exists():
            # Help the user by showing exactly where it's looking
            raise HTTPException(
                status_code=500,
                detail=f"Path for {category} not found at: {path.absolute()}"
            )
        return path

    def get_config(self) -> dict:
        """Returns the full current configuration."""
        return self.config_repository.get_config()
