import pytest
import shutil
from pravaha.domain.workflow.infrastructure.json_workflow_repository import JsonWorkflowRepository
from pravaha.domain.workflow.infrastructure.json_run_repository import JsonRunRepository
from pravaha.domain.workflow.manager.local_workflow_manager import LocalWorkflowManager
from pravaha.domain.workflow.entity.workflow import Workflow
from pravaha.domain.workflow.entity.workflow_node import WorkflowNode, NodeType
from pravaha.domain.workflow.entity.workflow_run import WorkflowRun
from pravaha.domain.workflow.entity.run_state import RunState
from datetime import datetime

class TestJsonWorkflowRepository:
    
    @pytest.fixture
    def repo(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mgr = LocalWorkflowManager(defaults={"details": "workflows", "run": "runs"})
        return JsonWorkflowRepository(mgr)

    def test_save_and_get(self, repo):
        wf = Workflow(id="1", name="Test", nodes=[], edges=[])
        repo.save(wf)
        
        fetched = repo.get("1")
        assert fetched is not None
        assert fetched.id == "1"
        assert fetched.name == "Test"
        
    def test_get_not_found(self, repo):
        assert repo.get("missing") is None

    def test_list_all(self, repo):
        repo.save(Workflow(id="1", name="W1", nodes=[], edges=[]))
        repo.save(Workflow(id="2", name="W2", nodes=[], edges=[]))
        
        all_wfs = repo.list_all()
        assert len(all_wfs) == 2
        ids = {w.id for w in all_wfs}
        assert ids == {"1", "2"}

    def test_delete(self, repo):
        repo.save(Workflow(id="1", name="W1", nodes=[], edges=[]))
        repo.delete("1")
        assert repo.get("1") is None
        
    def test_rename(self, repo):
        repo.save(Workflow(id="1", name="Old", nodes=[], edges=[]))
        repo.rename("1", "New")
        fetched = repo.get("1")
        assert fetched.name == "New"
        
        with pytest.raises(ValueError):
            repo.rename("missing", "New")

class TestJsonRunRepository:

    @pytest.fixture
    def repo(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mgr = LocalWorkflowManager(defaults={"details": "workflows", "run": "runs"})
        return JsonRunRepository(mgr)
        
    def test_save_and_get(self, repo):
        run = WorkflowRun(
            id="r1", 
            workflow_id="w1", 
            status=RunState.PENDING,
            created_at=datetime.now()
        )
        repo.save(run)
        
        fetched = repo.get("r1")
        assert fetched.id == "r1"
        assert fetched.workflow_id == "w1"
        assert fetched.status == RunState.PENDING
        
    def test_list_by_workflow(self, repo):
        repo.save(WorkflowRun(id="r1", workflow_id="w1", status=RunState.PENDING, created_at=datetime.now()))
        repo.save(WorkflowRun(id="r2", workflow_id="w1", status=RunState.COMPLETED, created_at=datetime.now()))
        repo.save(WorkflowRun(id="r3", workflow_id="w2", status=RunState.PENDING, created_at=datetime.now()))
        
        runs_w1 = repo.list_by_workflow("w1")
        assert len(runs_w1) == 2
        
        runs_w2 = repo.list_by_workflow("w2")
        assert len(runs_w2) == 1
