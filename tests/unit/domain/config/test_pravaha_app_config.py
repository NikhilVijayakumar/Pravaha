"""
Unit Tests for PravahaAppConfig

Tests default construction, partial config, path resolution,
and the composite config model behavior.
"""

import pytest
from pydantic import ValidationError
from pathlib import Path

from pravaha.domain.config.models.pravaha_app_config import PravahaAppConfig
from pravaha.domain.config.models.storage_config import StorageConfig
from pravaha.domain.config.models.workflow_config import WorkflowConfig
from pravaha.domain.auth.config.auth_config import AuthConfig
from pravaha.domain.config.cache_config import CachePathConfig


class TestPravahaAppConfig:
    def test_default_construction(self):
        """All defaults should produce a valid config."""
        config = PravahaAppConfig()
        assert config.mode == "production"
        assert config.logging_level == "INFO"
        assert config.llm is None
        assert isinstance(config.storage, StorageConfig)
        assert isinstance(config.workflow, WorkflowConfig)
        assert isinstance(config.auth, AuthConfig)
        assert isinstance(config.cache, CachePathConfig)

    def test_custom_name_and_mode(self):
        config = PravahaAppConfig(name="TestApp", mode="development")
        assert config.name == "TestApp"
        assert config.mode == "development"

    def test_path_resolution_defaults(self):
        """Default storage/workflow paths should be resolved relative to cache_root."""
        config = PravahaAppConfig()
        cache_root = str(config.cache.cache_root)
        assert config.storage.output == f"{cache_root}/output"
        assert config.storage.intermediate == f"{cache_root}/intermediate"
        assert config.storage.knowledge == f"{cache_root}/knowledge"
        assert config.workflow.details_path == f"{cache_root}/workflow/details"
        assert config.workflow.run_path == f"{cache_root}/workflow/run"

    def test_custom_storage_not_overridden(self):
        """Custom paths should NOT be overridden by default resolution."""
        config = PravahaAppConfig(
            storage=StorageConfig(output="/custom/output")
        )
        assert config.storage.output == "/custom/output"

    def test_custom_cache_root(self):
        """Paths should resolve relative to custom cache_root."""
        config = PravahaAppConfig(
            cache=CachePathConfig(cache_root=Path("/var/lib/app"))
        )
        assert config.storage.output == "/var/lib/app/output"

    def test_auth_embedded(self):
        config = PravahaAppConfig(
            auth=AuthConfig(enabled=False, exempt_paths=["/health"])
        )
        assert config.auth.enabled is False
        assert config.auth.exempt_paths == ["/health"]


class TestStorageConfig:
    def test_defaults(self):
        config = StorageConfig()
        assert config.output == "output"
        assert config.intermediate == "intermediate"
        assert config.knowledge == "knowledge"


class TestWorkflowConfig:
    def test_defaults(self):
        config = WorkflowConfig()
        assert config.details_path == "workflow/details"
        assert config.run_path == "workflow/run"


class TestAuthConfig:
    def test_default_factory(self):
        config = AuthConfig.default()
        assert config.enabled is True

    def test_disabled_factory(self):
        config = AuthConfig.disabled()
        assert config.enabled is False

    def test_invalid_exempt_path(self):
        with pytest.raises(ValidationError, match="must start with '/'"):
            AuthConfig(exempt_paths=["no-leading-slash"])


class TestCachePathConfig:
    def test_default_factory(self):
        config = CachePathConfig.default()
        assert config.cache_root == Path(".Pravaha")

    def test_custom_root(self):
        config = CachePathConfig.from_custom_root("/var/lib/myapp")
        assert config.cache_root == Path("/var/lib/myapp")

    def test_get_storage_cache_dir_default(self):
        config = CachePathConfig.default()
        assert config.get_storage_cache_dir() == Path(".Pravaha/config")

    def test_get_storage_cache_dir_override(self):
        config = CachePathConfig(
            cache_root=Path(".Pravaha"),
            storage_cache_dir=Path("/custom/storage"),
        )
        assert config.get_storage_cache_dir() == Path("/custom/storage")
