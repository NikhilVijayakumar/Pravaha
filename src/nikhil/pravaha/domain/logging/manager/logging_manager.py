"""
Pravaha Logging Manager

Provides a singleton wrapper around Nibandha for centralized logging in Pravaha.
"""

from nibandha import Nibandha, AppConfig
from typing import Optional
from pathlib import Path


class PravahaLoggingManager:
    """
    Manages Nibandha integration for Pravaha library.
    
    Uses singleton pattern to ensure Nibandha is initialized once per application runtime.
    """
    
    _instance: Optional[Nibandha] = None
    
    @classmethod
    def _ensure_rotation_config(cls) -> None:
        """
        Ensure rotation config exists to prevent interactive prompts.
        
        CRITICAL: Nibandha prompts for user input during bind() if no rotation
        config exists. This is unacceptable for backend libraries that may run
        in non-interactive environments (APIs, containers, CI/CD, etc.).
        
        This method creates a default config file if it doesn't exist, preventing
        any interactive prompts during Nibandha initialization.
        """
        from pravaha.domain.logging.utils.rotation_utils import LogRotationUtils
        
        config_path = Path(".Nibandha/config/rotation_config.yaml")
        
        if not config_path.exists():
            # Create default rotation config to prevent interactive prompts
            LogRotationUtils.setup_rotation()
    
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
            # CRITICAL: Ensure rotation config exists BEFORE Nibandha initialization
            # to prevent interactive prompts in backend environments
            cls._ensure_rotation_config()
            
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


# Backwards compatibility alias for typo used throughout codebase
PravphaLoggingManager = PravahaLoggingManager
