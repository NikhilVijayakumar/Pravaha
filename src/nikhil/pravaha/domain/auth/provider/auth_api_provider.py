"""
Authentication API Provider

API endpoints for managing access keys and discovering features.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

from pravaha.domain.auth.protocol.access_key_repository_protocol import AccessKeyRepositoryProtocol
from pravaha.domain.auth.model.module import PravahaModule
from pravaha.domain.logging.manager.logging_manager import PravahaLoggingManager


# Request/Response Models
class CreateKeyRequest(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str]  # Module names as strings


class KeyResponse(BaseModel):
    id: str
    name: str
    key: Optional[str] = None  # Only populated on creation
    created_at: str
    last_used: Optional[str]
    is_active: bool
    description: Optional[str]
    permissions: List[str]


class KeyCapabilitiesResponse(BaseModel):
    """Response showing what features are available for current key."""
    key_id: str
    key_name: str
    available_modules: List[str]
    endpoints: Dict[str, List[str]]  # module -> list of available endpoints


class FeatureInfo(BaseModel):
    description: str
    endpoints: List[str]


class AuthAPIProvider:
    """
    API endpoints for access key management and feature discovery.
    
    Note: These endpoints themselves require authentication.
    """
    
    def __init__(self, repository: AccessKeyRepositoryProtocol):
        self.repository = repository
        self.logger = PravahaLoggingManager.get_logger()
        self.router = APIRouter(tags=["Authentication"])
        
        # Module-to-endpoints mapping
        self.module_endpoints = {
            "bot": ["/api/bot/run/utility", "/api/bot/run/crew"],
            "llm": ["/api/llm/config"],
            "storage": [
                "/api/storage/browse/output",
                "/api/storage/browse/intermediate",
                "/api/storage/browse/knowledge",
                "/api/storage/read/output",
                "/api/storage/read/intermediate",
                "/api/storage/read/knowledge",
                "/api/storage/config"
            ],
            "workflow": [
                "/api/workflow/list",
                "/api/workflow/create",
                "/api/workflow/run",
                "/api/workflow/rename",
                "/api/workflow/delete"
            ]
        }
        
        #Define routes
        self._define_routes()
    
    def _define_routes(self):
        """Define all authentication API routes."""
        
        @self.router.post("/keys", response_model=KeyResponse)
        async def create_key(request: CreateKeyRequest):
            """Create a new API access key with specified permissions."""
            try:
                # Parse permissions
                permissions = [PravahaModule.from_string(p) for p in request.permissions]
                
                # Create key
                key = self.repository.create_key(
                    name=request.name,
                    description=request.description,
                    permissions=permissions
                )
                
                self.logger.info(f"Created new API key: {key.name} (ID: {key.id})")
                
                return KeyResponse(
                    id=key.id,
                    name=key.name,
                    key=key.key,  # Raw key shown only once!
                    created_at=key.created_at.isoformat(),
                    last_used=None,
                    is_active=True,
                    description=key.description,
                    permissions=[p.value for p in key.permissions]
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.router.get("/keys", response_model=List[KeyResponse])
        async def list_keys(include_inactive: bool = False):
            """List all API keys (key values are masked)."""
            keys = self.repository.list_keys(include_inactive=include_inactive)
            
            return [
                KeyResponse(
                    id=k.id,
                    name=k.name,
                    key=None,  # Never expose in list
                    created_at=k.created_at.isoformat(),
                    last_used=k.last_used.isoformat() if k.last_used else None,
                    is_active=k.is_active,
                    description=k.description,
                    permissions=[p.value for p in k.permissions]
                )
                for k in keys
            ]
        
        @self.router.delete("/keys/{key_id}")
        async def revoke_key(key_id: str):
            """Revoke an API key."""
            self.repository.revoke_key(key_id)
            self.logger.info(f"Revoked API key: {key_id}")
            return {"message": "Key revoked successfully", "key_id": key_id}
        
        @self.router.get("/capabilities", response_model=KeyCapabilitiesResponse)
        async def get_capabilities(request: Request):
            """Get available features for current API key."""
            # Access key attached by middleware
            access_key = request.state.access_key
            
            # Build endpoint list per module
            endpoints = {}
            for module in access_key.permissions:
                endpoints[module.value] = self.module_endpoints.get(module.value, [])
            
            return KeyCapabilitiesResponse(
                key_id=access_key.id,
                key_name=access_key.name,
                available_modules=[p.value for p in access_key.permissions],
                endpoints=endpoints
            )
        
        @self.router.get("/features", response_model=Dict[str, FeatureInfo])
        async def list_all_features():
            """List all available modules and their features (public endpoint)."""
            return {
                "bot": FeatureInfo(
                    description="Bot execution and task management",
                    endpoints=self.module_endpoints["bot"]
                ),
                "llm": FeatureInfo(
                    description="LLM configuration management",
                    endpoints=self.module_endpoints["llm"]
                ),
                "storage": FeatureInfo(
                    description="Artifact storage and retrieval",
                    endpoints=self.module_endpoints["storage"]
                ),
                "workflow": FeatureInfo(
                    description="Workflow definition and execution",
                    endpoints=self.module_endpoints["workflow"]
                )
            }
