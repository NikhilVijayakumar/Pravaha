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

# Authentication Imports
from pravaha.domain.auth.config.auth_config import AuthConfig
from pravaha.domain.auth.middleware.api_key_middleware import APIKeyMiddleware
from pravaha.domain.auth.repository.json_access_key_repository import JsonAccessKeyRepository
from pravaha.domain.auth.protocol.access_key_repository_protocol import AccessKeyRepositoryProtocol
from pravaha.domain.auth.provider.auth_api_provider import AuthAPIProvider

from typing import Optional
from pathlib import Path
from pravaha.domain.config.cache_config import CachePathConfig

def create_fastapi_app(
    bot_manager, 
    task_config, 
    storage_manager, 
    prefix="api", 
    title="Akashvani Unified API", 
    llm_config_path: Optional[str] = None,
    workflow_defaults: Optional[dict[str, str]] = None,
    cache_config: Optional[CachePathConfig] = None,
    auth_config: Optional[AuthConfig] = None,
    access_key_repository: Optional[AccessKeyRepositoryProtocol] = None
) -> FastAPI:
    logger = PravphaLoggingManager.get_logger()
    logger.info(f"Creating FastAPI application: {title}")
    
    # Use default cache config if not provided
    if cache_config is None:
        cache_config = CachePathConfig.default()
        logger.debug("Using default cache path: .Pravaha")
    else:
        logger.info(f"Using custom cache root: {cache_config.cache_root}")
    
    # Use default auth config if not provided
    if auth_config is None:
        auth_config = AuthConfig.default()
    
    app = FastAPI(title=title)
    logger.debug("FastAPI instance created")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.debug("CORS middleware configured")

    # Add authentication middleware if enabled
    if auth_config.enabled:
        # Use provided repository or create default JSON repository
        if access_key_repository is None:
            access_key_repository = JsonAccessKeyRepository(cache_config=cache_config)
        
        app.add_middleware(
            APIKeyMiddleware,
            repository=access_key_repository,
            exempt_paths=auth_config.exempt_paths
        )
        logger.info("API authentication enabled")
    else:
        logger.warning("API authentication DISABLED")

    # Initialize Class-Based Providers
    bot_provider = BotAPIProvider(bot_manager, task_config)
    logger.debug("Bot provider initialized")
    
    # Initialize Storage Components
    # We rely on defaults or can pass config path if needed
    from pravaha.domain.storage.manager.llm_config_manager import LLMConfigManager
    from pravaha.domain.storage.logic.path_resolver import StoragePathResolver
    from pravaha.domain.storage.logic.version_resolver import ArtifactVersionResolver
    
    llm_config_manager = LLMConfigManager(
        Path(llm_config_path) if llm_config_path else None,
        cache_config=cache_config
    )
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
    workflow_manager = LocalWorkflowManager(
        defaults=workflow_defaults,
        cache_config=cache_config
    )
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

    # Authentication Provider (if auth enabled)
    if auth_config.enabled and access_key_repository:
        auth_provider = AuthAPIProvider(access_key_repository)
        app.include_router(auth_provider.router, prefix=f"/{prefix}/auth")
        logger.debug("Auth provider initialized and mounted")

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