"""
Pravaha Configuration Manager

Manages loading and validation of Pravaha Application Configuration.
Provides smart defaults — modules receive fully configured objects.
Mirrors Nibandha's ConfigurationManager pattern.
"""

from pathlib import Path
from typing import Union, Dict, Any, Optional
import json
import yaml
from pydantic import ValidationError
import logging

from pravaha.domain.config.models.pravaha_app_config import PravahaAppConfig

logger = logging.getLogger(__name__)


class PravahaConfigurationManager:
    """
    Manages loading and validation of Application Configuration.
    Provides smart defaults — modules receive fully configured objects.
    """

    @staticmethod
    def load_from_dict(data: Dict[str, Any]) -> PravahaAppConfig:
        """
        Load configuration from a dictionary.
        Uses PravahaRobustConfigValidator for validation and sanitization.
        Falls back to default configuration on critical errors.

        Args:
            data: Configuration dictionary (can be partial).

        Returns:
            PravahaAppConfig: Validated application configuration with defaults.
        """
        try:
            from pravaha.domain.config.infrastructure.robust_validator import (
                PravahaRobustConfigValidator,
            )

            validator = PravahaRobustConfigValidator()
            clean_data = validator.validate_and_sanitize(
                PravahaAppConfig, data or {}
            )

            # Log audit trail
            for log_entry in validator.audit_log:
                logger.debug(log_entry)

            return PravahaAppConfig(**clean_data)

        except (ValidationError, ValueError, TypeError) as e:
            logger.error(
                f"❌ Configuration Validation Failed: "
                f"{type(e).__name__}: {str(e)}"
            )
            logger.warning(
                "⚠️  Application starting with DEFAULT configuration "
                "due to validation failure."
            )
            return PravahaConfigurationManager.create_default()

    @staticmethod
    def load_from_json(path: Union[str, Path]) -> PravahaAppConfig:
        """
        Load configuration from a JSON file.

        Args:
            path: Path to JSON file.

        Returns:
            PravahaAppConfig: Validated application configuration.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return PravahaConfigurationManager.load_from_dict(data)

    @staticmethod
    def load_from_yaml(path: Union[str, Path]) -> PravahaAppConfig:
        """
        Load configuration from a YAML file.

        Args:
            path: Path to YAML file.

        Returns:
            PravahaAppConfig: Validated application configuration.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return PravahaConfigurationManager.load_from_dict(data)

    @staticmethod
    def create_default(
        app_name: Optional[str] = None,
    ) -> PravahaAppConfig:
        """
        Create a default configuration.

        Args:
            app_name: Optional app name override.

        Returns:
            PravahaAppConfig with all defaults.
        """
        if app_name:
            return PravahaAppConfig(name=app_name)
        return PravahaAppConfig()
