from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ..service.workflow_service import WorkflowService
from ..entity.workflow import Workflow
from ..entity.workflow_run import WorkflowRun

class WorkflowRenameRequest(BaseModel):
    id: str
    new_name: str

class NodeStatusUpdateRequest(BaseModel):
    status: str  # "IN_PROGRESS" | "COMPLETED" | "FAILED"
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_attempt: Optional[int] = None

class WorkflowAPIProvider:
    def __init__(self, workflow_service: WorkflowService):
        self.workflow_service = workflow_service
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        # Workflow CRUD
        self.router.post("/workflow/create", response_model=Workflow)(self.create_workflow)
        self.router.post("/workflow/update", response_model=Workflow)(self.update_workflow)
        self.router.post("/workflow/rename", response_model=Workflow)(self.rename_workflow)
        self.router.get("/workflow/list", response_model=List[Workflow])(self.list_workflows)
        self.router.get("/workflow/{workflow_id}", response_model=Workflow)(self.get_workflow)
        self.router.delete("/workflow/{workflow_id}")(self.delete_workflow)

        # Client-Driven Execution API
        self.router.post("/execution/run")(self.start_execution)
        self.router.get("/execution/run/{run_id}/status")(self.get_execution_status)
        self.router.post("/execution/run/{run_id}/node/{node_id}/status")(self.update_node_status)
        self.router.get("/execution/run/{run_id}/node/{node_id}/output")(self.get_node_output)
        
        # Original endpoints (for backwards compatibility during transition)
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
    
    async def rename_workflow(self, request: WorkflowRenameRequest):
        try:
            return self.workflow_service.rename_workflow(request.id, request.new_name)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def trigger_run(self, workflow_id: str):
        """Legacy endpoint - redirects to start_execution"""
        return await self.start_execution({"workflow_id": workflow_id})
    
    async def start_execution(self, payload: Dict[str, str]):
        """Initialize a new workflow run for client-driven execution"""
        workflow_id = payload.get("workflow_id")
        if not workflow_id:
            raise HTTPException(status_code=400, detail="workflow_id required")
        
        try:
            run = self.workflow_service.trigger_run(workflow_id)
            return {
                "workflow_run_id": run.id,
                "status": run.status.value
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    async def get_execution_status(self, run_id: str):
        """Get current run status with next pending node for client polling"""
        try:
            return self.workflow_service.get_run_status(run_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    async def update_node_status(self, run_id: str, node_id: str, request: NodeStatusUpdateRequest):
        """Update node status based on client execution result"""
        try:
            return self.workflow_service.update_node_status(
                run_id=run_id,
                node_id=node_id,
                status=request.status,
                output_data=request.output_data,
                error=request.error,
                retry_attempt=request.retry_attempt
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_node_output(self, run_id: str, node_id: str):
        """Get output data from a completed node"""
        output = self.workflow_service.get_node_output(run_id, node_id)
        if output is None:
            raise HTTPException(status_code=404, detail="Node output not found")
        return output

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
