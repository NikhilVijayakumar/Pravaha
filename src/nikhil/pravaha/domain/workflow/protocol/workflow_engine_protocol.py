from typing import Protocol
from ..entity.workflow import Workflow
from ..entity.workflow_run import WorkflowRun

class WorkflowEngineProtocol(Protocol):
    async def execute_run(self, workflow: Workflow, run: WorkflowRun) -> None:
        ...
