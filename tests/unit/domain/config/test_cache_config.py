"""
Tests for CachePathConfig

Verifies cache path configuration defaults, custom paths, and component overrides.
"""

import pytest
from pathlib import Path

from pravaha.domain.config.cache_config import CachePathConfig


class TestCachePathConfigDefaults:
    """Test default cache configuration."""
    
    def test_default_config(self):
        """Verify default configuration uses .Pravaha."""
        config = CachePathConfig.default()
        
        assert config.cache_root == Path(".Pravaha")
        assert config.storage_cache_dir is None
        assert config.llm_cache_dir is None
        assert config.workflow_cache_dir is None
    
    def test_default_cache_directories(self):
        """Verify default cache directories resolve to .Pravaha/config."""
        config = CachePathConfig.default()
        
        assert config.get_storage_cache_dir() == Path(".Pravaha/config")
        assert config.get_llm_cache_dir() == Path(".Pravaha/config")
        assert config.get_workflow_cache_dir() == Path(".Pravaha/config")


class TestCachePathConfigCustomRoot:
    """Test custom root directory configuration."""
    
    def test_custom_root_from_string(self):
        """Verify custom root can be created from string path."""
        config = CachePathConfig.from_custom_root("/var/lib/myapp/pravaha")
        
        assert config.cache_root == Path("/var/lib/myapp/pravaha")
        assert config.get_storage_cache_dir() == Path("/var/lib/myapp/pravaha/config")
        assert config.get_llm_cache_dir() == Path("/var/lib/myapp/pravaha/config")
        assert config.get_workflow_cache_dir() == Path("/var/lib/myapp/pravaha/config")
    
    def test_custom_root_from_path(self):
        """Verify custom root can be created from Path object."""
        root = Path("/custom/path")
        config = CachePathConfig.from_custom_root(root)
        
        assert config.cache_root == Path("/custom/path")
        assert config.get_storage_cache_dir() == Path("/custom/path/config")
    
    def test_custom_root_relative_path(self):
        """Verify custom root works with relative paths."""
        config = CachePathConfig.from_custom_root("data/pravaha")
        
        assert config.cache_root == Path("data/pravaha")
        assert config.get_storage_cache_dir() == Path("data/pravaha/config")


class TestCachePathConfigComponentOverrides:
    """Test component-specific cache directory overrides."""
    
    def test_storage_override(self):
        """Verify storage cache directory can be overridden."""
        config = CachePathConfig(
            cache_root=Path("/base"),
            storage_cache_dir=Path("/custom/storage")
        )
        
        assert config.get_storage_cache_dir() == Path("/custom/storage")
        # Others should use default
        assert config.get_llm_cache_dir() == Path("/base/config")
        assert config.get_workflow_cache_dir() == Path("/base/config")
    
    def test_llm_override(self):
        """Verify LLM cache directory can be overridden."""
        config = CachePathConfig(
            cache_root=Path("/base"),
            llm_cache_dir=Path("/custom/llm")
        )
        
        assert config.get_llm_cache_dir() == Path("/custom/llm")
        # Others should use default
        assert config.get_storage_cache_dir() == Path("/base/config")
        assert config.get_workflow_cache_dir() == Path("/base/config")
    
    def test_workflow_override(self):
        """Verify workflow cache directory can be overridden."""
        config = CachePathConfig(
            cache_root=Path("/base"),
            workflow_cache_dir=Path("/custom/workflow")
        )
        
        assert config.get_workflow_cache_dir() == Path("/custom/workflow")
        # Others should use default
        assert config.get_storage_cache_dir() == Path("/base/config")
        assert config.get_llm_cache_dir() == Path("/base/config")
    
    def test_all_overrides(self):
        """Verify all components can have custom directories."""
        config = CachePathConfig(
            cache_root=Path("/base"),
            storage_cache_dir=Path("/storage"),
            llm_cache_dir=Path("/llm"),
            workflow_cache_dir=Path("/workflow")
        )
        
        assert config.get_storage_cache_dir() == Path("/storage")
        assert config.get_llm_cache_dir() == Path("/llm")
        assert config.get_workflow_cache_dir() == Path("/workflow")


class TestCachePathConfigDataclass:
    """Test dataclass behavior."""
    
    def test_dataclass_creation(self):
        """Verify CachePathConfig can be created as dataclass."""
        config = CachePathConfig(cache_root=Path("/test"))
        
        assert isinstance(config, CachePathConfig)
        assert config.cache_root == Path("/test")
    
    def test_dataclass_defaults(self):
        """Verify dataclass has correct defaults."""
        config = CachePathConfig()
        
        assert config.cache_root == Path(".Pravaha")
        assert config.storage_cache_dir is None
        assert config.llm_cache_dir is None
        assert config.workflow_cache_dir is None
    
    def test_equality(self):
        """Verify two configs with same values are equal."""
        config1 = CachePathConfig.default()
        config2 = CachePathConfig.default()
        
        assert config1 == config2
    
    def test_inequality(self):
        """Verify configs with different values are not equal."""
        config1 = CachePathConfig.default()
        config2 = CachePathConfig.from_custom_root("/custom")
        
        assert config1 != config2
