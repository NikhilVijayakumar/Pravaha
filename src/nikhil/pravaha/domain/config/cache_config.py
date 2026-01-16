"""
Cache Path Configuration

Provides centralized cache path configuration for Pravaha components,
allowing clients to customize cache directories instead of hardcoding `.Pravaha`.
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class CachePathConfig:
    """
    Centralized cache path configuration for Pravaha components.
    
    Allows clients to customize where Pravaha stores cached configurations
    instead of hardcoding `.Pravaha` directory.
    
    Usage Examples:
        # Default (uses .Pravaha)
        config = CachePathConfig.default()
        
        # Custom root directory
        config = CachePathConfig.from_custom_root("/var/lib/myapp/pravaha")
        
        # Per-component customization
        config = CachePathConfig(
            cache_root=Path("/var/lib/myapp"),
            storage_cache_dir=Path("/var/lib/myapp/storage"),
            llm_cache_dir=Path("/var/lib/myapp/llm"),
            workflow_cache_dir=Path("/var/lib/myapp/workflows")
        )
    """
    
    # Base cache directory (default: .Pravaha)
    cache_root: Path = Path(".Pravaha")
    
    # Component-specific overrides (optional)
    storage_cache_dir: Optional[Path] = None
    llm_cache_dir: Optional[Path] = None
    workflow_cache_dir: Optional[Path] = None
    
    def get_storage_cache_dir(self) -> Path:
        """
        Get storage cache directory path.
        
        Returns:
            Path to storage cache directory (defaults to {cache_root}/config)
        """
        return self.storage_cache_dir or (self.cache_root / "config")
    
    def get_llm_cache_dir(self) -> Path:
        """
        Get LLM cache directory path.
        
        Returns:
            Path to LLM cache directory (defaults to {cache_root}/config)
        """
        return self.llm_cache_dir or (self.cache_root / "config")
    
    def get_workflow_cache_dir(self) -> Path:
        """
        Get workflow cache directory path.
        
        Returns:
            Path to workflow cache directory (defaults to {cache_root}/config)
        """
        return self.workflow_cache_dir or (self.cache_root / "config")
    
    @staticmethod
    def default() -> 'CachePathConfig':
        """
        Create default cache configuration using .Pravaha directory.
        
        This maintains backwards compatibility with existing deployments.
        
        Returns:
            CachePathConfig with default settings
        """
        return CachePathConfig(cache_root=Path(".Pravaha"))
    
    @staticmethod
    def from_custom_root(root: str | Path) -> 'CachePathConfig':
        """
        Create cache configuration with custom root directory.
        
        All component cache directories will be placed under {root}/config
        unless explicitly overridden with component-specific paths.
        
        Args:
            root: Custom root directory path (string or Path object)
            
        Returns:
            CachePathConfig with custom root
            
        Example:
            config = CachePathConfig.from_custom_root("/var/lib/myapp/pravaha")
            # Results in:
            # - Storage: /var/lib/myapp/pravaha/config/storage.json
            # - LLM: /var/lib/myapp/pravaha/config/llm_config.json
            # - Workflow: /var/lib/myapp/pravaha/config/workflow.json
        """
        return CachePathConfig(cache_root=Path(root))
