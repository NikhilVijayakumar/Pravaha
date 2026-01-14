import os
import json
import shutil
from pathlib import Path
from typing import Optional

from fastapi import HTTPException
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager


class LocalWorkflowManager:
    def __init__(self, defaults: Optional[dict[str, str]] = None, config_path: Optional[Path] = None):
        self.project_root = Path(os.getcwd())
        
        # Strict config path: .Pravaha/config/workflow.json
        self.config_dir = self.project_root / ".Pravaha" / "config"
        self.config_file = self.config_dir / "workflow.json"
        
        # Caching Logic
        if config_path and config_path.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(config_path, self.config_file)
            except Exception as e:
                # Log warning using Nibandha logger
                logger = PravphaLoggingManager.get_logger()
                logger.warning(f"Failed to cache Workflow config from {config_path}: {e}")

        if defaults:
            self.defaults = defaults
        else:
            self.defaults = {
                "details": ".Pravaha/workflow/details",
                "run": ".Pravaha/workflow/run"
            }
        
        self._ensure_defaults()

    def _ensure_defaults(self):
        """Sets up default paths relative to project root if no config exists."""
        if not self.config_file.exists():
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)

            for path_str in self.defaults.values():
                (self.project_root / path_str).mkdir(parents=True, exist_ok=True)

            self._save_config(self.defaults)

    def _save_config(self, data: dict):
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=4)

    def update_config(self, details: str, run: str):
        """Allows API to override defaults with absolute or other relative paths."""

        config = {
            "details": str(Path(details)),
            "run": str(Path(run))
        }
        self._save_config(config)

    def get_path(self, category: str) -> Path:
        with open(self.config_file, "r") as f:
            config = json.load(f)

        path_str = config.get(category)
        if not path_str:
            raise HTTPException(status_code=400, detail=f"Category {category} missing.")

        path = Path(path_str)
        if not path.is_absolute():
            path = (self.project_root / path).resolve()
            
        if not path.exists():
            # Create the directory if it doesn't exist
            path.mkdir(parents=True, exist_ok=True)
            
        return path

    def get_config(self) -> dict:
        """Returns the full current configuration."""
        if not self.config_file.exists():
            # Should normally not happen due to _ensure_defaults
            return {}
            
        with open(self.config_file, "r") as f:
            return json.load(f)
    
    def is_configured(self) -> bool:
        """Check if workflow configuration exists."""
        return self.config_file.exists()
