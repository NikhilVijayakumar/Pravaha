"""
Tests for APIKeyMiddleware.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pravaha.domain.auth.middleware.api_key_middleware import APIKeyMiddleware
from pravaha.domain.auth.repository.json_access_key_repository import JsonAccessKeyRepository
from pravaha.domain.auth.model.module import PravahaModule
from pravaha.domain.config.cache_config import CachePathConfig

import tempfile
import shutil
from pathlib import Path


class TestAPIKeyMiddleware:
    """Test authentication middleware."""
    
    @pytest.fixture
    def temp_cache_config(self):
        """Create temporary cache directory."""
        temp_dir = tempfile.mkdtemp()
        cache_config = CachePathConfig.from_custom_root(Path(temp_dir))
        
        yield cache_config
        
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def repository(self, temp_cache_config):
        """Create repository."""
        return JsonAccessKeyRepository(cache_config=temp_cache_config)
    
    @pytest.fixture
    def test_app(self, repository):
        """Create test FastAPI app with middleware."""
        app = FastAPI()
        
        app.add_middleware(
            APIKeyMiddleware,
            repository=repository,
            exempt_paths=["/health", "/docs"]
        )
        
        @app.get("/health")
        async def health():
            return {"status": "ok"}
        
        @app.get("/api/storage/browse")
        async def storage_browse():
            return {"files": []}
        
        @app.get("/api/llm/config")
        async def llm_config():
            return {"models": {}}
        
        @app.get("/api/bot/run")
        async def bot_run():
            return {"result": "success"}
        
        return app
    
    @pytest.fixture
    def client(self, test_app):
        """Create test client."""
        return TestClient(test_app)
    
    def test_exempt_path_no_auth_required(self, client):
        """Test exempt paths don't require authentication."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_protected_path_requires_key(self, client):
        """Test protected paths require API key."""
        response = client.get("/api/storage/browse")
        assert response.status_code == 401
        assert "API key required" in response.json()["detail"]
    
    def test_valid_key_with_permission(self, client, repository):
        """Test valid key with correct permission grants access."""
        # Create key with STORAGE permission
        key = repository.create_key(
            name="Test",
            permissions=[PravahaModule.STORAGE]
        )
        
        # Request with key
        response = client.get(
            "/api/storage/browse",
            headers={"X-API-Key": key.key}
        )
        
        assert response.status_code == 200
    
    def test_valid_key_without_permission(self, client, repository):
        """Test valid key without required permission is denied."""
        # Create key with only STORAGE permission
        key = repository.create_key(
            name="Test",
            permissions=[PravahaModule.STORAGE]
        )
        
        # Try to access LLM endpoint
        response = client.get(
            "/api/llm/config",
            headers={"X-API-Key": key.key}
        )
        
        assert response.status_code == 403
        assert "llm" in response.json()["required_permission"]
        assert "storage" in response.json()["available_permissions"]
    
    def test_invalid_key(self, client):
        """Test invalid key is rejected."""
        response = client.get(
            "/api/storage/browse",
            headers={"X-API-Key": "invalid-key"}
        )
        
        assert response.status_code == 403
        assert "Invalid or inactive" in response.json()["detail"]
    
    def test_revoked_key(self, client, repository):
        """Test revoked key is rejected."""
        # Create and revoke key
        key = repository.create_key(
            name="Test",
            permissions=[PravahaModule.STORAGE]
        )
        
        repository.revoke_key(key.id)
        
        # Try to use
        response = client.get(
            "/api/storage/browse",
            headers={"X-API-Key": key.key}
        )
        
        assert response.status_code == 403
    
    def test_multiple_permissions(self, client, repository):
        """Test key with multiple permissions."""
        # Create key with multiple permissions
        key = repository.create_key(
            name="Multi",
            permissions=[PravahaModule.STORAGE, PravahaModule.LLM, PravahaModule.BOT]
        )
        
        # Should access all three
        assert client.get("/api/storage/browse", headers={"X-API-Key": key.key}).status_code == 200
        assert client.get("/api/llm/config", headers={"X-API-Key": key.key}).status_code == 200
        assert client.get("/api/bot/run", headers={"X-API-Key": key.key}).status_code == 200
