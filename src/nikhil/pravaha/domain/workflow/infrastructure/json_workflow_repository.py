import json
import os
from typing import List, Optional
from ..protocol.workflow_repository_protocol import WorkflowRepositoryProtocol
from ..entity.workflow import Workflow

class JsonWorkflowRepository(WorkflowRepositoryProtocol):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            dirname = os.path.dirname(self.file_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def _load(self) -> List[Workflow]:
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                return [Workflow(**item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_all(self, workflows: List[Workflow]):
        data = [w.model_dump(mode='json') for w in workflows]
        # Atomic write
        temp_path = f"{self.file_path}.tmp"
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, self.file_path)

    def save(self, workflow: Workflow) -> None:
        workflows = self._load()
        existing_idx = next((i for i, w in enumerate(workflows) if w.id == workflow.id), -1)
        
        if existing_idx >= 0:
            workflows[existing_idx] = workflow
        else:
            workflows.append(workflow)
        
        self._save_all(workflows)

    def get(self, workflow_id: str) -> Optional[Workflow]:
        workflows = self._load()
        return next((w for w in workflows if w.id == workflow_id), None)

    def list_all(self) -> List[Workflow]:
        return self._load()

    def delete(self, workflow_id: str) -> None:
        workflows = self._load()
        workflows = [w for w in workflows if w.id != workflow_id]
        self._save_all(workflows)
