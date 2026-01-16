
"""
E2E Scenario: Workflow Lifecycle
Verifies creating, running, and monitoring a workflow via the API.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.workflow.manager.local_workflow_manager import LocalWorkflowManager
from pravaha.domain.config.cache_config import CachePathConfig
from pravaha.domain.auth.config.auth_config import AuthConfig
from pravaha.domain.bot.protocol.bot_manager_protocol import BotManagerProtocol

# --- Mock Bot Manager ---
class MockBotManager(BotManagerProtocol):
    def __init__(self):
        self.call_log = []

    async def stream_run(self, task, inputs=None, llm_config=None, **kwargs):
        self.call_log.append(f"stream_run:{task}:{inputs}")
        yield "StreamResult"

    async def run(self, task, inputs=None, **kwargs):
        self.call_log.append(f"run:{task}:{inputs}")
        return "SyncResult"
    
    # Required protocol methods (stubs)
    def register_bot(self, *args, **kwargs): pass
    def get_bot(self, *args, **kwargs): pass
    def list_bots(self, *args, **kwargs): pass

# --- Mock Task Config ---
from enum import Enum
class MockTaskConfig:
    class UtilsType(str, Enum):
        TEST_UTIL = "test_util"
    class ApplicationType(str, Enum):
        TEST_APP = "test_app"
    class ExecutionTarget(str, Enum):
        LOCAL = "local"

class TestWorkflowLifecycle:
    
    @pytest.fixture
    def environment(self, tmp_path):
        """Setup API with Mock Bot Manager and Temp Storage."""
        root = tmp_path / "pravaha_root"
        root.mkdir()
        cache_config = CachePathConfig.from_custom_root(str(root))
        
        bot_mgr = MockBotManager()
        
        app = create_fastapi_app(
            bot_manager=bot_mgr,
            task_config=MockTaskConfig,
            storage_manager=None, # Not needed for this test
            auth_config=AuthConfig(enabled=False), 
            workflow_defaults={"details": "workflows", "run": "runs"},
            cache_config=cache_config,
            access_key_repository=None
        )
        
        return TestClient(app), bot_mgr

    def test_create_and_run_workflow(self, environment):
        client, bot_mgr = environment
        
        # 1. Create Workflow
        workflow_payload = {
            "name": "E2E Workflow",
            "nodes": [
                {
                    "id": "node-1",
                    "node_type": "UTIL", # Renamed from task_type
                    "task_name": "test_util", 
                    "inputs": {
                        "param": {
                            "key_name": "param", # Added required field
                            "source": "direct", 
                            "value": "123"
                        }
                    },
                    "position": {"x": 0, "y": 0}
                }
            ],
            "edges": []
        }
        
        resp = client.post("/api/workflow/create", json=workflow_payload)
        assert resp.status_code == 200
        wf_data = resp.json()
        wf_id = wf_data["id"]
        assert wf_data["name"] == "E2E Workflow"
        
        # 2. Trigger Run
        # Use new client-driven execution endpoint
        resp = client.post("/api/execution/run", json={"workflow_id": wf_id})
        assert resp.status_code == 200
        run_data = resp.json()
        run_id = run_data["workflow_run_id"]
        assert run_data["status"] == "RUNNING"
        
        # 3. Simulate Client Execution
        # 3.1 Get Status (Find Pending Node)
        resp = client.get(f"/api/execution/run/{run_id}/status")
        assert resp.status_code == 200
        status_data = resp.json()
        pending_node = status_data.get("current_node")
        assert pending_node is not None
        assert pending_node["node_id"] == "node-1"
        
        # 3.2 Mark Node IN_PROGRESS (Required)
        resp = client.post(
            f"/api/execution/run/{run_id}/node/node-1/status",
            json={"status": "IN_PROGRESS"}
        )
        assert resp.status_code == 200
        
        # 3.3 Complete Node
        # Simulate successful execution
        update_payload = {
            "status": "COMPLETED",
            "output_data": {"result": "success"}
        }
        resp = client.post(
            f"/api/execution/run/{run_id}/node/node-1/status",
            json=update_payload
        )
        assert resp.status_code == 200
        
        # 4. Verify Workflow Completion
        # Since it's a single node workflow, completing node-1 should complete the run.
        resp = client.get(f"/api/execution/run/{run_id}/status")
        assert resp.status_code == 200
        final_status = resp.json()
        assert final_status["status"] == "COMPLETED"
        assert final_status["current_node"] is None
