"""
JSON Storage Config Repository

Default JSON file-based implementation of StorageConfigRepositoryProtocol.
"""

import json
from pathlib import Path
from typing import Dict, Optional

from pravaha.domain.storage.protocol.storage_config_repository_protocol import StorageConfigRepositoryProtocol
from pravaha.domain.config.cache_config import CachePathConfig


class JsonStorageConfigRepository(StorageConfigRepositoryProtocol):
    """
    JSON file-based storage config repository.
    
    Stores storage paths in JSON file with get/update/get_path operations.
    """
    
    def __init__(self, cache_config: Optional[CachePathConfig] = None):
        """
        Initialize JSON repository.
        
        Args:
            cache_config: Cache configuration for file location
        """
        if cache_config is None:
            cache_config = CachePathConfig.default()
        
        self.config_dir = Path.cwd() / cache_config.get_storage_cache_dir()
        self.config_file = self.config_dir / "storage.json"
        
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize file if doesn't exist
        if not self.config_file.exists():
            self._save_config({})
    
    def _load_config(self) -> Dict[str, str]:
        """Load configuration from JSON file."""
        if not self.config_file.exists():
            return {}
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _save_config(self, config: Dict[str, str]) -> None:
        """Save configuration to JSON file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_config(self) -> Dict[str, str]:
        """Get storage paths configuration."""
        return self._load_config()
    
    def update_config(self, config: Dict[str, str]) -> None:
        """Update storage configuration."""
        # Load existing config
        existing = self._load_config()
        
        # Update with new values
        existing.update(config)
        
        # Save back
        self._save_config(existing)
    
    def get_path(self, category: str) -> str:
        """Get specific storage path by category."""
        config = self._load_config()
        return config.get(category, "")
