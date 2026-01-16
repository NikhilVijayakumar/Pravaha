"""
E2E Scenario: Secure/Insecure Toggle
Verifies that AuthConfig.enabled controls the authentication wall.
"""

import pytest
from fastapi.testclient import TestClient

from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.auth.config.auth_config import AuthConfig
from pravaha.domain.auth.repository.json_access_key_repository import JsonAccessKeyRepository
from pravaha.domain.config.cache_config import CachePathConfig

from enum import Enum

class MockTaskConfig:
    class UtilsType(str, Enum):
        TEST = "test"
    class ApplicationType(str, Enum):
        TEST = "test"
    class ExecutionTarget(str, Enum):
        LOCAL = "local"

class TestAuthToggleScenario:
    
    @pytest.fixture
    def setup_envs(self, tmp_path):
        """Setup two clients: one secure, one insecure."""
        cache_config = CachePathConfig.from_custom_root(str(tmp_path))
        repo = JsonAccessKeyRepository(cache_config=cache_config)
        
        # Secure App
        secure_app = create_fastapi_app(
            bot_manager=None, task_config=MockTaskConfig, storage_manager=None,
            auth_config=AuthConfig(enabled=True),
            access_key_repository=repo
        )
        
        # Insecure App
        insecure_app = create_fastapi_app(
            bot_manager=None, task_config=MockTaskConfig, storage_manager=None,
            auth_config=AuthConfig(enabled=False),
            access_key_repository=repo
        )
        
        return TestClient(secure_app), TestClient(insecure_app)

    def test_access_toggle(self, setup_envs):
        """
        Scenario:
        1. Access /api/storage without key on Insecure App -> Success (200/404 but NOT 401)
        2. Access /api/storage without key on Secure App -> Fail (401)
        """
        secure_client, insecure_client = setup_envs
        
        # Note: Since we pass None for managers, success might be 500 or 404, 
        # but what matters is it is NOT 401/403.
        # Ideally we hit an endpoint that exists even without managers, but storage endpoints need manager.
        # Let's hit /health - wait, /health is exempt anyway.
        # Let's hit /api/auth/features - this exists in both? 
        # No, AuthProvider is also optional? Yes usually.
        # But create_fastapi_app adds check_api_key globally.
        
        # Let's try to hit a text endpoint. We can't rely on 200 OK because managers are None.
        # We rely on status_code behavior.
        
        target_path = "/api/storage/browse/output"
        
        # Insecure check
        resp_insecure = insecure_client.get(target_path)
        # Should NOT be 401/403. Likely 500 (Manager None) or 404 (Router not mounted?)
        # If storage_manager is None, create_fastapi_app might not mount storage router.
        # Let's check logic... 
        # "if storage_manager: app.include_router..."
        # So path won't exist. It will be 404.
        
        assert resp_insecure.status_code != 401
        assert resp_insecure.status_code != 403
        
        # Secure check
        # Even if path doesn't exist (404), Auth Middleware runs BEFORE routing?
        # Typically Middleware runs dispatch.
        # If 404, Starlette router handles it. Middleware sees request.
        # Path matching mapping needs to know module.
        # "/api/storage" -> STORAGE.
        
        resp_secure = secure_client.get(target_path)
        assert resp_secure.status_code == 401
