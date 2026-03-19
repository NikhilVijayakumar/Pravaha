"""
Tests for AuthAPIProvider endpoints.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from datetime import datetime

from pravaha.domain.auth.provider.auth_api_provider import AuthAPIProvider
from pravaha.domain.auth.protocol.access_key_repository_protocol import AccessKeyRepositoryProtocol
from pravaha.domain.auth.model.access_key import AccessKey
from pravaha.domain.auth.model.module import PravahaModule


class TestAuthAPIProvider:
    """Test Authentication API endpoints."""
    
    @pytest.fixture
    def mock_repo(self):
        """Mock Key Repository."""
        return Mock(spec=AccessKeyRepositoryProtocol)
    
    @pytest.fixture
    def client(self, mock_repo):
        """Test Client with Auth Provider mounted."""
        provider = AuthAPIProvider(repository=mock_repo)
        
        app = FastAPI()
        app.include_router(provider.router, prefix="/api/auth")
        
        # Mock request state for capabilities endpoint
        # Because we're bypassing middleware in unit tests of the provider itself
        @app.middleware("http")
        async def mock_auth_middleware(request: Request, call_next):
            # Inject a fake key into state if header present
            if "X-Inject-Key" in request.headers:
                permissions = [PravahaModule.STORAGE]
                request.state.access_key = AccessKey(
                    id="current-key",
                    key="hashed",
                    name="Current Key",
                    permissions=permissions,
                    created_at=datetime.now(),
                    is_active=True,
                    last_used=None,
                    description=None
                )
            response = await call_next(request)
            return response
            
        return TestClient(app)
    
    def test_list_all_features(self, client):
        """Test listing features (public logic)."""
        response = client.get("/api/auth/features")
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "bot" in data
        assert "llm" in data
        assert "storage" in data
        assert "workflow" in data
        assert "description" in data["storage"]
        assert "endpoints" in data["storage"]
        
        # Verify NIBANDHA is NOT present (as per recent changes)
        assert "nibandha" not in data

    def test_create_key_success(self, client, mock_repo):
        """Test creating a key successfully."""
        # Setup mock return
        mock_key = AccessKey(
            id="new-id",
            key="raw-key-value",
            name="New Key",
            permissions=[PravahaModule.BOT],
            created_at=datetime.now(),
            is_active=True,
            last_used=None,
            description="Desc"
        )
        mock_repo.create_key.return_value = mock_key
        
        payload = {
            "name": "New Key",
            "description": "Desc",
            "permissions": ["bot"]
        }
        
        response = client.post("/api/auth/keys", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "new-id"
        assert data["key"] == "raw-key-value"  # Should return raw key on creation
        
        # Verify repo call
        mock_repo.create_key.assert_called_once()
        call_args = mock_repo.create_key.call_args[1]
        assert call_args["name"] == "New Key"
        assert call_args["permissions"] == [PravahaModule.BOT]

    def test_create_key_invalid_module(self, client, mock_repo):
        """Test creating key with invalid module raises 400."""
        payload = {
            "name": "Bad Key",
            "permissions": ["invalid_module"]
        }
        
        # Should be caught by Pydantic validation or our parser before hitting repo
        # Since we parse in the endpoint:
        response = client.post("/api/auth/keys", json=payload)
        assert response.status_code == 400
        assert "Invalid module" in response.json()["detail"]

    def test_list_keys(self, client, mock_repo):
        """Test listing keys masks the secret key."""
        mock_repo.list_keys.return_value = [
            AccessKey(
                id="1", key="should_be_hidden", name="Key 1", 
                permissions=[], created_at=datetime.now(), is_active=True, last_used=None, description=None
            )
        ]
        
        response = client.get("/api/auth/keys")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1
        assert data[0]["key"] is None  # Must be None/Hidden in list
        assert data[0]["id"] == "1"

    def test_revoke_key(self, client, mock_repo):
        """Test revoking a key."""
        response = client.delete("/api/auth/keys/target-id")
        
        assert response.status_code == 200
        mock_repo.revoke_key.assert_called_with("target-id")

    def test_get_capabilities(self, client):
        """Test getting capabilities for current key."""
        # Use our mock middleware to inject a key with STORAGE permission
        response = client.get(
            "/api/auth/capabilities",
            headers={"X-Inject-Key": "true"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["key_name"] == "Current Key"
        assert "storage" in data["available_modules"]
        assert "endpoints" in data
        assert len(data["endpoints"]["storage"]) > 0
        assert "llm" not in data["endpoints"]  # Should only show available modules
