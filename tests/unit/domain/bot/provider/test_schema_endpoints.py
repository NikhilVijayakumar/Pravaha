import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from enum import Enum
from pydantic import BaseModel
from pravaha.domain.bot.provider.bot_api_provider import BotAPIProvider

# Mocks
class MockUtilsType(Enum):
    TEST_UTIL = "test_util"

class MockAppType(Enum):
    TEST_APP = "test_app"

class MockExecTarget(Enum):
    LOCAL = "local"

class MockInputModel(BaseModel):
    field1: str
    field2: int

class MockOutputModel(BaseModel):
    result: str

@pytest.fixture
def mock_task_config():
    config = MagicMock()
    config.UtilsType = MockUtilsType
    config.ApplicationType = MockAppType
    config.ExecutionTarget = MockExecTarget
    return config

@pytest.fixture
def mock_bot_manager():
    manager = MagicMock()
    # Setup default return values
    manager.get_input_model.return_value = None
    manager.get_output_model.return_value = None
    return manager

@pytest.fixture
def client(mock_bot_manager, mock_task_config):
    from fastapi import FastAPI
    provider = BotAPIProvider(mock_bot_manager, mock_task_config)
    app = FastAPI()
    app.include_router(provider.router)
    return TestClient(app)

def test_get_input_schema_found(client, mock_bot_manager):
    mock_bot_manager.get_input_model.return_value = MockInputModel
    
    response = client.get("/protocol/schema/input/test_util")
    assert response.status_code == 200
    schema = response.json()
    assert "properties" in schema
    assert "field1" in schema["properties"]
    assert schema["title"] == "MockInputModel"

def test_get_input_schema_not_found_task(client):
    response = client.get("/protocol/schema/input/non_existent")
    assert response.status_code == 404

def test_get_input_schema_no_model(client, mock_bot_manager):
    # manager returns None for model (e.g. no input needed)
    mock_bot_manager.get_input_model.return_value = None
    
    response = client.get("/protocol/schema/input/test_util")
    assert response.status_code == 200
    assert response.json() == {}

def test_get_output_schema_found(client, mock_bot_manager):
    mock_bot_manager.get_output_model.return_value = MockOutputModel
    
    response = client.get("/protocol/schema/output/test_app")
    assert response.status_code == 200
    schema = response.json()
    assert "properties" in schema
    assert "result" in schema["properties"]

def test_get_output_schema_not_found_task(client):
    response = client.get("/protocol/schema/output/non_existent")
    assert response.status_code == 404
