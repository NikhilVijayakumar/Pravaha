from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime
from .run_state import RunState

class WorkflowRun(BaseModel):
    id: str
    workflow_id: str
    status: RunState = RunState.PENDING
    node_states: Dict[str, RunState] = Field(default_factory=dict) # NodeID -> State
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
