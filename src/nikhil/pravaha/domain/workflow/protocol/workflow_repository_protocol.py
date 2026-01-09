from typing import Protocol, List, Optional
from ..entity.workflow import Workflow

class WorkflowRepositoryProtocol(Protocol):
    def save(self, workflow: Workflow) -> None:
        ...

    def get(self, workflow_id: str) -> Optional[Workflow]:
        ...
    
    def list_all(self) -> List[Workflow]:
        ...
    
    def delete(self, workflow_id: str) -> None:
        ...
    
    def rename(self, workflow_id: str, new_name: str) -> None:
        ...
