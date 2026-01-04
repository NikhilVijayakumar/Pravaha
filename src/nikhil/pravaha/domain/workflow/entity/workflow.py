from pydantic import BaseModel, Field
from typing import List
from .workflow_node import WorkflowNode
from .workflow_edge import WorkflowEdge

class Workflow(BaseModel):
    id: str
    name: str # e.g. "My Processing Pipeline"
    description: str = ""
    nodes: List[WorkflowNode] = []
    edges: List[WorkflowEdge] = []
