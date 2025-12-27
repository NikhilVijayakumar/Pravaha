# src.nikhil.pravaha.domain.storage.manager.local_storage_manager.py
import json
from pathlib import Path

from fastapi import HTTPException


class LocalStorageManager:
    def __init__(self, config_file: str = "storage_config.json"):

        self.project_root = Path(__file__).parent.parent.parent.parent.resolve()
        self.config_file = Path(config_file)
        self._ensure_defaults()

    def _ensure_defaults(self):
        """Sets up default paths relative to project root if no config exists."""
        if not self.config_file.exists():
            defaults = {
                "output": str(self.project_root / ".Amsha" / "output" / "final" / "output"),
                "intermediate": str(self.project_root / ".Amsha" / "output" / "intermediate" / "output"),
                "knowledge": str(self.project_root / "data" / "knowledge")
            }

            for path_str in defaults.values():
                Path(path_str).mkdir(parents=True, exist_ok=True)

            self._save_config(defaults)

    def _save_config(self, data: dict):
        with open(self.config_file, "w") as f:
            json.dump(data, f, indent=4)

    def update_config(self, output: str, intermediate: str, knowledge: str):
        """Allows API to override defaults with absolute or other relative paths."""

        config = {
            "output": str(Path(output).resolve()),
            "intermediate": str(Path(intermediate).resolve()),
            "knowledge": str(Path(knowledge).resolve())
        }
        self._save_config(config)

    def get_path(self, category: str) -> Path:
        with open(self.config_file, "r") as f:
            config = json.load(f)

        path_str = config.get(category)
        if not path_str:
            raise HTTPException(status_code=400, detail=f"Category {category} missing.")

        path = Path(path_str)
        if not path.exists():
            # Help the user by showing exactly where it's looking
            raise HTTPException(
                status_code=500,
                detail=f"Path for {category} not found at: {path.absolute()}"
            )
        return path
