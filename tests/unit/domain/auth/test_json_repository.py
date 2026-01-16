"""
Tests for JsonAccessKeyRepository.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from pravaha.domain.auth.repository.json_access_key_repository import JsonAccessKeyRepository
from pravaha.domain.auth.model.module import PravahaModule
from pravaha.domain.config.cache_config import CachePathConfig


class TestJsonAccessKeyRepository:
    """Test JSON access key repository."""
    
    @pytest.fixture
    def temp_cache_config(self):
        """Create temporary cache directory for testing."""
        temp_dir = tempfile.mkdtemp()
        cache_config = CachePathConfig.from_custom_root(Path(temp_dir))
        
        yield cache_config
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def repository(self, temp_cache_config):
        """Create repository with temp config."""
        return JsonAccessKeyRepository(cache_config=temp_cache_config)
    
    def test_create_key(self, repository):
        """Test creating a new API key."""
        key = repository.create_key(
            name="Test Key",
            description="Test description",
            permissions=[PravahaModule.STORAGE, PravahaModule.LLM]
        )
        
        assert key.id is not None
        assert key.name == "Test Key"
        assert key.description == "Test description"
        assert len(key.key) > 0  # Raw key returned
        assert len(key.permissions) == 2
        assert PravahaModule.STORAGE in key.permissions
        assert PravahaModule.LLM in key.permissions
    
    def test_create_key_with_all_permissions(self, repository):
        """Test creating key with all module permissions."""
        key = repository.create_key(
            name="Admin Key",
            permissions=PravahaModule.all_modules()
        )
        
        assert len(key.permissions) == 4
        assert key.has_permission(PravahaModule.BOT)
        assert key.has_permission(PravahaModule.STORAGE)
    
    def test_validate_key(self, repository):
        """Test key validation."""
        # Create key
        key = repository.create_key(
            name="Test",
            permissions=[PravahaModule.STORAGE]
        )
        
        raw_key = key.key
        
        # Validate with correct key
        assert repository.validate_key(raw_key) is True
        
        # Validate with wrong key
        assert repository.validate_key("wrong-key") is False
    
    def test_get_key_by_value(self, repository):
        """Test retrieving key by value."""
        # Create key
        created_key = repository.create_key(
            name="Test",
            permissions=[PravahaModule.LLM]
        )
        
        raw_key = created_key.key
        
        # Retrieve
        retrieved = repository.get_key_by_value(raw_key)
        
        assert retrieved is not None
        assert retrieved.id == created_key.id
        assert retrieved.name == "Test"
        assert PravahaModule.LLM in retrieved.permissions
    
    def test_list_keys(self, repository):
        """Test listing all keys."""
        # Create multiple keys
        repository.create_key("Key 1", permissions=[PravahaModule.STORAGE])
        repository.create_key("Key 2", permissions=[PravahaModule.LLM])
        repository.create_key("Key 3", permissions=[PravahaModule.WORKFLOW])
        
        # List
        keys = repository.list_keys()
        
        assert len(keys) == 3
        assert all(k.key == "***HIDDEN***" for k in keys)  # Keys are masked
    
    def test_revoke_key(self, repository):
        """Test revoking a key."""
        # Create key
        key = repository.create_key(
            name="To Revoke",
            permissions=[PravahaModule.STORAGE]
        )
        
        raw_key = key.key
        
        # Revoke
        repository.revoke_key(key.id)
        
        # Should not validate anymore
        assert repository.validate_key(raw_key) is False
        
        # Should not be in active list
        active_keys = repository.list_keys(include_inactive=False)
        assert not any(k.id == key.id for k in active_keys)
        
        # Should be in full list
        all_keys = repository.list_keys(include_inactive=True)
        assert any(k.id == key.id for k in all_keys)
    
    def test_update_last_used(self, repository):
        """Test updating last used timestamp."""
        # Create key
        key = repository.create_key(
            name="Test",
            permissions=[PravahaModule.STORAGE]
        )
        
        assert key.last_used is None
        
        # Update
        repository.update_last_used(key.id)
        
        # Retrieve and check
        updated = repository.get_key_by_id(key.id)
        assert updated.last_used is not None
    
    def test_get_key_by_id(self, repository):
        """Test retrieving key by ID."""
        # Create key
        created = repository.create_key(
            name="Test",
            permissions=[PravahaModule.WORKFLOW]
        )
        
        # Retrieve
        retrieved = repository.get_key_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test"
        assert retrieved.key == "***HIDDEN***"  # Masked
    
    def test_key_persistence(self, temp_cache_config):
        """Test keys persist across repository instances."""
        # Create in first instance
        repo1 = JsonAccessKeyRepository(cache_config=temp_cache_config)
        key = repo1.create_key(
            name="Persistent",
            permissions=[PravahaModule.STORAGE]
        )
        
        # Read in second instance
        repo2 = JsonAccessKeyRepository(cache_config=temp_cache_config)
        retrieved = repo2.get_key_by_id(key.id)
        
        assert retrieved is not None
        assert retrieved.name == "Persistent"
