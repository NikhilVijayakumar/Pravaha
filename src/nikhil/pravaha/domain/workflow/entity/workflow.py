from pydantic import BaseModel, Field
from typing import List, Optional
from .workflow_node import WorkflowNode
from .workflow_edge import WorkflowEdge

class Workflow(BaseModel):
    id: Optional[str] = None  # Auto-generated on create
    name: str  # e.g. "My Processing Pipeline"
    description: str = ""
    nodes: List[WorkflowNode] = []
    edges: List[WorkflowEdge] = []
    created_at: Optional[str] = None  # ISO 8601 timestamp
    updated_at: Optional[str] = None  # ISO 8601 timestamp
