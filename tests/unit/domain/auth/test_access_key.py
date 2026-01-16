"""
Tests for AccessKey model and permission checking.
"""

import pytest
from datetime import datetime

from pravaha.domain.auth.model.access_key import AccessKey
from pravaha.domain.auth.model.module import PravahaModule


class TestAccessKey:
    """Test AccessKey model functionality."""
    
    def test_create_access_key(self):
        """Test creating an AccessKey with permissions."""
        key = AccessKey(
            id="test-id",
            key="hashed-key-value",
            name="Test Key",
            created_at=datetime.now(),
            permissions=[PravahaModule.STORAGE, PravahaModule.WORKFLOW]
        )
        
        assert key.id == "test-id"
        assert key.name == "Test Key"
        assert len(key.permissions) == 2
        assert key.is_active is True
    
    def test_has_permission(self):
        """Test permission checking for single module."""
        key = AccessKey(
            id="test-id",
            key="hashed-key",
            name="Test",
            created_at=datetime.now(),
            permissions=[PravahaModule.STORAGE, PravahaModule.LLM]
        )
        
        # Has permission
        assert key.has_permission(PravahaModule.STORAGE) is True
        assert key.has_permission(PravahaModule.LLM) is True
        
        # No permission
        assert key.has_permission(PravahaModule.BOT) is False
        assert key.has_permission(PravahaModule.WORKFLOW) is False
    
    def test_has_all_permissions(self):
        """Test checking for multiple permissions."""
        key = AccessKey(
            id="test-id",
            key="hashed-key",
            name="Test",
            created_at=datetime.now(),
            permissions=[PravahaModule.STORAGE, PravahaModule.WORKFLOW, PravahaModule.LLM]
        )
        
        # Has all
        assert key.has_all_permissions([PravahaModule.STORAGE, PravahaModule.LLM]) is True
        
        # Missing one
        assert key.has_all_permissions([PravahaModule.STORAGE, PravahaModule.BOT]) is False
        
        # Empty list
        assert key.has_all_permissions([]) is True
    
    def test_has_any_permission(self):
        """Test checking for any of multiple permissions."""
        key = AccessKey(
            id="test-id",
            key="hashed-key",
            name="Test",
            created_at=datetime.now(),
            permissions=[PravahaModule.STORAGE]
        )
        
        # Has one
        assert key.has_any_permission([PravahaModule.STORAGE, PravahaModule.BOT]) is True
        
        # Has none
        assert key.has_any_permission([PravahaModule.BOT, PravahaModule.WORKFLOW]) is False
        
        # Empty list
        assert key.has_any_permission([]) is False
    
    def test_serialization(self):
        """Test to_dict and from_dict."""
        original = AccessKey(
            id="test-id",
            key="hashed-key",
            name="Test Key",
            created_at=datetime(2026, 1, 16, 10, 0, 0),
            permissions=[PravahaModule.STORAGE, PravahaModule.LLM],
            description="Test description",
            is_active=True
        )
        
        # Serialize
        data = original.to_dict()
        
        assert data["id"] == "test-id"
        assert data["name"] == "Test Key"
        assert data["permissions"] == ["storage", "llm"]
        assert data["is_active"] is True
        
        # Deserialize
        restored = AccessKey.from_dict(data)
        
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.permissions == original.permissions
        assert restored.description == original.description


class TestPravahaModule:
    """Test PravahaModule enum."""
    
    def test_all_modules(self):
        """Test getting all available modules."""
        modules = PravahaModule.all_modules()
        
        assert len(modules) == 4
        assert PravahaModule.BOT in modules
        assert PravahaModule.LLM in modules
        assert PravahaModule.STORAGE in modules
        assert PravahaModule.WORKFLOW in modules
    
    def test_from_string(self):
        """Test parsing module from string."""
        assert PravahaModule.from_string("bot") == PravahaModule.BOT
        assert PravahaModule.from_string("llm") == PravahaModule.LLM
        assert PravahaModule.from_string("storage") == PravahaModule.STORAGE
        assert PravahaModule.from_string("workflow") == PravahaModule.WORKFLOW
    
    def test_from_string_case_insensitive(self):
        """Test case-insensitive parsing."""
        assert PravahaModule.from_string("BOT") == PravahaModule.BOT
        assert PravahaModule.from_string("Storage") == PravahaModule.STORAGE
        assert PravahaModule.from_string("WORKFLOW") == PravahaModule.WORKFLOW
    
    def test_from_string_invalid(self):
        """Test parsing invalid module raises ValueError."""
        with pytest.raises(ValueError, match="Invalid module"):
            PravahaModule.from_string("invalid_module")
    
    def test_module_values(self):
        """Test module enum values."""
        assert PravahaModule.BOT.value == "bot"
        assert PravahaModule.LLM.value == "llm"
        assert PravahaModule.STORAGE.value == "storage"
        assert PravahaModule.WORKFLOW.value == "workflow"
