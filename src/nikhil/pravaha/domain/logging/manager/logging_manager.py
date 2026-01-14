"""
Pravaha Logging Manager

Provides a singleton wrapper around Nibandha for centralized logging in Pravaha.
"""

from nibandha import Nibandha, AppConfig
from typing import Optional


class PravphaLoggingManager:
    """
    Manages Nibandha integration for Pravaha library.
    
    Uses singleton pattern to ensure Nibandha is initialized once per application runtime.
    """
    
    _instance: Optional[Nibandha] = None
    
    @classmethod
    def initialize(cls, log_level: str = "INFO") -> Nibandha:
        """
        Initialize Nibandha for Pravaha (singleton pattern).
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            Nibandha instance
        """
        if cls._instance is None:
            config = AppConfig(
                name="Pravaha",
                custom_folders=[
                    "workflow/details",
                    "workflow/run",
                    "config"
                ],
                log_level=log_level
            )
            cls._instance = Nibandha(config).bind()
        return cls._instance
    
    @classmethod
    def get_logger(cls):
        """
        Get the Nibandha logger instance.
        
        Automatically initializes if not already done.
        
        Returns:
            Logger instance from Nibandha
        """
        if cls._instance is None:
            cls.initialize()
        return cls._instance.logger
    
    @classmethod
    def get_instance(cls) -> Optional[Nibandha]:
        """
        Get the Nibandha instance without auto-initialization.
        
        Returns:
            Nibandha instance or None if not initialized
        """
        return cls._instance
