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
