"""
Authentication Configuration

Pydantic-based configuration for authentication behavior and exempt paths.
"""

from typing import List
from pydantic import BaseModel, Field, field_validator


class AuthConfig(BaseModel):
    """
    Authentication configuration for Pravaha API.

    Controls whether API authentication is enabled and which paths are exempt.
    """

    enabled: bool = Field(True, description="Whether authentication is enabled")
    exempt_paths: List[str] = Field(
        default_factory=lambda: [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/api/auth/features",
        ],
        description="Paths that don't require authentication",
    )

    @field_validator('exempt_paths')
    @classmethod
    def validate_exempt_paths(cls, v: List[str]) -> List[str]:
        """Ensure all exempt paths start with '/'."""
        for path in v:
            if not path.startswith('/'):
                raise ValueError(
                    f"Exempt path must start with '/', got: '{path}'"
                )
        return v

    @staticmethod
    def default() -> 'AuthConfig':
        """Create default configuration (auth enabled)."""
        return AuthConfig(enabled=True)

    @staticmethod
    def disabled() -> 'AuthConfig':
        """Create configuration with auth disabled (for local development)."""
        return AuthConfig(enabled=False)
