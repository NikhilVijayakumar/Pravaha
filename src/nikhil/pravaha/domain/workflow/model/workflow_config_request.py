from pydantic import BaseModel


class WorkflowConfigRequest(BaseModel):
    details_path: str
    run_path: str
