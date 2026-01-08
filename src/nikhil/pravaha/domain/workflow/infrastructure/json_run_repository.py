import json
import os
from typing import List, Optional
from ..protocol.run_repository_protocol import RunRepositoryProtocol
from ..entity.workflow_run import WorkflowRun
from ..entity.run_state import RunState

class JsonRunRepository(RunRepositoryProtocol):
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

    def _load(self) -> List[WorkflowRun]:
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                runs = []
                for item in data:
                    # Convert string enum back to RunState enum if needed, though Pydantic handles str->Enum usually
                    runs.append(WorkflowRun(**item))
                return runs
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_all(self, runs: List[WorkflowRun]):
        data = [r.model_dump(mode='json') for r in runs]
        # Atomic write
        temp_path = f"{self.file_path}.tmp"
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, self.file_path)

    def save(self, run: WorkflowRun) -> None:
        runs = self._load()
        existing_idx = next((i for i, r in enumerate(runs) if r.id == run.id), -1)
        
        if existing_idx >= 0:
            runs[existing_idx] = run
        else:
            runs.append(run)
        
        self._save_all(runs)

    def get(self, run_id: str) -> Optional[WorkflowRun]:
        runs = self._load()
        return next((r for r in runs if r.id == run_id), None)

    def update_node_state(self, run_id: str, node_id: str, state: RunState) -> None:
        runs = self._load()
        run = next((r for r in runs if r.id == run_id), None)
        if run:
            run.node_states[node_id] = state
            # Optionally update overall status logic could be here, but usually Service handles that.
            # However, for simple atomicity, we just save the node state.
            self.save(run)

    def list_by_workflow(self, workflow_id: str) -> List[WorkflowRun]:
        runs = self._load()
        return [r for r in runs if r.workflow_id == workflow_id]

    def list_all(self) -> List[WorkflowRun]:
        """Return all runs across all workflows"""
        return self._load()
