import pytest
from pathlib import Path
from pravaha.domain.config.cache_config import CachePathConfig

class TestCachePathConfig:
    """
    Unit tests for CachePathConfig.
    Target: src/nikhil/pravaha/domain/config/cache_config.py
    """

    def test_default_initialization(self):
        """[UT-CFG-001] Verify default initialization."""
        config = CachePathConfig.default()
        assert config.cache_root == Path(".Pravaha")
        assert config.get_storage_cache_dir() == Path(".Pravaha/config")
        assert config.get_llm_cache_dir() == Path(".Pravaha/config")
        assert config.get_workflow_cache_dir() == Path(".Pravaha/config")

    def test_custom_root(self):
        """[UT-CFG-002] Verify custom root factory."""
        root = Path("/tmp/custom")
        config = CachePathConfig.from_custom_root(root)
        
        assert config.cache_root == root
        assert config.get_storage_cache_dir() == root / "config"
        assert config.get_llm_cache_dir() == root / "config"

    def test_explicit_overrides(self):
        """[UT-CFG-003] Verify component-specific overrides."""
        root = Path("/tmp/base")
        storage_override = Path("/tmp/storage")
        
        config = CachePathConfig(
            cache_root=root,
            storage_cache_dir=storage_override
        )
        
        # Storage should leverage override
        assert config.get_storage_cache_dir() == storage_override
        
        # Others should fall back to root
        assert config.get_llm_cache_dir() == root / "config"
        assert config.get_workflow_cache_dir() == root / "config"

    def test_string_path_handling(self):
        """Verify handling of string input where Path is expected (if factory supports it)."""
        # from_custom_root supports str or Path
        config = CachePathConfig.from_custom_root("/tmp/str_path")
        assert isinstance(config.cache_root, Path)
        assert config.cache_root == Path("/tmp/str_path")
