import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from ..protocol.run_repository_protocol import RunRepositoryProtocol
from ..entity.workflow_run import WorkflowRun
from ..entity.run_state import RunState
from ..manager.local_workflow_manager import LocalWorkflowManager
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager

class JsonRunRepository(RunRepositoryProtocol):
    def __init__(self, workflow_manager: LocalWorkflowManager):
        self.workflow_manager = workflow_manager
        self.logger = PravphaLoggingManager.get_logger()
        self._ensure_directory()
        self.logger.debug("JsonRunRepository initialized")

    def _ensure_directory(self):
        """Ensure the workflow run directory exists."""
        run_path = self.workflow_manager.get_path("run")
        run_path.mkdir(parents=True, exist_ok=True)

    def _get_run_file_path(self, run_id: str) -> Path:
        """Get the file path for a specific run."""
        run_path = self.workflow_manager.get_path("run")
        return run_path / f"{run_id}.json"

    def _load_run(self, run_id: str) -> Optional[WorkflowRun]:
        """Load a single run from its JSON file."""
        file_path = self._get_run_file_path(run_id)
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                return WorkflowRun(**data)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def _save_run(self, run: WorkflowRun):
        """Save a single run to its JSON file."""
        file_path = self._get_run_file_path(run.id)
        self.logger.debug(f"Saving run to file: {file_path}, status: {run.status.value}")
        
        data = run.model_dump(mode='json')
        
        # Atomic write
        temp_path = file_path.with_suffix('.tmp')
        try:
            with open(temp_path, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, file_path)
            self.logger.debug(f"Run saved successfully: {run.id}")
        except Exception as e:
            self.logger.error(f"Failed to save run {run.id}: {e}")
            raise

    def save(self, run: WorkflowRun) -> None:
        self._save_run(run)

    def get(self, run_id: str) -> Optional[WorkflowRun]:
        return self._load_run(run_id)

    def update_node_state(self, run_id: str, node_id: str, state: RunState) -> None:
        run = self._load_run(run_id)
        if run:
            run.node_states[node_id] = state
            self.save(run)

    def list_by_workflow(self, workflow_id: str) -> List[WorkflowRun]:
        """List all runs for a specific workflow."""
        run_path = self.workflow_manager.get_path("run")
        runs = []
        
        for file_path in run_path.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    run = WorkflowRun(**data)
                    if run.workflow_id == workflow_id:
                        runs.append(run)
            except (json.JSONDecodeError, ValueError):
                # Skip invalid files
                continue
        
        return runs

    def list_all(self) -> List[WorkflowRun]:
        """Return all runs across all workflows"""
        run_path = self.workflow_manager.get_path("run")
        runs = []
        
        for file_path in run_path.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    runs.append(WorkflowRun(**data))
            except (json.JSONDecodeError, ValueError):
                # Skip invalid files
                continue
        
        return runs
    
    def save_node_output(self, run_id: str, node_id: str, output: Dict[str, Any]) -> None:
        """Save output data for a specific node in a run."""
        self.logger.debug(f"Saving node output: run={run_id}, node={node_id}")
        run = self.get(run_id)
        if run:
            run.node_outputs[node_id] = output
            self.save(run)
            self.logger.debug(f"Node output saved: run={run_id}, node={node_id}")
        else:
            self.logger.warning(f"Run not found for saving node output: {run_id}")
    
    def get_node_output(self, run_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        """Get output data for a specific node in a run."""
        run = self.get(run_id)
        if run:
            return run.node_outputs.get(node_id)
        return None
