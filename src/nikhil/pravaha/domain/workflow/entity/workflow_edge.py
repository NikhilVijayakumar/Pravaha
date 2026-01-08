from pydantic import BaseModel
from typing import Optional

class WorkflowEdge(BaseModel):
    id: str
    source: str  # Source node ID
    target: str  # Target node ID
    sourceHandle: Optional[str] = None  # Output handle on source node
    targetHandle: Optional[str] = None  # Input handle on target node
