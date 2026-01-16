"""
E2E Scenario: Frontend Feature Discovery
Verifies that the API correctly reports available features based on key permissions.
"""

import pytest
from fastapi.testclient import TestClient

from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.auth.config.auth_config import AuthConfig
from pravaha.domain.auth.repository.json_access_key_repository import JsonAccessKeyRepository
from pravaha.domain.auth.model.module import PravahaModule
from pravaha.domain.config.cache_config import CachePathConfig

from enum import Enum

class MockTaskConfig:
    class UtilsType(str, Enum):
        TEST = "test"
    class ApplicationType(str, Enum):
        TEST = "test"
    class ExecutionTarget(str, Enum):
        LOCAL = "local"

class TestFrontendDiscoveryScenario:
    
    @pytest.fixture
    def app_client(self, tmp_path):
        """Setup app with auth enabled."""
        cache_config = CachePathConfig.from_custom_root(str(tmp_path))
        repo = JsonAccessKeyRepository(cache_config=cache_config)
        
        # Create a key with specific permissions
        key_obj = repo.create_key(
            name="Frontend Key",
            permissions=[PravahaModule.WORKFLOW, PravahaModule.LLM]
        )
        
        # Create another key with different permissions
        storage_key_obj = repo.create_key(
            name="Storage Key",
            permissions=[PravahaModule.STORAGE]
        )
        
        app = create_fastapi_app(
            bot_manager=None, 
            task_config=MockTaskConfig,
            storage_manager=None,
            auth_config=AuthConfig(enabled=True),
            access_key_repository=repo
        )
        
        return TestClient(app), key_obj.key, storage_key_obj.key

    def test_discovery_workflow_llm(self, app_client):
        """
        Scenario: Frontend with WORKFLOW+LLM key checks capabilities.
        Expected: Returns endpoints for Workflow/LLM. DOES NOT return Storage/Bot.
        """
        client, frontend_key, _ = app_client
        headers = {"X-API-Key": frontend_key}
        
        response = client.get("/api/auth/capabilities", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify Key Info
        assert data["key_name"] == "Frontend Key"
        
        # Verify Modules
        modules = data["available_modules"]
        assert "workflow" in modules
        assert "llm" in modules
        assert "storage" not in modules
        assert "bot" not in modules
        
        # Verify Endpoints Map
        endpoints = data["endpoints"]
        assert "workflow" in endpoints
        assert "llm" in endpoints
        assert "storage" not in endpoints
        assert len(endpoints["workflow"]) > 0

    def test_discovery_storage_only(self, app_client):
        """
        Scenario: Frontend with STORAGE key checks capabilities.
        Expected: Returns endpoints for Storage. DOES NOT return Workflow/LLM.
        """
        client, _, storage_key = app_client
        headers = {"X-API-Key": storage_key}
        
        response = client.get("/api/auth/capabilities", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        modules = data["available_modules"]
        assert "storage" in modules
        assert "workflow" not in modules
        
        endpoints = data["endpoints"]
        assert "storage" in endpoints
        assert "workflow" not in endpoints
