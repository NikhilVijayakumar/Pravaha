from pydantic import BaseModel


class StorageConfigRequest(BaseModel):
    output_path: str
    intermediate_path: str
    knowledge_path: str