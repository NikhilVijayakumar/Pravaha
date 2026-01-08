from typing import Protocol, Optional, List
from ..entity.workflow_run import WorkflowRun
from ..entity.run_state import RunState

class RunRepositoryProtocol(Protocol):
    def save(self, run: WorkflowRun) -> None:
        ...

    def get(self, run_id: str) -> Optional[WorkflowRun]:
        ...

    def update_node_state(self, run_id: str, node_id: str, state: RunState) -> None:
        ...
    
    def list_by_workflow(self, workflow_id: str) -> List[WorkflowRun]:
        ...

    def list_all(self) -> List[WorkflowRun]:
        """Return all runs across all workflows"""
        ...
