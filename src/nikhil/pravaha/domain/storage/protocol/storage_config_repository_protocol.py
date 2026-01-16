"""
Storage Config Repository Protocol

Protocol for storage configuration persistence.
"""

from typing import Protocol, Dict


class StorageConfigRepositoryProtocol(Protocol):
    """
    Protocol for storage configuration persistence.
    
    Implementations can use JSON, PostgreSQL, MongoDB, etc.
    """
    
    def get_config(self) -> Dict[str, str]:
        """
        Get storage paths configuration.
        
        Returns:
            Dictionary mapping category to path
            Example: {"output": "output", "intermediate": "intermediate", "knowledge": "knowledge"}
        """
        ...
    
    def update_config(self, config: Dict[str, str]) -> None:
        """
        Update storage configuration.
        
        Args:
            config: Dictionary mapping category to path
        """
        ...
    
    def get_path(self, category: str) -> str:
        """
        Get specific storage path by category.
        
        Args:
            category: Storage category (output, intermediate, knowledge)
            
        Returns:
            Path for the category
        """
        ...
