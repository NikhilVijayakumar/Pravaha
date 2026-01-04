from pydantic import BaseModel

class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
