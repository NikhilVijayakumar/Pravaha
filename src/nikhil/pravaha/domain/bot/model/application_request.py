from typing import Any, Optional, List, Dict

from pydantic import BaseModel


class ApplicationRequest(BaseModel):
    task_name: Any
    inputs: Optional[List[Dict[str, Any]]] = None