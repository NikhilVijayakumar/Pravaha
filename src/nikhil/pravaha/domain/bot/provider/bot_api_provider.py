import inspect
from fastapi import APIRouter, HTTPException
from pravaha.domain.bot.model.application_request import ApplicationRequest
from pravaha.domain.bot.model.utility_request import UtilityRequest
from pravaha.domain.bot.streaming.sync_to_async import stream_from_sync_iterable
from sse_starlette.sse import EventSourceResponse



class BotAPIProvider:
    def __init__(self, bot_manager, task_config):
        self.bot_manager = bot_manager
        self.task_config = task_config
        self.router = APIRouter()
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

    async def run_utility(self, req: UtilityRequest):
        try:
            result = self.bot_manager.run(req.task_name, inputs=req.inputs)
            return {"status": "success", "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

    async def run_application_stream(self, req: ApplicationRequest):
        try:
            if req.inputs:
                stream = self.bot_manager.stream_run(req.task_name, inputs=req.inputs)
            else:
                stream = self.bot_manager.stream_run(req.task_name)

            return EventSourceResponse(
                self._event_generator(stream),
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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