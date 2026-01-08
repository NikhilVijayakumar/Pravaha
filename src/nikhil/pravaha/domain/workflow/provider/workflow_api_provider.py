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
        self.router.post("/workflow/create", response_model=Workflow)(self.create_workflow)
        self.router.post("/workflow/update", response_model=Workflow)(self.update_workflow)
        self.router.get("/workflow/list", response_model=List[Workflow])(self.list_workflows)
        self.router.get("/workflow/{workflow_id}", response_model=Workflow)(self.get_workflow)
        self.router.delete("/workflow/{workflow_id}")(self.delete_workflow)

        # Execution - Nested under /workflow/run naming convention
        self.router.post("/workflow/run", response_model=WorkflowRun)(self.trigger_run)
        self.router.get("/workflow/run/{run_id}", response_model=WorkflowRun)(self.get_run)
        self.router.get("/workflow/runs", response_model=List[WorkflowRun])(self.list_runs)

    async def create_workflow(self, workflow: Workflow):
        return self.workflow_service.create_workflow(workflow)

    async def update_workflow(self, workflow: Workflow):
        try:
            return self.workflow_service.update_workflow(workflow)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

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
        else:
            # Return all runs across all workflows
            return self.workflow_service.list_all_runs()
