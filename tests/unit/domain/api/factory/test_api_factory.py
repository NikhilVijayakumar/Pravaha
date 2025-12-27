import pytest
from enum import Enum
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from pravaha.domain.api.factory.api_factory import create_bot_api, create_fastapi_app
from pravaha.domain.api.protocol.bot_manager_protocol import BotManagerProtocol
from pravaha.domain.api.protocol.task_config_protocol import TaskConfigProtocol

class MockUtils(Enum):
    UTIL_1 = "util_1"

class MockApp(Enum):
    APP_1 = "app_1"

class MockTarget(Enum):
    TARGET_1 = "target_1"

@pytest.fixture
def mock_task_config():
    config = Mock(spec=TaskConfigProtocol)
    config.UtilsType = MockUtils
    config.ApplicationType = MockApp
    config.ExecutionTarget = MockTarget
    return config

@pytest.fixture
def mock_bot_manager():
    manager = Mock(spec=BotManagerProtocol)
    return manager

def test_create_bot_api_utility(mock_bot_manager, mock_task_config):
    mock_bot_manager.run.return_value = "success_result"
    
    router = create_bot_api(mock_bot_manager, mock_task_config)
    # We need a FastAPI app to test the router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    
    response = client.post("/run/utility", json={"task_name": "util_1"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "result": "success_result"}
    mock_bot_manager.run.assert_called_with(MockUtils.UTIL_1)

def test_create_bot_api_utility_error(mock_bot_manager, mock_task_config):
    mock_bot_manager.run.side_effect = ValueError("Test Error")
    
    router = create_bot_api(mock_bot_manager, mock_task_config)
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    
    response = client.post("/run/utility", json={"task_name": "util_1"})
    assert response.status_code == 500
    assert "ValueError: Test Error" in response.json()["detail"]

def test_create_bot_api_enums(mock_bot_manager, mock_task_config):
    router = create_bot_api(mock_bot_manager, mock_task_config)
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    
    assert client.get("/enums/util-types").json() == ["util_1"]
    assert client.get("/enums/application-types").json() == ["app_1"]
    assert client.get("/enums/execution-targets").json() == ["target_1"]

def test_create_bot_api_stream(mock_bot_manager, mock_task_config):
    # Mock stream_run to return an async iterator
    async def async_gen():
        yield "chunk1"
        yield "chunk2"
    
    mock_bot_manager.stream_run.return_value = async_gen()
    
    router = create_bot_api(mock_bot_manager, mock_task_config)
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    
    response = client.post("/run/application/stream", json={"task_name": "app_1"})
    assert response.status_code == 200
    # Verify SSE format
    assert "data: chunk1.n.n" in response.text
    assert "data: chunk2.n.n" in response.text
    assert "data: chunk2.n.n" in response.text
    assert "data: [DONE].n.n" in response.text

def test_create_bot_api_stream_sync(mock_bot_manager, mock_task_config):
    # Mock stream_run to return a sync iterator
    def sync_gen():
        yield "sync_chunk1"
        yield "sync_chunk2"
    
    mock_bot_manager.stream_run.return_value = sync_gen()
    
    router = create_bot_api(mock_bot_manager, mock_task_config)
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    
    response = client.post("/run/application/stream", json={"task_name": "app_1"})
    assert response.status_code == 200
    assert "data: sync_chunk1.n.n" in response.text
    assert "data: sync_chunk2.n.n" in response.text
    assert "data: [DONE].n.n" in response.text

def test_create_bot_api_stream_single(mock_bot_manager, mock_task_config):
    # Mock stream_run to return a single value
    mock_bot_manager.stream_run.return_value = "single_value"
    
    router = create_bot_api(mock_bot_manager, mock_task_config)
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    
    response = client.post("/run/application/stream", json={"task_name": "app_1"})
    assert response.status_code == 200
    assert "data: single_value.n.n" in response.text
    assert "data: [DONE].n.n" in response.text

def test_create_fastapi_app(mock_bot_manager, mock_task_config):
    app = create_fastapi_app(mock_bot_manager, mock_task_config)
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
    # Check if router is included (e.g. check enums)
    # Note: create_fastapi_app adds prefix="/api" by default
    response = client.get("/api/enums/util-types")
    assert response.status_code == 200
    assert response.json() == ["util_1"]
