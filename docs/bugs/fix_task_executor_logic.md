# Bug Report: PravahaTaskExecutor Implementation Issues

**Date**: 2026-01-12
**Status**: Open
**Severity**: High
**Component**: Workflow Infrastructure

## Description
The file `src/nikhil/pravaha/domain/workflow/infrastructure/pravaha_task_executor.py` contains severe implementation issues preventing correct workflow execution.

## Issues Identified
1.  **Duplicate Code**: The file contains multiple conflicting definitions of the `PravahaTaskExecutor` class and its `__init__` method.
2.  **Incorrect Type Resolution**: The code attempts to resolve `task_name` strings to Enums (`UtilsType`/`ApplicationType`) using a `task_config` attribute that is not properly injected or standard.
3.  **Ignoring Task Type**: The generic `execute` method does not correctly utilize the `task_type` argument passed by the workflow engine to distinguish between streaming (APP) and blocking (UTIL) executions.

## Expected Behavior
The `PravahaTaskExecutor` should:
1.  Accept `task_type` (e.g., 'APP', 'UTIL') and `task_name` (str) from the engine.
2.  Route 'APP' tasks to `bot_manager.stream_run(task_name, inputs)`.
3.  Route 'UTIL' tasks to `bot_manager.run(task_name, inputs)`.
4.  Rely on the `BotManager` (in Akashavani) to handle `str` -> `Enum` conversion if supported, or receive `task_name` as a valid valid identifier.

## logic of the proposed fix
```python
    async def execute(
        self,
        task_type: str,
        task_name: str,
        inputs: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False
    ) -> Union[Any, AsyncIterable[str]]:
        
        normalized_type = task_type.upper()
        
        if normalized_type in ["APP", "APPLICATION"]:
            # Delegate to BotManager stream_run for Applications
            return self.bot_manager.stream_run(task_name, inputs=inputs)
            
        elif normalized_type in ["UTIL", "UTILITY"]:
             # Delegate to BotManager run for Utilities
             return self.bot_manager.run(task_name, inputs=inputs)
             
        else:
            raise ValueError(f"Unsupported task_type: {task_type}")
```
