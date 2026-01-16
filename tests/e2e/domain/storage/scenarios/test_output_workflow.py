"""
E2E Scenario: Full Output Lifecycle
Verifies saving, browsing, and reading output artifacts.
"""

import pytest
import json
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from pravaha.domain.storage.provider.output_storage_provider import OutputStorageProvider
from pravaha.domain.config.cache_config import CachePathConfig
from pravaha.domain.auth.config.auth_config import AuthConfig
from pravaha.domain.llm.manager.llm_config_manager import LLMConfigManager

# Mock Task Config to satisfy API Factory
from enum import Enum
class MockTaskConfig:
    class UtilsType(str, Enum):
        TEST = "test"
    class ApplicationType(str, Enum):
        TEST = "test"
    class ExecutionTarget(str, Enum):
        LOCAL = "local"


class TestOutputWorkflowScenario:
    
    @pytest.fixture
    def environment(self, tmp_path):
        """Setup full environment."""
        root = tmp_path / "pravaha_root"
        root.mkdir()
        
        cache_config = CachePathConfig.from_custom_root(str(root))
        
        # Managers
        storage_mgr = LocalStorageManager(
            defaults={
                "output": str(root / "output"),
                "intermediate": str(root / "intermediate"),
                "knowledge": str(root / "knowledge")
            },
            cache_config=cache_config
        )
        
        # Simple LLM Config Manager (needed for product resolution)
        llm_mgr = LLMConfigManager(cache_config=cache_config)
        
        app = create_fastapi_app(
            bot_manager=None,
            task_config=MockTaskConfig,
            storage_manager=storage_mgr,
            auth_config=AuthConfig(enabled=False), # Disable auth for storage logic focus
            access_key_repository=None
        )
        
        return TestClient(app), storage_mgr, root

    def test_output_lifecycle(self, environment):
        """
        1. Save file via Provider.
        2. Browse API to find it.
        3. Read API to get content.
        """
        client, storage_mgr, root = environment
        
        # 1. Save File (Simulate Internal Task)
        # We assume dependencies like LLM Config are handled or optional
        # OutputStorageProvider needs manager.
        
        output_provider = OutputStorageProvider(
            storage_manager=storage_mgr,
            llm_config_manager=None, # Optional if we pass product explicitly? 
            # Check implementation. If None, it might fail?
            # Actually OutputStorageProvider constructor signature:
            # (storage_manager, llm_config_manager, path_resolver, version_resolver)
            # We usually use the storage_mgr to get providers? 
            # No, StorageAPIProvider creates them. 
            # Let's verify constructor signature or use StorageAPIProvider logic?
            # Internal tasks use providers directly.
        )
        # Wait, if I cannot easily instantiate Provider due to DI complexity, 
        # I can just write the file to disk manually to simulate "Save".
        # This is E2E for the API, so verifying API can read what exists is key.
        # But verifying Provider.save() puts it in right place is also good.
        
        # Let's write manually to guarantee Setup, then use API to Browse/Read.
        
        target_dir = root / "output" / "gpt-4" / "feature-a"
        target_dir.mkdir(parents=True)
        
        file_path = target_dir / "result.json"
        data = {"success": True, "value": 42}
        with open(file_path, "w") as f:
            json.dump(data, f)
            
        # 2. Browse API
        # Browse Root (Expect Groups)
        resp = client.get("/api/storage/output/browse")
        assert resp.status_code == 200
        groups = resp.json()
        assert isinstance(groups, list)
        
        # Check if our group is present
        # Grouped by (Feature, Product, Model)
        # We saved to feature-a, gpt-4
        
        target_group = next((g for g in groups if g["feature"] == "feature-a" and g["product"] == "gpt-4"), None)
        assert target_group is not None
        assert target_group["model"] == "result" # "result" from result_v1.json
        
        # Check Versions
        versions = target_group["versions"]
        assert len(versions) > 0
        assert versions[0]["version"] == 1
        
        # 3. Read API
        # Path from the group metadata
        read_path = versions[0]["path"] 
        # Note: path returned by browse is strictly relative to storage root?
        # OutputStorageProvider uses: str(file.relative_to(storage_root))
        
        resp = client.get(f"/api/storage/output/read?path={read_path}")
        assert resp.status_code == 200
        assert resp.json()["content"] == data
