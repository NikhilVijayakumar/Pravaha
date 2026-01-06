from typing import Optional

from fastapi import APIRouter
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from pravaha.domain.storage.model.storage_config_request import StorageConfigRequest
from pravaha.domain.storage.protocol.artifact_resolver_protocol import ArtifactVersionResolverProtocol
from pravaha.domain.storage.protocol.artifact_resolver_protocol import StoragePathResolverProtocol
from pravaha.domain.storage.protocol.llm_config_protocol import LLMConfigManagerProtocol
from pravaha.domain.storage.provider.intermediate_storage_provider import IntermediateStorageProvider
from pravaha.domain.storage.provider.knowledge_storage_provider import KnowledgeStorageProvider
from pravaha.domain.storage.provider.output_storage_provider import OutputStorageProvider


class StorageAPIProvider:
    """
    Main Storage API Provider - Coordinator for all storage categories.
    
    Responsibilities:
    - Route registration
    - Delegation to specialized providers
    - Configuration management
    
    Delegates actual browse/read logic to:
    - KnowledgeStorageProvider: Simple file listing
    - IntermediateStorageProvider: Feature + timestamp versioning
    - OutputStorageProvider: Product/Feature + suffix versioning
    """

    def __init__(
        self,
        storage_manager: LocalStorageManager,
        llm_config_manager: LLMConfigManagerProtocol,
        path_resolver: StoragePathResolverProtocol,
        version_resolver: ArtifactVersionResolverProtocol,
    ):
        self.storage_manager = storage_manager
        self.llm_config = llm_config_manager
        self.path_resolver = path_resolver
        self.version_resolver = version_resolver

        # Initialize specialized providers
        self.knowledge_provider = KnowledgeStorageProvider(storage_manager)
        self.intermediate_provider = IntermediateStorageProvider(
            storage_manager, llm_config_manager
        )
        self.output_provider = OutputStorageProvider(
            storage_manager, llm_config_manager
        )

        # Map categories to providers
        self.providers = {
            "knowledge": self.knowledge_provider,
            "intermediate": self.intermediate_provider,
            "output": self.output_provider,
        }

        self.router = APIRouter(prefix="/storage")
        self._setup_routes()

    def _setup_routes(self):
        """Register all storage API routes."""
        # Configuration routes
        self.router.post("/config")(self.set_storage_config)
        self.router.get("/config")(self.get_storage_config)
        self.router.get("/schema/config")(self.get_config_schema)

        # Browse and read routes for each category
        for category in ["intermediate", "output", "knowledge"]:
            self.router.get(f"/{category}/browse")(
                self._create_browse_handler(category)
            )
            self.router.get(f"/{category}/read")(self._create_read_handler(category))

    def _create_browse_handler(self, category: str):
        """Create browse handler that delegates to the appropriate provider."""

        async def handler(
            feature: Optional[str] = None,
            product: Optional[str] = None,
            model: Optional[str] = None,
            path: Optional[str] = None,
        ):
            provider = self.providers[category]
            
            # Knowledge category uses 'path' parameter, others use feature/product/model
            if category == "knowledge":
                return await provider.browse(path=path)
            else:
                return await provider.browse(
                    feature=feature, product=product, model=model
                )

        return handler

    def _create_read_handler(self, category: str):
        """Create read handler that delegates to the appropriate provider."""

        async def handler(path: str):
            provider = self.providers[category]
            return await provider.read(path)

        return handler

    # ---------------------------------------------------------------------
    # CONFIGURATION
    # ---------------------------------------------------------------------

    async def set_storage_config(self, req: StorageConfigRequest):
        """Update storage configuration."""
        self.storage_manager.update_config(
            req.output_path, req.intermediate_path, req.knowledge_path
        )
        return {"status": "Configured successfully"}

    async def get_storage_config(self):
        """Get current storage configuration."""
        return self.storage_manager.get_config()

    async def get_config_schema(self):
        """Get storage configuration JSON schema."""
        return StorageConfigRequest.model_json_schema()