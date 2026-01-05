import pytest
from unittest.mock import MagicMock
from pathlib import Path
from fastapi.testclient import TestClient
from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider
from pravaha.domain.storage.protocol.artifact_resolver_protocol import StorageStage

# Mock classes
class MockLLMConfigManager:
    def resolve_output_config(self, model_key):
        if model_key == "gemma-3-12b-it":
            return {"display_name": "Gemma 3 12B", "alias": "gemma-3-12b"}
        if model_key == "gemini_flash":
            return {"display_name": "Gemini Flash", "alias": "gemini_flash"}
        return {"display_name": model_key, "alias": model_key}

class MockStorageManager:
    def __init__(self, root: Path):
        self.root = root
        self.project_root = root # Simplify
    
    def get_path(self, category):
        return self.root / category
    
    @property
    def project_root(self):
        return self.root

class MockResolver:
    pass

@pytest.fixture
def api_client(tmp_path):
    storage_root = tmp_path / "storage"
    storage_root.mkdir()
    (storage_root / "output").mkdir()
    (storage_root / "intermediate").mkdir()
    
    storage_manager = MockStorageManager(storage_root)
    config_manager = MockLLMConfigManager()
    
    provider = StorageAPIProvider(
        storage_manager, 
        config_manager, 
        MockResolver(), 
        MockResolver()
    )
    return TestClient(provider.router), storage_root

def test_display_name_with_extension_output(api_client):
    client, root = api_client
    
    # Setup: Create a file in output
    # Structure: output/Feature/gemma-3-12b-it_1.json
    feature_dir = root / "output" / "StoryGen"
    feature_dir.mkdir(parents=True)
    
    # mocked logic in provider expects:
    # Stem: gemma-3-12b-it_1 -> alias=gemma-3-12b-it, version=2
    (feature_dir / "gemma-3-12b-it_1.json").touch()
    
    response = client.get("/storage/output/browse")
    assert response.status_code == 200
    data = response.json()
    
    # Check assertions
    # Response is a list of groups
    assert isinstance(data, list)
    assert len(data) > 0
    group = data[0]
    
    assert group["model"] == "gemma-3-12b-it"
    # User requirement: "Gemma 3 12B.json"
    assert group["display_name"] == "Gemma 3 12B.json"

def test_display_name_with_extension_intermediate(api_client):
    client, root = api_client
    
    # Setup: Create a file in intermediate
    # Structure: intermediate/Feature/output_TIMESTAMP/gemma-3-12b-it.json
    # Timestamp format needs to match regex: output_(\d{14})
    ts_dir = root / "intermediate" / "StoryGen" / "output_20250101000000"
    ts_dir.mkdir(parents=True)
    
    (ts_dir / "gemma-3-12b-it.json").touch()
    
    response = client.get("/storage/intermediate/browse")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) > 0
    group = data[0]
    
    assert group["display_name"] == "Gemma 3 12B.json"
