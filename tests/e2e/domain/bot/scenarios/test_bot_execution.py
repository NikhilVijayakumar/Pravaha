import pytest
from starlette.testclient import TestClient
from fastapi import FastAPI
from enum import Enum
from unittest.mock import MagicMock, AsyncMock
from typing import List, Dict, Any, Optional

from pravaha.domain.bot.provider.bot_api_provider import BotAPIProvider
from pravaha.domain.bot.protocol.bot_manager_protocol import BotManagerProtocol

# Define Mock Enums
class UtilsType(str, Enum):
    TEST_UTIL = "test_util"

class ApplicationType(str, Enum):
    TEST_APP = "test_app"

class MockTaskConfig:
    UtilsType = UtilsType
    ApplicationType = ApplicationType
    ExecutionTarget = UtilsType

class MockBotManager:
    """Mock Manager implementing Protocol."""
    def run(self, utility_task: UtilsType, inputs: Optional[List[Dict[str, Any]]] = None) -> Any:
        if utility_task == UtilsType.TEST_UTIL:
            return {"status": "ok", "input_received": inputs}
        raise ValueError("Unknown task")

    async def stream_run(
        self, 
        application_task: ApplicationType, 
        inputs: Optional[List[Dict[str, Any]]] = None,
        llm_config: Optional[Any] = None
    ):
        if application_task == ApplicationType.TEST_APP:
            yield "chunk1"
            yield "chunk2"
            if llm_config:
                # Handle dict since ApplicationRequest types it as Any
                model = llm_config["model_config"]["model"] if isinstance(llm_config, dict) else llm_config.model_config.model
                yield f"config:{model}"

    def get_input_model(self, task):
        return None
    def get_output_model(self, task):
        return None
    def get_config(self, task):
        return {"mock": "config"}

class TestBotExecutionE2E:
    """
    E2E Tests for Bot Module.
    Target: tests/e2e/domain/bot/scenarios/test_bot_execution.py
    """

    @pytest.fixture
    def client(self):
        manager = MockBotManager()
        provider = BotAPIProvider(
            bot_manager=manager,
            task_config=MockTaskConfig()
        )
        app = FastAPI()
        app.include_router(provider.router)
        return TestClient(app)

    def test_sync_utility_flow(self, client):
        """[E2E-BOT-001] Verify sync task execution flow."""
        response = client.post("/run/utility", json={
            "task_name": "test_util",
            "inputs": [{"val": 1}]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["result"]["input_received"] == [{"val": 1}]

    def test_async_stream_flow(self, client):
        """[E2E-BOT-002] Verify async streaming flow."""
        response = client.post("/run/application/stream", json={
            "task_name": "test_app",
            "inputs": []
        })
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        # Verify chunks
        content = response.text
        assert "data: chunk1" in content
        assert "data: chunk2" in content
        assert "data: [DONE]" in content

    def test_llm_config_override_flow(self, client):
        """[E2E-BOT-003] Verify LLM config override is passed to manager."""
        override = {
            "model_config": {"model": "gpt-4-test"},
            "llm_parameters": {}
        }
        response = client.post("/run/application/stream", json={
            "task_name": "test_app",
            "llm_config_override": override
        })
        assert response.status_code == 200
        content = response.text
        # our mock manager yields the model name if config is present
        assert "data: config:gpt-4-test" in content

    def test_introspection_flow(self, client):
        """[E2E-BOT-004] Verify introspection schemas."""
        # Enums
        res = client.get("/enums/util-types")
        assert "test_util" in res.json()
        
        # Config
        res = client.get("/protocol/config/test_util")
        assert res.json() == {"mock": "config"}
