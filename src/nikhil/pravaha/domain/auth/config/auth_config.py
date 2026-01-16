"""
Authentication Configuration

Controls authentication behavior and exempt paths.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class AuthConfig:
    """
    Authentication configuration for Pravaha API.
    
    Controls whether API authentication is enabled and which paths are exempt.
    """
    
    enabled: bool = True
    """Whether authentication is enabled."""
    
    exempt_paths: List[str] = field(default_factory=lambda: [
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/auth/features"
    ])
    """Paths that don't require authentication."""
    
    @staticmethod
    def default() -> 'AuthConfig':
        """
        Create default configuration (auth enabled).
        
        Returns:
            AuthConfig with authentication enabled
        """
        return AuthConfig(enabled=True)
    
    @staticmethod
    def disabled() -> 'AuthConfig':
        """
        Create configuration with auth disabled.  
        
        Useful for local development.
        
        Returns:
            AuthConfig with authentication disabled
        """
        return AuthConfig(enabled=False)
