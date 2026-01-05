from typing import TypedDict, Literal, Optional, List

class ArtifactVersion(TypedDict):
    version: int
    path: str
    created_at: str

class GroupedArtifactMetadata(TypedDict):
    feature: str
    product: Optional[str]
    model: str
    stage: Literal["intermediate", "final"]
    display_name: Optional[str]
    latest_version: int
    versions: List[ArtifactVersion]

class ArtifactMetadata(TypedDict):
    feature: str
    product: Optional[str]
    model: str
    version: int
    stage: Literal["intermediate", "final"]
    path: str
    created_at: str
    display_name: Optional[str]
