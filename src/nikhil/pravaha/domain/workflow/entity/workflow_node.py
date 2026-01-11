from pydantic import BaseModel
from typing import Dict, Any, Optional
from enum import Enum

class NodeType(str, Enum):
    """Classification of workflow nodes for execution behavior"""
    APPLICATION = "APP"  # Executable: Full domain application
    UTILITY = "UTIL"  # Executable: Helper function or data transform
    LLM_CONFIG = "LLM"  # Configuration: Local LLM settings for specific node
    GLOBAL_LLM = "GLOBAL_LLM"  # Configuration: Default LLM for entire workflow
    ENVIRONMENT = "ENVIRONMENT"  # Configuration: Environment variables
    NOTE = "NOTE"  # UI-only: Documentation/comments
    GROUP = "GROUP"  # UI-only: Visual grouping container

class InputItem(BaseModel):
    key_name: str  # Changed from 'name' to match frontend
    source: str  # "direct" | "file" | node_id for node output reference
    value: Optional[Any] = None  # For direct input
    path: Optional[str] = None  # For file input
    format: Optional[str] = None  # "json" | "text" for file inputs

class WorkflowNode(BaseModel):
    id: str
    node_type: NodeType  # Changed from task_type string to NodeType enum
    task_name: str  # Must match enum value from TaskConfig
    inputs: Dict[str, InputItem] = {}  # Changed from List to Dict for efficient lookups
    position: Optional[Dict[str, float]] = None  # {x: float, y: float} for visual editor
    llm_config: Optional[Dict[str, Any]] = None  # LLM configuration override
    environment_config: Optional[Dict[str, Any]] = None  # Environment variables
    ui_metadata: Optional[Dict[str, Any]] = None  # Additional UI state (label, description)
    
    def is_executable(self) -> bool:
        """Returns True if this node type should be executed (APP or UTIL)"""
        return self.node_type in (NodeType.APPLICATION, NodeType.UTILITY)
