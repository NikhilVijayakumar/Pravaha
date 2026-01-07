from typing import Any, Optional, List, Dict

from pydantic import BaseModel, Field


class ApplicationRequest(BaseModel):
    task_name: Any
    inputs: Optional[List[Dict[str, Any]]] = None
    llm_config_override: Optional[Any] = Field(default=None, description="LLM configuration override")