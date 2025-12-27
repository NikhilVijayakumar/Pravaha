from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pravaha.domain.bot.provider.bot_api_provider import BotAPIProvider
from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider


def create_fastapi_app(bot_manager, task_config, storage_manager, prefix="api") -> FastAPI:
    app = FastAPI(title="Akashvani Unified API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize Class-Based Providers
    bot_provider = BotAPIProvider(bot_manager, task_config)
    storage_provider = StorageAPIProvider(storage_manager)

    # Mount Routers
    app.include_router(bot_provider.router, prefix=f"/{prefix}")
    app.include_router(storage_provider.router, prefix=f"/{prefix}")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app