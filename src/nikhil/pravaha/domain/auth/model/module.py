"""
Pravaha Module Enumeration

Defines the available modules for permission control.
"""

from enum import Enum
from typing import List


class PravahaModule(str, Enum):
    """
    Available modules in Pravaha that can be controlled via API access permissions.
    
    Each module represents a distinct feature area with its own API endpoints.
    """
    
    BOT = "bot"           # Bot execution and task management
    LLM = "llm"           # LLM configuration management
    STORAGE = "storage"   # Artifact storage and retrieval
    WORKFLOW = "workflow" # Workflow definition and execution
    
    @staticmethod
    def all_modules() -> List['PravahaModule']:
        """
        Get all available modules.
        
        Returns:
            List of all PravahaModule enum values
        """
        return [
            PravahaModule.BOT,
            PravahaModule.LLM,
            PravahaModule.STORAGE,
            PravahaModule.WORKFLOW
        ]
    
    @staticmethod
    def from_string(value: str) -> 'PravahaModule':
        """
        Parse module from string value.
        
        Args:
            value: Module name as string (case-insensitive)
            
        Returns:
            PravahaModule enum value
            
        Raises:
            ValueError: If value is not a valid module name
        """
        value_lower = value.lower()
        
        for module in PravahaModule:
            if module.value == value_lower:
                return module
        
        raise ValueError(f"Invalid module: {value}. Valid modules: {[m.value for m in PravahaModule.all_modules()]}")
