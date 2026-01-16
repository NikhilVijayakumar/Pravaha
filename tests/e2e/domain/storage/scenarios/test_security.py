"""
E2E Scenario: Storage and Path Security
Verifies that path traversal attacks are blocked.
"""

import pytest
from fastapi.testclient import TestClient

from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from pravaha.domain.config.cache_config import CachePathConfig
from pravaha.domain.auth.config.auth_config import AuthConfig

# Mock Task Config
from enum import Enum
class MockTaskConfig:
    class UtilsType(str, Enum):
        TEST = "test"
    class ApplicationType(str, Enum):
        TEST = "test"
    class ExecutionTarget(str, Enum):
        LOCAL = "local"

class TestStorageSecurityScenario:
    
    @pytest.fixture
    def client(self, tmp_path):
        root = tmp_path / "pravaha_root"
        cache_config = CachePathConfig.from_custom_root(str(root))
        
        storage_mgr = LocalStorageManager(
            defaults={"knowledge": str(root / "knowledge")},
            cache_config=cache_config
        )
        
        app = create_fastapi_app(
            bot_manager=None,
            task_config=MockTaskConfig,
            storage_manager=storage_mgr,
            auth_config=AuthConfig(enabled=False),
            access_key_repository=None
        )
        return TestClient(app)

    def test_path_traversal_attack(self, client):
        """
        Attempt to read /etc/passwd via traversal.
        Should return 400 or 403.
        """
        # Note: The actual path doesn't need to exist for Validator to reject it.
        # We check if it rejects the PATTERN.
        
        traversal_path = "../../../../etc/passwd"
        
        # Try Browse
        resp = client.get(f"/api/storage/knowledge/browse?path={traversal_path}")
        assert resp.status_code in [400, 403, 404]
        if resp.status_code == 400:
            assert "traversal" in resp.json()["detail"].lower() or "invalid" in resp.json()["detail"].lower()
            
        # Try Read
        resp = client.get(f"/api/storage/knowledge/read?path={traversal_path}")
        assert resp.status_code in [400, 403, 404]
        
    def test_absolute_path_attack(self, client):
        """Attempt to pass an absolute path outside root."""
        abs_path = "/etc/passwd"
        resp = client.get(f"/api/storage/knowledge/read?path={abs_path}")
        assert resp.status_code in [400, 403, 404]
