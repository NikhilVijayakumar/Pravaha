from typing import Any, List, Dict, Optional, Union, AsyncIterable
from ...bot.protocol.bot_manager_protocol import BotManagerProtocol
from ..protocol.task_executor_protocol import TaskExecutorProtocol

class PravahaTaskExecutor(TaskExecutorProtocol):
    def __init__(self, bot_manager: BotManagerProtocol):
        self.bot_manager = bot_manager

    async def execute(
        self,
        task_type: str,
        task_name: str,
        inputs: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> Union[Any, AsyncIterable[str]]:
        """
        Executes a task based on its type and name.
        Delegates strict type resolution to the BotManager.
        """
        
        normalized_type = task_type.upper()
        
        if normalized_type in ["APP", "APPLICATION"]:
            return await self.bot_manager.stream_run(task_name, inputs=inputs)
            
        elif normalized_type in ["UTIL", "UTILITY"]:
             return await self.bot_manager.run(task_name, inputs=inputs)
             
        else:
            raise ValueError(f"Unsupported task_type: {task_type}")

