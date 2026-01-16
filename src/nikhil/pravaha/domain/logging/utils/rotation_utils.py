"""
Log Rotation Utilities

Provides utility functions for log rotation management.
These are meant to be used by client applications, not by Pravaha itself.
"""

from nibandha import Nibandha, LogRotationConfig
from pathlib import Path
from typing import Optional
import yaml


class LogRotationUtils:
    """
    Utilities for log rotation - to be used by client applications.
    
    Pravaha is a library and does not automatically trigger log rotation.
    Client applications should use these utilities to manage rotation on their schedule.
    """
    
    @staticmethod
    def setup_rotation(
        max_size_mb: int = 50,
        rotation_interval_hours: int = 24,
        archive_retention_days: int = 30,
        config_path: Optional[Path] = None
    ) -> None:
        """
        Create log rotation configuration file for Nibandha.
        Client applications should call this at startup.
        
        Default configuration (production-ready):
        - Max log size: 50MB
        - Rotation interval: 24 hours
        - Archive retention: 30 days
        
        Args:
            max_size_mb: Maximum log file size in MB before rotation
            rotation_interval_hours: Time interval in hours for rotation
            archive_retention_days: Days to retain archived logs
            config_path: Optional custom path for config file
        """
        if config_path is None:
            config_path = Path(".Nibandha/config/rotation_config.yaml")
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = LogRotationConfig(
            enabled=True,
            max_size_mb=max_size_mb,
            rotation_interval_hours=rotation_interval_hours,
            archive_retention_days=archive_retention_days
        )
        
        with open(config_path, 'w') as f:
            yaml.dump(config.model_dump(), f, default_flow_style=False)
    
    @staticmethod
    def check_and_rotate(nb: Nibandha) -> bool:
        """
        Check if rotation is needed and perform it.
        
        Args:
            nb: Nibandha instance
            
        Returns:
            True if rotation was performed, False otherwise
        """
        if nb.should_rotate():
            nb.rotate_logs()
            return True
        return False
    
    @staticmethod
    def cleanup_old_logs(nb: Nibandha) -> int:
        """
        Clean up old archived logs based on retention policy.
        
        Args:
            nb: Nibandha instance
            
        Returns:
            Count of deleted archive files
        """
        return nb.cleanup_old_archives()
