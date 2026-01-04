from typing import Protocol, Any, List, Dict, Optional, Union, AsyncIterable

class TaskExecutorProtocol(Protocol):
    async def execute(
        self,
        task_type: str,
        task_name: str,
        inputs: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> Union[Any, AsyncIterable[str]]:
        ...
