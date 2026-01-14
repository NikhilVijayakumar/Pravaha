import inspect
from fastapi import APIRouter, HTTPException
from typing import Union
from pydantic import BaseModel
from pravaha.domain.bot.model.application_request import ApplicationRequest
from pravaha.domain.bot.model.utility_request import UtilityRequest
from pravaha.domain.bot.streaming.sync_to_async import stream_from_sync_iterable
from sse_starlette.sse import EventSourceResponse
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager



class BotAPIProvider:
    def __init__(self, bot_manager, task_config):
        self.bot_manager = bot_manager
        self.task_config = task_config
        self.router = APIRouter()
        self.logger = PravphaLoggingManager.get_logger()
        self._setup_routes()

    def _setup_routes(self):
        # Dynamically inject Enum types into Pydantic models for Swagger validation
        UtilityRequest.__annotations__['task_name'] = self.task_config.UtilsType
        ApplicationRequest.__annotations__['task_name'] = self.task_config.ApplicationType

        # Execution Routes
        self.router.post("/run/utility")(self.run_utility)
        self.router.post("/run/application/stream")(self.run_application_stream)

        # Enum Exposure Routes
        self.router.get("/enums/util-types")(self.get_util_types)
        self.router.get("/enums/application-types")(self.get_app_types)
        self.router.get("/enums/execution-targets")(self.get_exec_targets)

        # Schema Routes
        self.router.get("/protocol/schema/input/{task_name}")(self.get_input_schema)
        self.router.get("/protocol/schema/output/{task_name}")(self.get_output_schema)
        self.router.get("/protocol/config/{task_name}")(self.get_config)

    async def run_utility(self, req: UtilityRequest):
        self.logger.info(f"Executing utility task: {req.task_name}")
        try:
            result = self.bot_manager.run(req.task_name, inputs=req.inputs)
            self.logger.info(f"Utility task completed successfully: {req.task_name}")
            return {"status": "success", "result": result}
        except Exception as e:
            self.logger.error(f"Utility task failed: {req.task_name}, error: {e}")
            raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

    async def run_application_stream(self, req: ApplicationRequest):
        self.logger.info(f"Starting application stream: {req.task_name}")
        try:
            if req.inputs:
                stream = self.bot_manager.stream_run(req.task_name, inputs=req.inputs, llm_config=req.llm_config_override)
            else:
                stream = self.bot_manager.stream_run(req.task_name, llm_config=req.llm_config_override)

            self.logger.info(f"Application stream initialized: {req.task_name}")
            return EventSourceResponse(
                self._event_generator(stream),
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        except Exception as e:
            import traceback
            error_details = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            logger = PravphaLoggingManager.get_logger()
            logger.error(f"Stream endpoint error: {error_details}")
            raise HTTPException(status_code=500, detail=error_details)

    async def _event_generator(self, stream):
        # 1. Handle Async Iterables
        if inspect.isasyncgen(stream) or inspect.isawaitable(getattr(stream, "__aiter__", None)):
            async for chunk in stream:
                yield str(chunk)
        # 2. Handle Sync Iterables via background thread
        elif hasattr(stream, "__iter__"):
            async for chunk in stream_from_sync_iterable(stream):
                yield str(chunk)
        else:
            yield str(stream)

        yield "[DONE]"


    async def get_util_types(self):
        return [u.value for u in self.task_config.UtilsType]

    async def get_app_types(self):
        return [a.value for a in self.task_config.ApplicationType]

    async def get_exec_targets(self):
        return [e.value for e in self.task_config.ExecutionTarget]

    async def get_input_schema(self, task_name: str):
        task_enum = self._get_task_enum(task_name)
        if not task_enum:
             raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
        
        model = self.bot_manager.get_input_model(task_enum)
        if model:
            return model.model_json_schema()
        return {}

    async def get_output_schema(self, task_name: str):
        task_enum = self._get_task_enum(task_name)
        if not task_enum:
             raise HTTPException(status_code=404, detail=f"Task {task_name} not found")

        model = self.bot_manager.get_output_model(task_enum)
        if model:
            return model.model_json_schema()
        return {}
    
    async def get_config(self, task_name: str):
        """Get YAML configuration for a task as JSON."""
        task_enum = self._get_task_enum(task_name)
        if not task_enum:
             raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
        
        config = self.bot_manager.get_config(task_enum)
        if config:
            return config
        return {}

    def _get_task_enum(self, task_name: str):
        # Try finding in UtilsType
        for member in self.task_config.UtilsType:
            if member.value == task_name:
                return member
        
        # Try finding in ApplicationType
        for member in self.task_config.ApplicationType:
            if member.value == task_name:
                return member
        
        return None