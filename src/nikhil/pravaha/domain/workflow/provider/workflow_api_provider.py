from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from ..service.workflow_service import WorkflowService
from ..entity.workflow import Workflow
from ..entity.workflow_run import WorkflowRun

class WorkflowAPIProvider:
    def __init__(self, workflow_service: WorkflowService):
        self.workflow_service = workflow_service
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        # Workflow CRUD
        self.router.post("/workflow", response_model=Workflow)(self.create_workflow)
        self.router.get("/workflow", response_model=List[Workflow])(self.list_workflows)
        self.router.get("/workflow/{workflow_id}", response_model=Workflow)(self.get_workflow)
        self.router.delete("/workflow/{workflow_id}")(self.delete_workflow)

        # Execution
        self.router.post("/run", response_model=WorkflowRun)(self.trigger_run)
        self.router.get("/run/{run_id}", response_model=WorkflowRun)(self.get_run)
        self.router.get("/run", response_model=List[WorkflowRun])(self.list_runs)

    async def create_workflow(self, workflow: Workflow):
        return self.workflow_service.create_workflow(workflow)

    async def list_workflows(self):
        return self.workflow_service.list_workflows()

    async def get_workflow(self, workflow_id: str):
        wf = self.workflow_service.get_workflow(workflow_id)
        if not wf:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return wf

    async def delete_workflow(self, workflow_id: str):
        self.workflow_service.delete_workflow(workflow_id)
        return {"status": "deleted"}

    async def trigger_run(self, workflow_id: str, background_tasks: BackgroundTasks):
        try:
            run = await self.workflow_service.trigger_run(workflow_id)
            # Schedule execution in background
            background_tasks.add_task(self.workflow_service.execute_run, run.id)
            return run
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def get_run(self, run_id: str):
        run = self.workflow_service.get_run(run_id)
        if not run:
             raise HTTPException(status_code=404, detail="Run not found")
        return run

    async def list_runs(self, workflow_id: Optional[str] = None):
        if workflow_id:
            return self.workflow_service.list_runs(workflow_id)
        # If no workflow_id provided, likely return all or error. 
        # Protocol `list_by_workflow` implies filtering by workflow.
        # Ideally we implement list_all in repo if needed.
        # For now, let's return error if missing, or empty list.
        # Update: Spec didn't strictly say list ALL runs globally, but it's useful.
        # To be safe and compliant with existing repo protocol, we require workflow_id or we iterate all workflows?
        # Let's check `RunRepositoryProtocol`: only `list_by_workflow` existed.
        # So we mandate `workflow_id` in query for now.
        if workflow_id is None:
             raise HTTPException(status_code=400, detail="workflow_id query parameter is required")
        return self.workflow_service.list_runs(workflow_id)
