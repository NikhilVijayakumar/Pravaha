"""
LLM Config Manager Protocol

Protocol for LLM configuration management.
"""

from typing import Protocol, Dict, Any

class LLMConfigManagerProtocol(Protocol):
    """
    Protocol for LLM Configuration Manager.
    
    Responsible for:
    - Loading/Saving configuration
    - Resolving model-specific output settings
    """
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get complete LLM configuration using the storage system.
        
        Returns:
            Full LLM configuration dictionary
        """
        ...
        
    def resolve_output_config(self, model_key: str) -> Dict[str, Any]:
        """
        Resolve output configuration for a specific model context.
        
        Args:
            model_key: Model identifier or alias
            
        Returns:
            Output configuration for the model (e.g., display_name)
        """
        ...
