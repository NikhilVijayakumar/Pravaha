# src.nikhil.pravaha.domain.api.factory.api_factory.py
import inspect
from typing import Optional, List, Dict, Any

import fastapi
from fastapi import APIRouter, HTTPException, FastAPI
from pravaha.domain.api.protocol.bot_manager_protocol import BotManagerProtocol
from pravaha.domain.api.protocol.task_config_protocol import TaskConfigProtocol
from pravaha.domain.api.streaming.sync_to_async import stream_from_sync_iterable
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse


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
    The `task_config` must expose utils_type, application_type, execution_target Enums.
    """
    router = APIRouter(prefix=route_prefix)

    utils_type = task_config.UtilsType
    application_type = task_config.ApplicationType
    execution_target = task_config.ExecutionTarget

    class UtilityRequest(BaseModel):
        task_name: utils_type
        inputs: Optional[List[Dict[str, Any]]] = None

    class ApplicationRequest(BaseModel):
        task_name: application_type
        inputs: Optional[List[Dict[str, Any]]] = None

    @router.post("/run/utility")
    async def run_utility(req: UtilityRequest):
        try:

            result = bot_manager.run(req.task_name, inputs=req.inputs)
            return {"status": "success", "result": result}
        except Exception as e:
            # map to HTTP 500 with type name
            raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

    @router.post("/run/application/stream")
    async def run_application_stream(req: ApplicationRequest):
        """
        Streams responses as SSE.
        Cleaned to rely on EventSourceResponse for protocol formatting.
        """
        try:
            stream = bot_manager.stream_run(req.task_name, inputs=req.inputs)

            async def event_generator():
                # 1. Handle Async Iterables
                if inspect.isasyncgen(stream) or inspect.isawaitable(getattr(stream, "__aiter__", None)):
                    async for chunk in stream:
                        # Yield raw string; EventSourceResponse adds "data: " prefix
                        yield str(chunk)

                # 2. Handle Sync Iterables (via your background thread utility)
                elif hasattr(stream, "__iter__"):
                    async for chunk in stream_from_sync_iterable(stream):
                        yield str(chunk)

                # 3. Handle Single Results
                else:
                    yield str(stream)

                # 4. Final sentinel (Frontend will check for this exact string)
                yield "[DONE]"

            return EventSourceResponse(
                event_generator(),
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

    # Enum endpoints
    @router.get("/enums/util-types")
    async def util_types():
        return [u.value for u in utils_type]

    @router.get("/enums/application-types")
    async def app_types():
        return [a.value for a in application_type]

    @router.get("/enums/execution-targets")
    async def exec_targets():
        return [e.value for e in execution_target]

    return router


def create_fastapi_app(bot_manager: BotManagerProtocol, task_config: TaskConfigProtocol,
                       prefix="api") -> "fastapi.FastAPI":
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