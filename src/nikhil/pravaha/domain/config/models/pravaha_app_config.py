"""
Pravaha Application Configuration

Root composite configuration model for the Pravaha application.
Mirrors Nibandha's AppConfig pattern with composable sub-configs
and model_validator for cross-field path resolution.
"""

from pathlib import Path
from typing import Optional
import tomli
from pydantic import BaseModel, Field, model_validator

from pravaha.domain.config.models.llm_config import LLMConfig
from pravaha.domain.config.models.storage_config import StorageConfig
from pravaha.domain.config.models.workflow_config import WorkflowConfig
from pravaha.domain.auth.config.auth_config import AuthConfig
from pravaha.domain.config.cache_config import CachePathConfig


def _read_project_name_from_pyproject() -> str:
    """Read project name from pyproject.toml, fallback to 'Pravaha'."""
    try:
        pyproject_path = Path.cwd() / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomli.load(f)
                return data.get("project", {}).get("name", "Pravaha")
    except Exception:
        pass
    return "Pravaha"


class PravahaAppConfig(BaseModel):
    """
    Main Application Configuration for Pravaha.

    All fields are optional with sensible defaults.
    Sub-configs are composable and independently configurable.
    """

    # Core identity
    name: str = Field(
        default_factory=_read_project_name_from_pyproject,
        description="Application Name",
    )
    mode: str = Field(
        default="production",
        description="Operating Mode (development/production)",
    )

    # Sub-configs — all optional with defaults
    llm: Optional[LLMConfig] = Field(
        None, description="LLM Configuration (loaded separately if not embedded)"
    )
    storage: StorageConfig = Field(
        default_factory=StorageConfig, description="Storage Configuration"
    )
    workflow: WorkflowConfig = Field(
        default_factory=WorkflowConfig, description="Workflow Configuration"
    )
    auth: AuthConfig = Field(
        default_factory=AuthConfig, description="Authentication Configuration"
    )
    cache: CachePathConfig = Field(
        default_factory=CachePathConfig, description="Cache Path Configuration"
    )

    # Nibandha integration
    logging_level: str = Field(
        "INFO", description="Log level for Nibandha logging"
    )

    @model_validator(mode='after')
    def resolve_paths(self) -> 'PravahaAppConfig':
        """
        Resolve default paths based on app name and cache root.
        Ensures storage, workflow, and cache paths are consistent.
        """
        cache_root = self.cache.cache_root

        # Resolve storage paths relative to cache root if they are defaults
        if self.storage.output == "output":
            self.storage.output = str(cache_root / "output")
        if self.storage.intermediate == "intermediate":
            self.storage.intermediate = str(cache_root / "intermediate")
        if self.storage.knowledge == "knowledge":
            self.storage.knowledge = str(cache_root / "knowledge")

        # Resolve workflow paths relative to cache root if they are defaults
        if self.workflow.details_path == "workflow/details":
            self.workflow.details_path = str(cache_root / "workflow" / "details")
        if self.workflow.run_path == "workflow/run":
            self.workflow.run_path = str(cache_root / "workflow" / "run")

        return self
