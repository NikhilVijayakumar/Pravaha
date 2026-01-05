import pytest
import json
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from pathlib import Path

from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider
from pravaha.domain.storage.protocol.artifact_resolver_protocol import StorageStage

@pytest.fixture
def mock_storage_manager(tmp_path):
    manager = MagicMock()
    # Mock get_path to return temp dirs
    def get_path_side_effect(category):
        p = tmp_path / category
        p.mkdir(exist_ok=True)
        return p
    manager.get_path.side_effect = get_path_side_effect
    return manager

@pytest.fixture
def mock_llm_config():
    config = MagicMock()
    # Mock resolve to return simple dict
    def resolve_side_effect(model_key):
        return {"display_name": model_key.title(), "alias": model_key}
    config.resolve_output_config.side_effect = resolve_side_effect
    return config

@pytest.fixture
def client(mock_storage_manager, mock_llm_config):
    provider = StorageAPIProvider(
        storage_manager=mock_storage_manager,
        llm_config_manager=mock_llm_config,
        path_resolver=MagicMock(),
        version_resolver=MagicMock()
    )
    return TestClient(provider.router)

def test_browse_intermediate_structure(client, mock_storage_manager, tmp_path):
    # Data Setup
    inter_root = tmp_path / "intermediate"
    inter_root.mkdir(exist_ok=True)
    
    # Feature folder
    feature = inter_root / "MyFeature"
    feature.mkdir()
    
    # Output timestamp dir
    ts_dir = feature / "output_20250101000000"
    ts_dir.mkdir()
    
    # File
    (ts_dir / "model.json").touch()
    
    response = client.get("/storage/intermediate/browse")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    item = data[0]
    assert item["feature"] == "MyFeature"
    assert item["model"] == "model"
    assert item["display_name"] == "Model.json"

def test_browse_final_structure(client, mock_storage_manager, tmp_path):
    # Data Setup
    out_root = tmp_path / "output"
    out_root.mkdir(exist_ok=True)
    
    # Product -> Feature
    prod = out_root / "MyProduct"
    prod.mkdir()
    feat = prod / "MyFeature"
    feat.mkdir()
    
    # File
    (feat / "model.json").touch()
    
    response = client.get("/storage/output/browse")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    item = data[0]
    assert item["product"] == "MyProduct"
    assert item["feature"] == "MyFeature"
    assert item["display_name"] == "Model.json"

def test_read_file_content(client, mock_storage_manager, tmp_path):
    # Data Setup for Read
    out_root = tmp_path / "output"
    out_root.mkdir(exist_ok=True)
    prod = out_root / "MyProduct"
    prod.mkdir()
    feat = prod / "MyFeature"
    feat.mkdir()
    
    file_path = feat / "data.json"
    file_path.write_text('{"foo": "bar"}', encoding="utf-8")
    
    # We need the absolute path for read? 
    # API expects 'path' query param. 
    # The new code resolves path from root: (root / path).resolve() NO WAIT
    # The new code: file_path = Path(path).resolve()
    # It takes absolute path directly?
    # Yes: async def handler(path: str): file_path = Path(path).resolve()
    
    response = client.get("/storage/output/read", params={"path": str(file_path)})
    assert response.status_code == 200
    assert response.json() == {"content": {"foo": "bar"}}

def test_read_security_check(client, mock_storage_manager, tmp_path):
    # Try reading file outside root
    outside = tmp_path / "outside.txt"
    outside.touch()
    
    response = client.get("/storage/output/read", params={"path": str(outside)})
    assert response.status_code == 403
