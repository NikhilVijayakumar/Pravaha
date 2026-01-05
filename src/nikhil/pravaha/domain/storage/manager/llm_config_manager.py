import shutil
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from pravaha.domain.storage.protocol.llm_config_protocol import LLMConfigManagerProtocol, LLMOutputConfig

class LLMConfigManager(LLMConfigManagerProtocol):
    def __init__(self, config_path: Optional[Path] = None):
        self.project_root = Path.cwd()
        # Internal cache location
        self.config_dir = self.project_root / ".Pravaha" / "config"
        self.config_file = self.config_dir / "llm_config.yaml"
        
        # Caching Logic
        if config_path and config_path.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(config_path, self.config_file)
            except Exception as e:
                print(f"Warning: Failed to cache LLM config from {config_path}: {e}")
        
        # If no path provided, we expect the file to already exist at self.config_file
        # or we might fail gracefully in _load_config
        
        self._config_cache: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        if not self.config_file.exists():
            # If config is missing, we might want to log a warning or use defaults.
            # For now, we'll initialize empty and handle lookups gracefully.
            self._config_cache = {}
            return

        try:
            with open(self.config_file, "r") as f:
                self._config_cache = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading LLM config: {e}")
            self._config_cache = {}

    def resolve_output_config(self, model_key: str) -> LLMOutputConfig:
        """
        Resolves output configuration for a model key.
        Searches recursively for 'models' -> {model_key}.
        """
        # Flat search in the 'llm' block
        # Structure is usually llm -> category -> models -> key
        
        llm_block = self._config_cache.get("llm", {})
        
        # We need to find the model_key anywhere in the config
        # Simplified traversal: iterate categories
        for category, details in llm_block.items():
            if "models" in details:
                models = details["models"]
                if model_key in models:
                    model_config = models[model_key]
                    output_config = model_config.get("output_config", {})
                    
                    return {
                        "alias": output_config.get("alias", model_key),
                        "structure": output_config.get("structure", "flat"),
                        "folder_name": output_config.get("folder_name"),
                        "display_name": output_config.get("display_name", model_key)
                    }
        
        # Fallback if not found
        return {
            "alias": model_key,
            "structure": "flat",
            "display_name": model_key
        }

    def get_all_config(self) -> Dict[str, Any]:
        """Returns the complete LLM configuration."""
        return self._config_cache
