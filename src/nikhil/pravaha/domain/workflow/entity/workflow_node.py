from pydantic import BaseModel
from typing import Dict, Any, Optional

class InputItem(BaseModel):
    key_name: str  # Changed from 'name' to match frontend
    source: str  # "direct" | "file" | node_id for node output reference
    value: Optional[Any] = None  # For direct input
    path: Optional[str] = None  # For file input
    format: Optional[str] = None  # "json" | "text" for file inputs

class WorkflowNode(BaseModel):
    id: str
    task_type: str  # "APP" | "UTIL" | "LLM" | "ENVIRONMENT"
    task_name: str  # Must match enum value from TaskConfig
    inputs: Dict[str, InputItem] = {}  # Changed from List to Dict for efficient lookups
    position: Optional[Dict[str, float]] = None  # {x: float, y: float} for visual editor
    llm_config: Optional[Dict[str, Any]] = None  # LLM configuration override
    environment_config: Optional[Dict[str, Any]] = None  # Environment variables
    ui_metadata: Optional[Dict[str, Any]] = None  # Additional UI state
