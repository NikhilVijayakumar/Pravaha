import pytest
import os
import json
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from pravaha.domain.workflow.entity.workflow import Workflow
from pravaha.domain.workflow.entity.workflow_node import WorkflowNode
from pravaha.domain.workflow.entity.workflow_edge import WorkflowEdge
from pravaha.domain.workflow.entity.workflow_run import WorkflowRun
from pravaha.domain.workflow.entity.run_state import RunState
from pravaha.domain.workflow.infrastructure.json_workflow_repository import JsonWorkflowRepository
from pravaha.domain.workflow.infrastructure.json_run_repository import JsonRunRepository
from pravaha.domain.workflow.service.simple_workflow_engine import SimpleWorkflowEngine
from pravaha.domain.workflow.service.workflow_service import WorkflowService
from pravaha.domain.workflow.protocol.task_executor_protocol import TaskExecutorProtocol

# --- Mocks ---

class MockTaskExecutor(TaskExecutorProtocol):
    def __init__(self):
        self.executed_tasks = []

    async def execute(self, task_type, task_name, inputs=None, stream=False):
        self.executed_tasks.append(task_name)
        if task_name == "FAIL_TASK":
            raise Exception("Task Failed by Design")
        return f"Result of {task_name}"

# --- Tests ---

@pytest.fixture
def temp_dirs(tmp_path):
    wf_file = tmp_path / "workflows.json"
    run_file = tmp_path / "runs.json"
    return str(wf_file), str(run_file)

@pytest.fixture
def services(temp_dirs):
    wf_path, run_path = temp_dirs
    wf_repo = JsonWorkflowRepository(wf_path)
    run_repo = JsonRunRepository(run_path)
    executor = MockTaskExecutor()
    engine = SimpleWorkflowEngine(executor, run_repo)
    service = WorkflowService(wf_repo, run_repo, engine)
    return service, wf_repo, run_repo, executor

def test_workflow_crud(services):
    service, _, _, _ = services
    
    wf = Workflow(
        id="wf-1",
        name="Test Workflow",
        nodes=[WorkflowNode(id="node-1", task_type="APP", task_name="Task1")],
        edges=[]
    )
    
    saved = service.create_workflow(wf)
    assert saved.id == "wf-1"
    
    fetched = service.get_workflow("wf-1")
    assert fetched.name == "Test Workflow"
    assert len(fetched.nodes) == 1

@pytest.mark.asyncio
async def test_workflow_execution_success(services):
    service, _, run_repo, executor = services
    
    # Create Workflow: A -> B
    wf = Workflow(
        id="wf-seq",
        name="Sequential",
        nodes=[
            WorkflowNode(id="A", task_type="APP", task_name="TaskA"),
            WorkflowNode(id="B", task_type="APP", task_name="TaskB")
        ],
        edges=[WorkflowEdge(id="e1", source="A", target="B")]
    )
    service.create_workflow(wf)
    
    # Trigger Run
    run = await service.trigger_run("wf-seq")
    assert run.status == RunState.PENDING
    
    # Execute
    await service.execute_run(run.id)
    
    # Verify execution
    updated_run = service.get_run(run.id)
    assert updated_run.status == RunState.COMPLETED
    assert executor.executed_tasks == ["TaskA", "TaskB"]
    assert updated_run.node_states["A"] == RunState.COMPLETED
    assert updated_run.node_states["B"] == RunState.COMPLETED

@pytest.mark.asyncio
async def test_workflow_execution_failure_and_resume(services):
    service, _, run_repo, executor = services
    
    # Create Workflow: A -> FAIL -> B
    wf = Workflow(
        id="wf-fail",
        name="Fail Resume",
        nodes=[
            WorkflowNode(id="A", task_type="APP", task_name="TaskA"),
            WorkflowNode(id="FAIL", task_type="APP", task_name="FAIL_TASK"),
            WorkflowNode(id="B", task_type="APP", task_name="TaskB")
        ],
        edges=[
            WorkflowEdge(id="e1", source="A", target="FAIL"),
            WorkflowEdge(id="e2", source="FAIL", target="B")
        ]
    )
    service.create_workflow(wf)
    
    # 1. Run -> Should Fail
    run_1 = await service.trigger_run("wf-fail")
    await service.execute_run(run_1.id)
    
    run_1_state = service.get_run(run_1.id)
    assert run_1_state.status == RunState.FAILED
    assert executor.executed_tasks == ["TaskA", "FAIL_TASK"]
    assert run_1_state.node_states["A"] == RunState.COMPLETED
    assert run_1_state.node_states["FAIL"] == RunState.FAILED
    assert "B" not in run_1_state.node_states # Should not reach B
    
    # 2. Fix Metadata (Simulate changing task definition or just retrying externally)
    # Ideally, user updates workflow definition to fix bug.
    # Here, we will PATCH the MockExecutor to succeed next time for "FAIL_TASK" (simulating a transient error or fix)
    
    # Reset executor log for clarity but keep state
    executor.executed_tasks = []
    
    # Modify mock logic dynamically (hack for test)
    original_execute = executor.execute
    async def success_execute(self, task_type, task_name, inputs=None, stream=False):
        self.executed_tasks.append(task_name)
        return "Success"
    # Bind new method
    MockTaskExecutor.execute = success_execute
    
    # 3. Resume (Call execute_run again on SAME run_id)
    # The spec says "Stop on Failure..., allowing future resumption". 
    # Simply calling execute_run again should trigger the loop.
    await service.execute_run(run_1.id)
    
    run_1_resumed = service.get_run(run_1.id)
    assert run_1_resumed.status == RunState.COMPLETED
    
    # Verify "TaskA" was SKIPPED (not re-executed)
    assert "TaskA" not in executor.executed_tasks
    # "FAIL_TASK" (now succeeding) and "TaskB" should run
    assert "FAIL_TASK" in executor.executed_tasks
    assert "TaskB" in executor.executed_tasks
