import uuid
from typing import List, Optional
from datetime import datetime
from ..protocol.workflow_repository_protocol import WorkflowRepositoryProtocol
from ..protocol.run_repository_protocol import RunRepositoryProtocol
from ..protocol.workflow_engine_protocol import WorkflowEngineProtocol
from ..entity.workflow import Workflow
from ..entity.workflow_run import WorkflowRun
from ..entity.run_state import RunState

class WorkflowService:
    def __init__(
        self,
        workflow_repo: WorkflowRepositoryProtocol,
        run_repo: RunRepositoryProtocol,
        engine: WorkflowEngineProtocol
    ):
        self.workflow_repo = workflow_repo
        self.run_repo = run_repo
        self.engine = engine

    def create_workflow(self, workflow: Workflow) -> Workflow:
        # Auto-generate ID and timestamps
        if not workflow.id:
            workflow.id = str(uuid.uuid4())
        if not workflow.created_at:
            workflow.created_at = datetime.now().isoformat()
        if not workflow.updated_at:
            workflow.updated_at = workflow.created_at
        
        self.workflow_repo.save(workflow)
        return workflow

    def update_workflow(self, workflow: Workflow) -> Workflow:
        if not workflow.id:
            raise ValueError("Workflow ID is required for update")
        
        existing = self.workflow_repo.get(workflow.id)
        if not existing:
            raise ValueError(f"Workflow {workflow.id} not found")
        
        # Update timestamp
        workflow.updated_at = datetime.now().isoformat()
        
        self.workflow_repo.save(workflow)
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self.workflow_repo.get(workflow_id)

    def list_workflows(self) -> List[Workflow]:
        return self.workflow_repo.list_all()

    def delete_workflow(self, workflow_id: str) -> None:
        self.workflow_repo.delete(workflow_id)
    
    def rename_workflow(self, workflow_id: str, new_name: str) -> Workflow:
        """Rename a workflow and return the updated workflow."""
        if not workflow_id:
            raise ValueError("Workflow ID is required")
        if not new_name or not new_name.strip():
            raise ValueError("New name cannot be empty")
        
        # This will raise ValueError if workflow not found
        self.workflow_repo.rename(workflow_id, new_name.strip())
        
        # Return the updated workflow
        workflow = self.workflow_repo.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found after rename")
        
        return workflow

    async def trigger_run(self, workflow_id: str) -> WorkflowRun:
        workflow = self.workflow_repo.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Create new Run
        run = WorkflowRun(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            status=RunState.PENDING,
            created_at=datetime.now()
        )
        self.run_repo.save(run)
        
        # We start the engine execution here. 
        # Note: The caller (API) should likely schedule this as a background task
        # if they want to return immediately. However, since the Service method 
        # usually encapsulates usage, we will return the Run object immediately
        # and expect the Controller/Provider to handle the async scheduling of `engine.execute_run`.
        # But `engine.execute_run` requires the run object.
        
        # Actually, for clean separation, the Service could return the (run, coroutine) 
        # or just return run and have a specific method `execute_run_async` that does both.
        # Let's keep `trigger_run` as "Create and Return Run", and let API schedule execution.
        
        # OR better: The service method triggers it itself if we weren't in an async event loop web context restriction.
        # But we are. 
        
        return run

    async def execute_run(self, run_id: str):
        """
        Actual execution logic, to be called via BackgroundTasks
        """
        run = self.run_repo.get(run_id)
        if not run:
            return
        
        workflow = self.workflow_repo.get(run.workflow_id)
        if not workflow:
             # Fail run
             run.status = RunState.FAILED
             run.error_message = "Workflow deleted"
             self.run_repo.save(run)
             return

        await self.engine.execute_run(workflow, run)

    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        return self.run_repo.get(run_id)

    def list_runs(self, workflow_id: str) -> List[WorkflowRun]:
        return self.run_repo.list_by_workflow(workflow_id)

    def list_all_runs(self) -> List[WorkflowRun]:
        """Return all runs across all workflows"""
        return self.run_repo.list_all()
