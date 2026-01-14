import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..protocol.workflow_repository_protocol import WorkflowRepositoryProtocol
from ..protocol.run_repository_protocol import RunRepositoryProtocol
from ..protocol.orchestration_engine_protocol import OrchestrationEngineProtocol
from ..entity.workflow import Workflow
from ..entity.workflow_run import WorkflowRun
from ..entity.run_state import RunState
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager

class WorkflowService:
    def __init__(
        self,
        workflow_repo: WorkflowRepositoryProtocol,
        run_repo: RunRepositoryProtocol,
        orchestration_engine: OrchestrationEngineProtocol
    ):
        self.workflow_repo = workflow_repo
        self.run_repo = run_repo
        self.orchestration_engine = orchestration_engine
        self.logger = PravphaLoggingManager.get_logger()

    def create_workflow(self, workflow: Workflow) -> Workflow:
        # Auto-generate ID and timestamps
        if not workflow.id:
            workflow.id = str(uuid.uuid4())
        self.logger.debug(f"Creating workflow with ID: {workflow.id}, name: {workflow.name}")
        
        if not workflow.created_at:
            workflow.created_at = datetime.now().isoformat()
        if not workflow.updated_at:
            workflow.updated_at = workflow.created_at
        
        self.workflow_repo.save(workflow)
        self.logger.info(f"Workflow created and saved: {workflow.id}")
        return workflow

    def update_workflow(self, workflow: Workflow) -> Workflow:
        if not workflow.id:
            raise ValueError("Workflow ID is required for update")
        
        self.logger.debug(f"Updating workflow: {workflow.id}")
        existing = self.workflow_repo.get(workflow.id)
        if not existing:
            self.logger.warning(f"Workflow not found for update: {workflow.id}")
            raise ValueError(f"Workflow {workflow.id} not found")
        
        # Update timestamp
        workflow.updated_at = datetime.now().isoformat()
        
        self.workflow_repo.save(workflow)
        self.logger.info(f"Workflow updated successfully: {workflow.id}")
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self.workflow_repo.get(workflow_id)

    def list_workflows(self) -> List[Workflow]:
        return self.workflow_repo.list_all()

    def delete_workflow(self, workflow_id: str) -> None:
        self.logger.info(f"Deleting workflow: {workflow_id}")
        self.workflow_repo.delete(workflow_id)
        self.logger.info(f"Workflow deleted: {workflow_id}")
    
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

    def trigger_run(self, workflow_id: str) -> WorkflowRun:
        """
        Initialize a new workflow run for client-driven execution.
        Creates run and initializes orchestration state.
        """
        self.logger.info(f"Triggering run for workflow: {workflow_id}")
        workflow = self.workflow_repo.get(workflow_id)
        if not workflow:
            self.logger.error(f"Cannot trigger run - workflow not found: {workflow_id}")
            raise ValueError(f"Workflow {workflow_id} not found")

        # Create new Run
        run = WorkflowRun(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            status=RunState.PENDING,
            created_at=datetime.now()
        )
        
        self.logger.info(f"Initializing run: {run.id} for workflow: {workflow_id}")
        # Initialize orchestration state (marks root nodes PENDING)
        run = self.orchestration_engine.initialize_run(workflow, run)
        self.logger.info(f"Run initialized successfully: {run.id}, status: {run.status.value}")
        
        return run
    
    def get_run_status(self, run_id: str) -> Dict[str, Any]:
        """
        Get current run status with next pending node for client polling.
        Also checks for stale nodes stuck in IN_PROGRESS.
        """
        run = self.run_repo.get(run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found")
        
        workflow = self.workflow_repo.get(run.workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {run.workflow_id} not found")
        
        # Check for stale nodes (orphaned)
        run = self.orchestration_engine.check_stale_nodes(run)
        
        # Get next pending node
        current_node = self.orchestration_engine.get_next_pending_node(workflow, run)
        
        response = {
            "run_id": run.id,
            "status": run.status.value,
            "current_node": None,
            "nodes_status": {node_id: state.value for node_id, state in run.node_states.items()}
        }
        
        if current_node:
            response["current_node"] = {
                "node_id": current_node.id,
                "node_type": current_node.node_type.value,
                "task_name": current_node.task_name,
                "status": run.node_states[current_node.id].value,
                "retry_count": run.retry_counts.get(current_node.id, 0)
            }
        
        return response
    
    def update_node_status(
        self, 
        run_id: str, 
        node_id: str, 
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        retry_attempt: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update node status based on client execution result.
        """
        self.logger.debug(f"Updating node status: run={run_id}, node={node_id}, status={status}")
        run = self.run_repo.get(run_id)
        if not run:
            self.logger.error(f"Run not found for node status update: {run_id}")
            raise ValueError(f"Run {run_id} not found")
        
        workflow = self.workflow_repo.get(run.workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {run.workflow_id} not found")
        
        status_enum = RunState(status)
        
        if status_enum == RunState.IN_PROGRESS:
            self.logger.info(f"Marking node IN_PROGRESS: run={run_id}, node={node_id}")
            run = self.orchestration_engine.mark_node_in_progress(run, node_id)
        
        elif status_enum == RunState.COMPLETED:
            self.logger.info(f"Completing node: run={run_id}, node={node_id}")
            run = self.orchestration_engine.complete_node(run, workflow, node_id, output_data)
            self.logger.info(f"Node completed successfully: run={run_id}, node={node_id}")
        
        elif status_enum == RunState.FAILED:
            retry = retry_attempt is not None
            self.logger.warning(f"Node failed: run={run_id}, node={node_id}, error={error}, retry={retry}")
            run = self.orchestration_engine.fail_node(run, node_id, error or "Unknown error", retry)
        
        else:
            self.logger.error(f"Invalid status for update: {status}")
            raise ValueError(f"Invalid status for update: {status}")
        
        return {
            "success": True,
            "run_status": run.status.value
        }
    
    def get_node_output(self, run_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get output data from a completed node.
        """
        return self.run_repo.get_node_output(run_id, node_id)

    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        return self.run_repo.get(run_id)

    def list_runs(self, workflow_id: str) -> List[WorkflowRun]:
        return self.run_repo.list_by_workflow(workflow_id)

    def list_all_runs(self) -> List[WorkflowRun]:
        """Return all runs across all workflows"""
        return self.run_repo.list_all()
