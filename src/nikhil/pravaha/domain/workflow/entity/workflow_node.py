from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class InputItem(BaseModel):
    name: str
    source: Optional[str] = None  # Node ID if input comes from another node
    path: Optional[str] = None    # File path if input is a file
    value: Optional[Any] = None   # Direct value

class WorkflowNode(BaseModel):
    id: str
    task_type: str  # 'APPLICATION' or 'UTILITY'
    task_name: str
    inputs: List[InputItem] = []
    ui_metadata: Optional[Dict[str, Any]] = None # For storing UI position, etc.
