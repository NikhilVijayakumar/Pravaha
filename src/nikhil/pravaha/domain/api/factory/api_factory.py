import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pravaha.domain.bot.provider.bot_api_provider import BotAPIProvider
from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider

# Workflow Imports
from pravaha.domain.workflow.manager.local_workflow_manager import LocalWorkflowManager
from pravaha.domain.workflow.infrastructure.json_workflow_repository import JsonWorkflowRepository
from pravaha.domain.workflow.infrastructure.json_run_repository import JsonRunRepository
from pravaha.domain.workflow.service.simple_orchestration_engine import SimpleOrchestrationEngine
from pravaha.domain.workflow.service.workflow_service import WorkflowService
from pravaha.domain.workflow.provider.workflow_api_provider import WorkflowAPIProvider
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager


from typing import Optional
from pathlib import Path

def create_fastapi_app(
    bot_manager, 
    task_config, 
    storage_manager, 
    prefix="api", 
    title="Akashvani Unified API", 
    llm_config_path: Optional[str] = None,
    workflow_defaults: Optional[dict[str, str]] = None
) -> FastAPI:
    logger = PravphaLoggingManager.get_logger()
    logger.info(f"Creating FastAPI application: {title}")
    
    app = FastAPI(title=title)
    logger.debug("FastAPI instance created")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.debug("CORS middleware configured")

    # Initialize Class-Based Providers
    bot_provider = BotAPIProvider(bot_manager, task_config)
    logger.debug("Bot provider initialized")
    
    # Initialize Storage Components
    # We rely on defaults or can pass config path if needed
    from pravaha.domain.storage.manager.llm_config_manager import LLMConfigManager
    from pravaha.domain.storage.logic.path_resolver import StoragePathResolver
    from pravaha.domain.storage.logic.version_resolver import ArtifactVersionResolver
    
    llm_config_manager = LLMConfigManager(Path(llm_config_path) if llm_config_path else None)
    version_resolver = ArtifactVersionResolver(storage_manager, llm_config_manager)
    path_resolver = StoragePathResolver(storage_manager, llm_config_manager, version_resolver)
    
    storage_provider = StorageAPIProvider(
        storage_manager,
        llm_config_manager,
        path_resolver,
        version_resolver
    )
    logger.debug("Storage provider initialized")

    # Initialize Workflow Components
    workflow_manager = LocalWorkflowManager(defaults=workflow_defaults)
    workflow_repo = JsonWorkflowRepository(workflow_manager)
    run_repo = JsonRunRepository(workflow_manager)
    
    # Orchestration Engine (state management only, no execution)
    # Client-driven execution means backend doesn't need task executor
    orchestration_engine = SimpleOrchestrationEngine(run_repo)
    workflow_service = WorkflowService(workflow_repo, run_repo, orchestration_engine)
    
    # Provider
    workflow_provider = WorkflowAPIProvider(workflow_service, workflow_manager)
    logger.debug(f"Workflow provider initialized with defaults: {workflow_defaults}")
    
    # LLM Provider
    from pravaha.domain.llm.provider.llm_api_provider import LLMAPIProvider
    llm_api_provider = LLMAPIProvider(llm_config_manager)
    logger.debug("LLM provider initialized")

    # Mount Routers
    app.include_router(bot_provider.router, prefix=f"/{prefix}")
    app.include_router(storage_provider.router, prefix=f"/{prefix}")
    app.include_router(workflow_provider.router, prefix=f"/{prefix}")
    app.include_router(llm_api_provider.router, prefix=f"/{prefix}/llm")
    logger.info("All API routers mounted successfully")
    logger.info(f"Application {title} ready to serve at /{prefix}")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app