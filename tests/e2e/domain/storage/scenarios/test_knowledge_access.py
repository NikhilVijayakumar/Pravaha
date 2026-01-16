"""
E2E Scenario: Knowledge Access
Verifies browsing and reading documentation and schemas.
"""

import pytest
import json
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

class TestKnowledgeAccessScenario:
    
    @pytest.fixture
    def setup_knowledge(self, tmp_path):
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
        
        # Create Content
        docs_dir = root / "knowledge" / "docs"
        docs_dir.mkdir(parents=True)
        (docs_dir / "guide.md").write_text("# Guide\nHello World")
        
        schemas_dir = root / "knowledge" / "schemas"
        schemas_dir.mkdir(parents=True)
        (schemas_dir / "data.json").write_text('{"schema": "v1"}')
        
        return TestClient(app)

    def test_browse_and_read(self, setup_knowledge):
        client = setup_knowledge
        
        # 1. Browse Root
        resp = client.get("/api/storage/knowledge/browse")
        assert resp.status_code == 200
        children = resp.json()["items"]
        names = [c["name"] for c in children]
        assert "docs" in names
        assert "schemas" in names
        
        # 2. Browse Subfolder
        resp = client.get("/api/storage/knowledge/browse?path=docs")
        assert resp.status_code == 200
        docs_children = resp.json()["items"]
        assert docs_children[0]["name"] == "guide.md"
        assert docs_children[0]["type"] == "file"
        
        # 3. Read Markdown
        resp = client.get("/api/storage/knowledge/read?path=docs/guide.md")
        assert resp.status_code == 200
        # Should return plain string (auto-detected usually, or generic response)
        # The API usually returns JSON for .json and String for others?
        # Let's check implementation. If response is JSON, content is inside?
        # Or raw string body?
        # Usually file endpoints might return FileResponse or raw text.
        # Our docs say: "Text files: Plain text string"
        assert "# Guide" in resp.text
        
        # 4. Read JSON
        resp = client.get("/api/storage/knowledge/read?path=schemas/data.json")
        assert resp.status_code == 200
        assert resp.json()["content"]["schema"] == "v1"
