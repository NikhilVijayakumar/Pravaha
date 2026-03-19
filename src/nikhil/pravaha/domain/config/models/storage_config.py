"""
Storage Configuration Model

Pydantic-based configuration for Pravaha storage paths.
"""

from pydantic import BaseModel, Field


class StorageConfig(BaseModel):
    """Configuration for storage directory paths."""
    output: str = Field("output", description="Output directory path")
    intermediate: str = Field("intermediate", description="Intermediate files path")
    knowledge: str = Field("knowledge", description="Knowledge base path")
