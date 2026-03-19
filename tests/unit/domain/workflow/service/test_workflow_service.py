import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock

from pravaha.domain.workflow.entity.workflow import Workflow
from pravaha.domain.workflow.entity.workflow_node import WorkflowNode, NodeType
from pravaha.domain.workflow.entity.workflow_edge import WorkflowEdge
from pravaha.domain.workflow.entity.run_state import RunState
from pravaha.domain.workflow.manager.local_workflow_manager import LocalWorkflowManager
from pravaha.domain.workflow.infrastructure.json_workflow_repository import JsonWorkflowRepository
from pravaha.domain.workflow.infrastructure.json_run_repository import JsonRunRepository
from pravaha.domain.workflow.service.simple_orchestration_engine import SimpleOrchestrationEngine
from pravaha.domain.workflow.service.workflow_service import WorkflowService

@pytest.fixture
def services(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Setup Manager with temp paths
    workflow_manager = LocalWorkflowManager(
        defaults={"details": "workflows", "run": "runs"}
    )
    
    # Setup Real Repositories (fast enough for unit/integration)
    wf_repo = JsonWorkflowRepository(workflow_manager)
    run_repo = JsonRunRepository(workflow_manager)
    
    # Setup Real Engine
    engine = SimpleOrchestrationEngine(run_repo)
    
    # Setup Service
    service = WorkflowService(wf_repo, run_repo, engine)
    
    return service, wf_repo, run_repo

def test_workflow_crud(services):
    service, _, _ = services
    
    wf = Workflow(
        id="wf-1",
        name="Test Workflow",
        nodes=[WorkflowNode(id="node-1", node_type=NodeType.APPLICATION, task_name="Task1")],
        edges=[]
    )
    
    saved = service.create_workflow(wf)
    assert saved.id == "wf-1"
    
    fetched = service.get_workflow("wf-1")
    assert fetched.name == "Test Workflow"
    assert len(fetched.nodes) == 1

def test_trigger_run_initialization(services):
    service, _, run_repo = services
    
    # Create Workflow: A -> B
    wf = Workflow(
        id="wf-seq",
        name="Sequential",
        nodes=[
            WorkflowNode(id="A", node_type=NodeType.APPLICATION, task_name="TaskA"),
            WorkflowNode(id="B", node_type=NodeType.APPLICATION, task_name="TaskB")
        ],
        edges=[WorkflowEdge(id="e1", source="A", target="B")]
    )
    service.create_workflow(wf)
    
    # Trigger Run
    run = service.trigger_run("wf-seq")
    
    assert run.status == RunState.RUNNING
    assert run.node_states["A"] == RunState.PENDING # First node
    assert run.node_states["B"] == RunState.NEW # Dependent node
    
    # Verify Persistence
    persisted = run_repo.get(run.id)
    assert persisted.status == RunState.RUNNING

def test_client_driven_execution_flow(services):
    service, _, _ = services
    
    # Create Workflow: A -> B
    wf = Workflow(
        id="wf-flow",
        name="Flow Test",
        nodes=[
            WorkflowNode(id="A", node_type=NodeType.APPLICATION, task_name="TaskA"),
            WorkflowNode(id="B", node_type=NodeType.APPLICATION, task_name="TaskB")
        ],
        edges=[WorkflowEdge(id="e1", source="A", target="B")]
    )
    service.create_workflow(wf)
    run = service.trigger_run("wf-flow")
    run_id = run.id
    
    # 1. Get Status (Check node A is pending)
    status_resp = service.get_run_status(run_id)
    assert status_resp["current_node"]["node_id"] == "A"
    assert status_resp["current_node"]["status"] == RunState.PENDING.value

    # 2. Mark A IN_PROGRESS
    service.update_node_status(run_id, "A", "IN_PROGRESS")
    status_resp = service.get_run_status(run_id)
    # When IN_PROGRESS, get_next_pending_node returns None (since no node is PENDING)
    # Client relies on nodes_status to see what's running
    assert status_resp["current_node"] is None 
    assert status_resp["nodes_status"]["A"] == RunState.IN_PROGRESS.value

    # 3. Complete A
    service.update_node_status(run_id, "A", "COMPLETED", output_data={"res": "A done"})
    
    # 4. Check Status (Next node B should be pending)
    status_resp = service.get_run_status(run_id)
    assert status_resp["current_node"]["node_id"] == "B"
    assert status_resp["current_node"]["status"] == RunState.PENDING.value
    
    # 5. Complete B
    service.update_node_status(run_id, "B", "IN_PROGRESS")
    service.update_node_status(run_id, "B", "COMPLETED")
    
    # 6. Verify Workflow Completion
    status_resp = service.get_run_status(run_id)
    assert status_resp["status"] == RunState.COMPLETED.value
    assert status_resp["current_node"] is None

def test_workflow_rename(services):
    service, _, _ = services
    wf = Workflow(
        id="wf-1",
        name="Original Name",
        nodes=[WorkflowNode(id="node-1", node_type=NodeType.APPLICATION, task_name="Task1")],
        edges=[]
    )
    service.create_workflow(wf)
    
    renamed = service.rename_workflow("wf-1", "New Name")
    assert renamed.name == "New Name"
    fetched = service.get_workflow("wf-1")
    assert fetched.name == "New Name"

def test_workflow_rename_errors(services):
    service, _, _ = services
    with pytest.raises(ValueError, match="not found"):
        service.rename_workflow("non-exist", "New")
    
    wf = Workflow(id="valid", name="Valid", nodes=[], edges=[])
    service.create_workflow(wf)
    
    with pytest.raises(ValueError, match="cannot be empty"):
        service.rename_workflow("valid", "")
