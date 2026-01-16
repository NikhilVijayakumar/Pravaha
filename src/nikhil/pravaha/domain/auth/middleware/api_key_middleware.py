"""
API Key Authentication Middleware

FastAPI middleware for validating API keys with module-based permissions.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette import status
from typing import Optional, Dict

from pravaha.domain.auth.protocol.access_key_repository_protocol import AccessKeyRepositoryProtocol
from pravaha.domain.auth.model.module import PravahaModule
from pravaha.domain.logging.manager.logging_manager import PravahaLoggingManager


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key validation with module-based permissions.
    
    Validates X-API-Key header and checks module permissions based on request path.
    """
    
    def __init__(
        self, 
        app,
        repository: AccessKeyRepositoryProtocol,
        exempt_paths: Optional[list[str]] = None,
        module_path_mapping: Optional[Dict[str, PravahaModule]] = None
    ):
        """
        Initialize middleware.
        
        Args:
            app: FastAPI application
            repository: Access key repository
            exempt_paths: Paths that don't require authentication
            module_path_mapping: Mapping of path prefixes to required modules
        """
        super().__init__(app)
        self.repository = repository
        self.logger = PravahaLoggingManager.get_logger()
        
        # Default exempt paths
        self.exempt_paths = exempt_paths or [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc"
        ]
        
        # Map path prefixes to modules
        self.module_path_mapping = module_path_mapping or {
            "/api/bot": PravahaModule.BOT,
            "/api/llm": PravahaModule.LLM,
            "/api/storage": PravahaModule.STORAGE,
            "/api/workflow": PravahaModule.WORKFLOW,
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request and validate API key with permissions."""
        
        # Check if path is exempt
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
       # Get API key from header
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            self.logger.warning(f"Request to {request.url.path} without API key")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "API key required. Include X-API-Key header."}
            )
        
        # Validate key and get access key object
        access_key = self.repository.get_key_by_value(api_key)
        
        if not access_key or not access_key.is_active:
            self.logger.warning(f"Invalid API key attempt for {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Invalid or inactive API key"}
            )
        
        # Check module permission
        required_module = self._get_required_module(request.url.path)
        
        if required_module and not access_key.has_permission(required_module):
            self.logger.warning(
                f"Permission denied for {access_key.name} to access {request.url.path} "
                f"(requires {required_module.value})"
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": f"Access denied. Key does not have '{required_module.value}' permission",
                    "required_permission": required_module.value,
                    "available_permissions": [p.value for p in access_key.permissions]
                }
            )
        
        # Update last used timestamp
        self.repository.update_last_used(access_key.id)
        
        # Attach access key to request state for use in endpoints
        request.state.access_key = access_key
        
        self.logger.debug(
            f"Authenticated request from {access_key.name} to {request.url.path}"
        )
        
        return await call_next(request)
    
    def _get_required_module(self, path: str) -> Optional[PravahaModule]:
        """
        Determine which module permission is required for a path.
        
        Args:
            path: Request path
            
        Returns:
            Required PravahaModule or None if no specific module required
        """
        for prefix, module in self.module_path_mapping.items():
            if path.startswith(prefix):
                return module
        return None
