import json
import os
from typing import List, Optional
from pathlib import Path
from ..protocol.workflow_repository_protocol import WorkflowRepositoryProtocol
from ..entity.workflow import Workflow
from ..manager.local_workflow_manager import LocalWorkflowManager
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager

class JsonWorkflowRepository(WorkflowRepositoryProtocol):
    def __init__(self, workflow_manager: LocalWorkflowManager):
        self.workflow_manager = workflow_manager
        self.logger = PravphaLoggingManager.get_logger()
        self._ensure_directory()
        self.logger.debug("JsonWorkflowRepository initialized")

    def _ensure_directory(self):
        """Ensure the workflow details directory exists."""
        details_path = self.workflow_manager.get_path("details")
        details_path.mkdir(parents=True, exist_ok=True)

    def _get_workflow_file_path(self, workflow_id: str) -> Path:
        """Get the file path for a specific workflow."""
        details_path = self.workflow_manager.get_path("details")
        return details_path / f"{workflow_id}.json"

    def _load_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Load a single workflow from its JSON file."""
        file_path = self._get_workflow_file_path(workflow_id)
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                return Workflow(**data)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def _save_workflow(self, workflow: Workflow):
        """Save a single workflow to its JSON file."""
        file_path = self._get_workflow_file_path(workflow.id)
        self.logger.debug(f"Saving workflow to file: {file_path}")
        
        data = workflow.model_dump(mode='json')
        
        # Atomic write
        temp_path = file_path.with_suffix('.tmp')
        try:
            with open(temp_path, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, file_path)
            self.logger.debug(f"Workflow saved successfully: {workflow.id}")
        except Exception as e:
            self.logger.error(f"Failed to save workflow {workflow.id}: {e}")
            raise

    def save(self, workflow: Workflow) -> None:
        self._save_workflow(workflow)

    def get(self, workflow_id: str) -> Optional[Workflow]:
        return self._load_workflow(workflow_id)

    def list_all(self) -> List[Workflow]:
        """List all workflows by reading all JSON files in the details directory."""
        details_path = self.workflow_manager.get_path("details")
        self.logger.debug(f"Listing all workflows from: {details_path}")
        
        workflows = []
        invalid_count = 0
        
        for file_path in details_path.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    workflows.append(Workflow(**data))
            except (json.JSONDecodeError, ValueError) as e:
                invalid_count += 1
                self.logger.warning(f"Skipping invalid workflow file: {file_path.name}, error: {e}")
                continue
        
        self.logger.info(f"Loaded {len(workflows)} workflows, skipped {invalid_count} invalid files")
        return workflows

    def delete(self, workflow_id: str) -> None:
        """Delete a workflow by removing its JSON file."""
        file_path = self._get_workflow_file_path(workflow_id)
        if file_path.exists():
            file_path.unlink()
            self.logger.info(f"Deleted workflow file: {workflow_id}")
        else:
            self.logger.warning(f"Workflow file not found for deletion: {workflow_id}")
    
    def rename(self, workflow_id: str, new_name: str) -> None:
        """Rename a workflow by updating only its name and updated_at timestamp."""
        from datetime import datetime
        
        workflow = self._load_workflow(workflow_id)
        
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow.name = new_name
        workflow.updated_at = datetime.now().isoformat()
        
        self._save_workflow(workflow)

