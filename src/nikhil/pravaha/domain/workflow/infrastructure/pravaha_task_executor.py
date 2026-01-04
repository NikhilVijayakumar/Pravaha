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
        
        # Determine if we should treat it as Utility or Application based on task_type enum logic ideally,
        # but here we follow the simplified specification: TaskType "APPLICATION" or "UTILITY"
        
        # NOTE: BotManagerProtocol is generic [UT, AT]. We assume task_name is a valid value for the enum.
        # Since we receive string, we might need to cast it or rely on BotManager to handle strings if it does, 
        # BUT current BotManagerProtocol expects UT/AT enums. 
        # Real BotManager likely handles string resolution or we need to find the enum member.
        # Given the previous context (BotAPIProvider._get_task_enum), we know we might need the config to resolve it.
        # However, to keep this adapter clean, we'll try passing the name directly IF BotManager accepts it, 
        # OR we need to inject the TaskConfig to resolve it.
        
        # Let's check BotManagerProtocol again. It expects UT/AT.
        # To avoid circular dependency or complex injection, we will assume for now that 
        # specific implementation of BotManager can handle string lookup OR we perform it here.
        # Spec says: "PravahaTaskExecutor" implements TaskExecutorProtocol using BotManagerProtocol.
        
        # Let's assume for this implementation we inject task_config or helper as well if needed, 
        # or simplified: we'll try to resolve it if possible.
        # Actually, let's look at `BotAPIProvider`. It does `_get_task_enum`.
        # We should probably pass the TaskConfig to this Executor so it can resolve strings to Enums.
        
        # For MVP, we will assume we pass the string and let the BotManager implementation handle it 
        # OR we will improve this class to take the Enums if available.
        # Wait, BotManagerProtocol defines `run(utility_task: UT, ...)`
        # If we pass a string, it might fail type check at runtime if purely strict.
        
        # Strategy: We will add `task_config` to `__init__` to resolve Enums, similar to `BotAPIProvider`.
        pass
    
    # Re-writing class with task_config injected
    def __init__(self, bot_manager: BotManagerProtocol, task_config: Any):
        self.bot_manager = bot_manager
        self.task_config = task_config

    def _get_task_enum(self, task_name: str):
        # Try finding in UtilsType
        for member in self.task_config.UtilsType:
            if member.value == task_name:
                return member, "UTILITY"
        
        # Try finding in ApplicationType
        for member in self.task_config.ApplicationType:
            if member.value == task_name:
                return member, "APPLICATION"
        
        return None, None

    async def execute(
        self,
        task_type: str, # 'APPLICATION' or 'UTILITY' passed from Node
        task_name: str,
        inputs: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> Union[Any, AsyncIterable[str]]:
        
        task_enum, resolved_type = self._get_task_enum(task_name)
        
        if not task_enum:
            raise ValueError(f"Task '{task_name}' not found in configuration.")

        # Logic: Utility is almost always sync/blocking in this design, Application is streamable.
        # Spec says: "execute" -> Any | AsyncIterable.
        
        if resolved_type == "UTILITY":
            # Utilty run is sync
            return self.bot_manager.run(task_enum, inputs=inputs)
        
        elif resolved_type == "APPLICATION":
             if stream:
                 return self.bot_manager.stream_run(task_enum, inputs=inputs)
             else:
                 # If we want non-stream application run, we could iterate or just use stream_run
                 # But protocol implies `execute` wraps both.
                 # Let's return the stream generator if stream=True
                 return self.bot_manager.stream_run(task_enum, inputs=inputs)
        
        return None
