# Required Dependency Changes

> [!IMPORTANT]
> The following changes are required in the `Pravaha` and `Amsha` repositories to ensure correct workflow execution and compatibility with `Akashavani`. Please revert any local modifications and request these changes from the respective repository maintainers.

## Pravaha Repository

### File: `src/nikhil/pravaha/domain/workflow/infrastructure/pravaha_task_executor.py`

**Issue:**
- The file currently contains duplicate class and method definitions (e.g., multiple `__init__` and `execute` methods).
- It attempts to resolve `task_name` strings to Enums locally using a `task_config` object that is not reliably available or standard.
- It does not correctly utilize the `task_type` passed from the workflow engine to distinguish between Application and Utility tasks.

**Required Change:**
Refactor the `PravahaTaskExecutor` class to:
1.  **Remove Duplicate Logic**: Clean up the file to have a single class definition.
2.  **Use `task_type`**: Utilize the `task_type` argument (normalized to 'APP'/'APPLICATION' or 'UTIL'/'UTILITY') to determine whether to call `stream_run` or `run`.
3.  **Delegate to BotManager**: Pass the `task_name` string directly to the `BotManager`. The `Akashavani` implementation of `BotManager` handles string-to-Enum conversion internally, so the Executor does not need to perform this lookup.

**Proposed Implementation Code:**

```python
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
            return self.bot_manager.stream_run(task_name, inputs=inputs)
            
        elif normalized_type in ["UTIL", "UTILITY"]:
             return self.bot_manager.run(task_name, inputs=inputs)
             
        else:
            raise ValueError(f"Unsupported task_type: {task_type}")
```

## Amsha Repository

### File: `src/nikhil/amsha/crew_forge/orchestrator/file/amsha_crew_file_application.py`

**Status:** ✅ **Verified**
- The current implementation correctly handles external inputs via `_prepare_multiple_inputs_for` and `_handle_external_overrides`.
- No changes are required at this time.
