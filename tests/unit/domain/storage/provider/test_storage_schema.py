import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from fastapi import FastAPI
from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider

@pytest.fixture
def mock_storage_manager():
    return MagicMock()

@pytest.fixture
def client(mock_storage_manager):
    provider = StorageAPIProvider(mock_storage_manager)
    app = FastAPI()
    app.include_router(provider.router)
    return TestClient(app)

def test_get_config_schema(client):
    response = client.get("/storage/schema/config")
    assert response.status_code == 200
    schema = response.json()
    
    assert "properties" in schema
    assert "output_path" in schema["properties"]
    assert "intermediate_path" in schema["properties"]
    assert "knowledge_path" in schema["properties"]
    assert schema["title"] == "StorageConfigRequest"

def test_get_storage_config(client, mock_storage_manager):
    mock_config = {
        "output": "/out",
        "intermediate": "/inter",
        "knowledge": "/know"
    }
    mock_storage_manager.get_config.return_value = mock_config

    response = client.get("/storage/config")
    assert response.status_code == 200
    data = response.json()
    assert data["output_path"] == "/out"
    assert data["intermediate_path"] == "/inter"
    assert data["knowledge_path"] == "/know"
