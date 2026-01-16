"""
JSON LLM Config Repository

Default JSON file-based implementation of LLMConfigRepositoryProtocol.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from pravaha.domain.llm.protocol.llm_config_repository_protocol import LLMConfigRepositoryProtocol
from pravaha.domain.config.cache_config import CachePathConfig


class JsonLLMConfigRepository(LLMConfigRepositoryProtocol):
    """
    JSON file-based LLM config repository.
    
    Stores LLM configuration (originally from YAML) in JSON cache.
    """
    
    def __init__(
        self, 
        cache_config: Optional[CachePathConfig] = None,
        source_config_path: Optional[Path] = None
    ):
        """
        Initialize JSON repository.
        
        Args:
            cache_config: Cache configuration for file location
            source_config_path: Optional path to source YAML config to cache
        """
        if cache_config is None:
            cache_config = CachePathConfig.default()
        
        self.config_dir = Path.cwd() / cache_config.get_llm_cache_dir()
        self.config_file = self.config_dir / "llm_config.json"
        self.source_config_path = source_config_path
        
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load source config if provided
        if source_config_path:
            self._cache_source_config(source_config_path)
        elif not self.config_file.exists():
            self._save_config({})
    
    def _cache_source_config(self, source_path: Path) -> None:
        """Cache source YAML config to JSON."""
        if source_path.exists():
            with open(source_path, 'r') as f:
                if source_path.suffix in ['.yaml', '.yml']:
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            
            self._save_config(config or {})
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_file.exists():
            return {}
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to JSON file."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_config(self) -> Dict[str, Any]:
        """Get complete LLM configuration."""
        return self._load_config()
    
    def resolve_output_config(self, model_key: str) -> Dict[str, Any]:
        """
        Resolve output configuration for a specific model.
        
        Args:
            model_key: Model identifier (e.g., 'default', 'creative')
            
        Returns:
            Output configuration for the model
        """
        config = self._load_config()
        
        # Navigate to output config if structure exists
        if 'llm_config' in config:
            llm_configs = config['llm_config']
            if model_key in llm_configs:
                model_config = llm_configs[model_key]
                return model_config.get('output', {})
        
        return {}
