"""
LLM Config Repository Protocol

Protocol for LLM configuration persistence.
"""

from typing import Protocol, Dict, Any


class LLMConfigRepositoryProtocol(Protocol):
    """
    Protocol for LLM configuration persistence.
    
    Implementations can use JSON, PostgreSQL, MongoDB, etc.
    """
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get complete LLM configuration.
        
        Returns:
            Full LLM configuration dictionary
        """
        ...
    
    def resolve_output_config(self, model_key: str) -> Dict[str, Any]:
        """
        Resolve output configuration for a specific model.
        
        Args:
            model_key: Model identifier
            
        Returns:
            Output configuration for the model
        """
        ...
