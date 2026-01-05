from typing import TypedDict, Literal, Optional

class ArtifactMetadata(TypedDict):
    feature: str
    product: Optional[str]
    model: str
    version: int
    stage: Literal["intermediate", "final"]
    path: str
    created_at: str
    display_name: Optional[str]
