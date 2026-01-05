from typing import Protocol, Optional
from enum import Enum
from pathlib import Path

class StorageStage(Enum):
    INTERMEDIATE = "intermediate"
    FINAL = "final"

class ArtifactVersionResolverProtocol(Protocol):
    def get_latest_version(
        self,
        stage: StorageStage,
        feature: str,
        product: Optional[str],
        model_alias: str
    ) -> Optional[int]:
        ...

    def get_next_version(
        self,
        stage: StorageStage,
        feature: str,
        product: Optional[str],
        model_alias: str
    ) -> int:
        ...

class StoragePathResolverProtocol(Protocol):
    def resolve_output_path(
        self,
        stage: StorageStage,
        feature: str,
        product: Optional[str],
        model_key: str
    ) -> Path:
        """
        Returns deterministic path for the NEXT version.
        """
        ...
