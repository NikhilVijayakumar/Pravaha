"""
Workflow Config Repository Protocol

Protocol for workflow configuration persistence.
"""

from typing import Protocol, Dict


class WorkflowConfigRepositoryProtocol(Protocol):
    """
    Protocol for workflow configuration persistence.
    
    Implementations can use JSON, PostgreSQL, MongoDB, etc.
    """
    
    def get_config(self) -> Dict[str, str]:
        """
        Get workflow paths configuration.
        
        Returns:
            Dictionary mapping category to path
            Example: {"details": ".Pravaha/workflow/details", "run": ".Pravaha/workflow/run"}
        """
        ...
    
    def update_config(self, config: Dict[str, str]) -> None:
        """
        Update workflow configuration.
        
        Args:
            config: Dictionary mapping category to path
        """
        ...
    
    def get_path(self, category: str) -> str:
        """
        Get specific workflow path by category.
        
        Args:
            category: Workflow category (details, run)
            
        Returns:
            Path for the category
        """
        ...
