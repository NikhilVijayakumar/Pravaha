# src.nikhil.pravaha.domain.api.factory.api_factory.py
import inspect

import fastapi
from fastapi import APIRouter, HTTPException, FastAPI
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from pravaha.domain.api.protocol.bot_manager_protocol import BotManagerProtocol
from pravaha.domain.api.protocol.task_config_protocol import TaskConfigProtocol
from pravaha.domain.api.streaming.sync_to_async import stream_from_sync_iterable


def _sse_format(data: str) -> str:
    # Basic SSE formatting (client expects "data: <line>.n.n")
    return f"data: {data}.n.n"

def create_bot_api(
    bot_manager: BotManagerProtocol,
    task_config: TaskConfigProtocol,
    *,
    route_prefix: str = "",
) -> APIRouter:
    """
    Create an APIRouter with:
     - /run/utility        -> synchronous utility endpoint
     - /run/application/stream -> SSE streaming endpoint
     - /enums/*            -> enums exposure
    The `bot_manager` must satisfy BotManagerProtocol.
    The `task_config` must expose UtilsType, ApplicationType, ExecutionTarget Enums.
    """
    router = APIRouter(prefix=route_prefix)

    UtilsType = task_config.UtilsType
    ApplicationType = task_config.ApplicationType
    ExecutionTarget = task_config.ExecutionTarget

    class UtilityRequest(BaseModel):
        task_name: UtilsType

    class ApplicationRequest(BaseModel):
        task_name: ApplicationType


    @router.post("/run/utility")
    async def run_utility(req: UtilityRequest):
        try:

            result = bot_manager.run(req.task_name)
            return {"status": "success", "result": result}
        except Exception as e:
            # map to HTTP 500 with type name
            raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

    @router.post("/run/application/stream")
    async def run_application_stream(req: ApplicationRequest):
        """
        Streams responses as SSE. Accepts both sync and async iterables from bot_manager.stream_run.
        """
        try:
            stream = bot_manager.stream_run(req.task_name)

            async def event_generator():
                # If async generator / async iterable:
                if inspect.isasyncgen(stream) or inspect.isawaitable(getattr(stream, "__aiter__", None)):
                    async for chunk in stream:  # type: ignore
                        yield _sse_format(str(chunk))
                # If sync iterable/generator:
                elif hasattr(stream, "__iter__") and not isinstance(stream, (str, bytes)):
                    async for chunk in stream_from_sync_iterable(stream):  # type: ignore
                        yield _sse_format(str(chunk))
                else:
                    # If it's a single non-iterable result, just yield it once
                    yield _sse_format(str(stream))
                # final sentinel to client
                yield _sse_format("[DONE]")

            # EventSourceResponse handles headers and streaming lifecycle
            return EventSourceResponse(event_generator(),
                                       headers={
                                           "Cache-Control": "no-cache",
                                           "Connection": "keep-alive",
                                           "X-Accel-Buffering": "no"
                                       })

        except Exception as e:
            # In case of an error before streaming starts
            raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

    # Enum endpoints
    @router.get("/enums/util-types")
    async def util_types():
        return [u.value for u in UtilsType]

    @router.get("/enums/application-types")
    async def app_types():
        return [a.value for a in ApplicationType]

    @router.get("/enums/execution-targets")
    async def exec_targets():
        return [e.value for e in ExecutionTarget]

    return router


def create_fastapi_app(bot_manager: BotManagerProtocol, task_config: TaskConfigProtocol,prefix="api") -> "fastapi.FastAPI":
    """
    Convenience helper to create a full FastAPI app including the bot router and
    a simple health endpoint. Client can call this to get an app object to run.
    """
    app = FastAPI()
    app.include_router(create_bot_api(bot_manager, task_config), prefix=f"/{prefix}")
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    return app
