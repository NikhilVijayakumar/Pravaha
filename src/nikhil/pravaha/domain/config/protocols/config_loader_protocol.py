"""
Configuration Loader Protocol

Protocol for loading Pravaha application configuration.
"""

from typing import Protocol, runtime_checkable
from pravaha.domain.config.models.pravaha_app_config import PravahaAppConfig


@runtime_checkable
class PravahaConfigLoaderProtocol(Protocol):
    """Protocol for loading application configuration."""

    def load(self) -> PravahaAppConfig:
        """Load and return the PravahaAppConfig."""
        ...
