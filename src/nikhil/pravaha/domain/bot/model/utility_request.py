from typing import Any, Optional, List, Dict

from pydantic import BaseModel


class UtilityRequest(BaseModel):
    task_name: Any  # Type-hinted dynamically in the router
    inputs: Optional[List[Dict[str, Any]]] = None