from typing import Protocol, TypedDict, Literal, NotRequired, Dict, Any

class LLMOutputConfig(TypedDict):
    alias: str
    structure: Literal["flat", "folder"]
    folder_name: NotRequired[str]
    display_name: NotRequired[str]

class LLMConfigManagerProtocol(Protocol):
    def resolve_output_config(self, model_key: str) -> LLMOutputConfig:
        """
        Resolves output configuration for a model.
        """
        ...

    def get_all_config(self) -> Dict[str, Any]:
        """
        Returns the complete configuration dictionary.
        """
        ...
