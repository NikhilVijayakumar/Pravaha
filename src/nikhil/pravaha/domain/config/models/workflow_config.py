"""
Workflow Configuration Model

Pydantic-based configuration for Pravaha workflow paths.
"""

from pydantic import BaseModel, Field


class WorkflowConfig(BaseModel):
    """Configuration for workflow directory paths."""
    details_path: str = Field("workflow/details", description="Workflow details directory")
    run_path: str = Field("workflow/run", description="Workflow run directory")
