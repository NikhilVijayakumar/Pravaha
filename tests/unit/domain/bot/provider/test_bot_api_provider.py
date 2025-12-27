from enum import Enum
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Must import the provider which imports the models
from pravaha.domain.bot.provider.bot_api_provider import BotAPIProvider

# Define mock Enums
class MockUtilsType(str, Enum):
    UTIL_A = "util_a"
    UTIL_B = "util_b"

class MockApplicationType(str, Enum):
    APP_X = "app_x"
    APP_Y = "app_y"

class MockExecutionTarget(str, Enum):
    TARGET_1 = "target_1"

@pytest.fixture
def mock_task_config():
    config = MagicMock()
    config.UtilsType = MockUtilsType
    config.ApplicationType = MockApplicationType
    config.ExecutionTarget = MockExecutionTarget
    return config

@pytest.fixture
def mock_bot_manager():
    manager = MagicMock()
    return manager

@pytest.fixture
def client(mock_bot_manager, mock_task_config):
    # This init will patch UtilityRequest/ApplicationRequest annotations
    provider = BotAPIProvider(mock_bot_manager, mock_task_config)
    return TestClient(provider.router)

def test_run_utility_success(client, mock_bot_manager):
    mock_bot_manager.run.return_value = "success_result"
    
    payload = {"task_name": "util_a", "inputs": [{"k": "v"}]}
    response = client.post("/run/utility", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"status": "success", "result": "success_result"}
    # Verify it was called with the Enum member, not just string, if pydantic converts it?
    # fastAPI/pydantic usually converts input string to Enum member if type is Enum.
    mock_bot_manager.run.assert_called()
    call_args = mock_bot_manager.run.call_args
    # call_args[0][0] should be MockUtilsType.UTIL_A
    assert call_args[0][0] == MockUtilsType.UTIL_A

def test_run_application_stream_sync_iter(client, mock_bot_manager):
    # Mock stream_run returning a list (iterable)
    mock_bot_manager.stream_run.return_value = ["chunk1", "chunk2"]
    
    payload = {"task_name": "app_x", "inputs": []}
    response = client.post("/run/application/stream", json=payload)
    
    assert response.status_code == 200
    # verify content contains chunks. SSE format usually has "data: ..."
    # But checking substring is enough for unit test of flow.
    assert "chunk1" in response.text
    assert "chunk2" in response.text

def test_get_util_types(client):
    response = client.get("/enums/util-types")
    assert response.status_code == 200
    assert "util_a" in response.json()
    assert "util_b" in response.json()

def test_run_utility_invalid_enum(client):
    payload = {"task_name": "invalid_util", "inputs": []}
    response = client.post("/run/utility", json=payload)
    assert response.status_code == 422
