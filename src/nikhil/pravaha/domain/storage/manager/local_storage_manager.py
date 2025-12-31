import os
import json
from pathlib import Path

from fastapi import HTTPException


class LocalStorageManager:
    def __init__(self):
        self.project_root = Path(os.getcwd())
        
        # Strict config path: .Pravaha/config/storage.json
        self.config_dir = self.project_root / ".Pravaha" / "config"
        self.config_file = self.config_dir / "storage.json"
        
        self._ensure_defaults()

    def _ensure_defaults(self):
        """Sets up default paths relative to project root if no config exists."""
        if not self.config_file.exists():
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)

            defaults = {
                "output": "output",
                "intermediate": "intermediate",
                "knowledge": "knowledge"
            }

            for path_str in defaults.values():
                (self.project_root / path_str).mkdir(parents=True, exist_ok=True)

            self._save_config(defaults)

    def _save_config(self, data: dict):
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=4)

    def update_config(self, output: str, intermediate: str, knowledge: str):
        """Allows API to override defaults with absolute or other relative paths."""

        config = {
            "output": str(Path(output)),
            "intermediate": str(Path(intermediate)),
            "knowledge": str(Path(knowledge))
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
            # Help the user by showing exactly where it's looking
            raise HTTPException(
                status_code=500,
                detail=f"Path for {category} not found at: {path.absolute()}"
            )
        return path

    def get_config(self) -> dict:
        """Returns the full current configuration."""
        if not self.config_file.exists():
            # Should normally not happen due to _ensure_defaults
            return {}
            
        with open(self.config_file, "r") as f:
            return json.load(f)
