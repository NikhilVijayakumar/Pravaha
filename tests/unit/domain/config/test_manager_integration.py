"""
Integration tests for cache configuration with managers.

Verifies that managers properly use CachePathConfig.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from pravaha.domain.config.cache_config import CachePathConfig
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from pravaha.domain.llm.manager.llm_config_manager import LLMConfigManager
from pravaha.domain.workflow.manager.local_workflow_manager import LocalWorkflowManager


class TestStorageManagerWithCache:
    """Test LocalStorageManager with cache configuration."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        import os
        os.chdir(self.test_dir)
        
        yield
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_default_cache_path(self):
        """Verify storage manager uses .Pravaha by default."""
        manager = LocalStorageManager()
        
        expected_config_dir = Path.cwd() / ".Pravaha" / "config"
        assert manager.config_dir == expected_config_dir
        assert manager.config_file == expected_config_dir / "storage.json"
    
    def test_custom_cache_root(self):
        """Verify storage manager uses custom cache root."""
        cache_config = CachePathConfig.from_custom_root("custom_cache")
        manager = LocalStorageManager(cache_config=cache_config)
        
        expected_config_dir = Path.cwd() / "custom_cache" / "config"
        assert manager.config_dir == expected_config_dir
        assert manager.config_file == expected_config_dir / "storage.json"
    
    def test_component_override(self):
        """Verify storage manager uses component-specific override."""
        cache_config = CachePathConfig(
            cache_root=Path("base"),
            storage_cache_dir=Path("storage_cache")
        )
        manager = LocalStorageManager(cache_config=cache_config)
        
        expected_config_dir = Path.cwd() / "storage_cache"
        assert manager.config_dir == expected_config_dir


class TestLLMConfigManagerWithCache:
    """Test LLMConfigManager with cache configuration."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        import os
        os.chdir(self.test_dir)
        
        yield
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_default_cache_path(self):
        """Verify LLM manager uses .Pravaha by default."""
        manager = LLMConfigManager()
        
        expected_config_dir = Path.cwd() / ".Pravaha" / "config"
        assert manager.config_dir == expected_config_dir
        assert manager.config_file == expected_config_dir / "llm_config.json"
    
    def test_custom_cache_root(self):
        """Verify LLM manager uses custom cache root."""
        cache_config = CachePathConfig.from_custom_root("/tmp/llm_cache")
        manager = LLMConfigManager(cache_config=cache_config)
        
        expected_config_dir = Path.cwd() / Path("tmp/llm_cache/config")
        assert manager.config_dir == expected_config_dir
        assert manager.config_file == expected_config_dir / "llm_config.json"
    
    def test_component_override(self):
        """Verify LLM manager uses component-specific override."""
        cache_config = CachePathConfig(
            cache_root=Path("base"),
            llm_cache_dir=Path("llm_cache")
        )
        manager = LLMConfigManager(cache_config=cache_config)
        
        expected_config_dir = Path.cwd() / "llm_cache"
        assert manager.config_dir == expected_config_dir


class TestWorkflowManagerWithCache:
    """Test LocalWorkflowManager with cache configuration."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        import os
        os.chdir(self.test_dir)
        
        yield
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_default_cache_path(self):
        """Verify workflow manager uses .Pravaha by default."""
        manager = LocalWorkflowManager()
        
        expected_config_dir = Path.cwd() / ".Pravaha" / "config"
        assert manager.config_dir == expected_config_dir
        assert manager.config_file == expected_config_dir / "workflow.json"
    
    def test_custom_cache_root(self):
        """Verify workflow manager uses custom cache root."""
        cache_config = CachePathConfig.from_custom_root("workflow_cache")
        manager = LocalWorkflowManager(cache_config=cache_config)
        
        expected_config_dir = Path.cwd() / "workflow_cache" / "config"
        assert manager.config_dir == expected_config_dir
        assert manager.config_file == expected_config_dir / "workflow.json"
    
    def test_default_workflow_paths_custom_root(self):
        """Verify default workflow paths use custom cache root."""
        cache_config = CachePathConfig.from_custom_root("custom")
        manager = LocalWorkflowManager(cache_config=cache_config)
        
        # Default workflow paths should use cache_root
        assert manager.defaults["details"] == "custom/workflow/details"
        assert manager.defaults["run"] == "custom/workflow/run"
    
    def test_component_override(self):
        """Verify workflow manager uses component-specific override."""
        cache_config = CachePathConfig(
            cache_root=Path("base"),
            workflow_cache_dir=Path("wf_cache")
        )
        manager = LocalWorkflowManager(cache_config=cache_config)
        
        expected_config_dir = Path.cwd() / "wf_cache"
        assert manager.config_dir == expected_config_dir
        
        # Defaults should still use cache_root
        assert manager.defaults["details"] == "base/workflow/details"
        assert manager.defaults["run"] == "base/workflow/run"
