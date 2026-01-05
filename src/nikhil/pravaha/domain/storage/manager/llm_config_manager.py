import shutil
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from pravaha.domain.storage.protocol.llm_config_protocol import LLMConfigManagerProtocol, LLMOutputConfig

class LLMConfigManager(LLMConfigManagerProtocol):
    def __init__(self, config_path: Optional[Path] = None):
        self.project_root = Path.cwd()
        # Internal cache location
        self.config_dir = self.project_root / ".Pravaha" / "config"
        self.config_file = self.config_dir / "llm_config.json"
        
        # Caching Logic
        if config_path and config_path.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            try:
                # Read YAML source
                with open(config_path, "r") as f:
                    yaml_content = yaml.safe_load(f) or {}
                
                # Write JSON cache
                with open(self.config_file, "w") as f:
                    json.dump(yaml_content, f, indent=2)
                    
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
                self._config_cache = json.load(f) or {}
        except Exception as e:
            print(f"Error loading LLM config: {e}")
            self._config_cache = {}

    def resolve_output_config(self, model_key: str) -> LLMOutputConfig:
        """
        Resolves output configuration for a model key.
        Searches recursively for 'models' -> {model_key}.
        """
        llm_block = self._config_cache.get("llm", {})
        
        # Normalize input key for comparison
        search_key = model_key.lower()

        for category, details in llm_block.items():
            if "models" in details:
                models = details["models"]
                for key, model_config in models.items():
                    # Check 1: Exact key match (or case-insensitive)
                    if key.lower() == search_key:
                        output_config = model_config.get("output_config", {})
                        return self._build_output_config(output_config, key)

                    # Check 2: Alias match from output_config
                    output_config = model_config.get("output_config", {})
                    alias = output_config.get("alias", "").lower()
                    if alias and alias == search_key:
                        return self._build_output_config(output_config, key)

                    # Check 3: Model specific name match (last part of model string)
                    # e.g. "lm_studio/gemma-3-12b-it" -> "gemma-3-12b-it"
                    model_str = model_config.get("model", "")
                    if model_str:
                        # Extract the last part after slash
                        parts = model_str.rsplit("/", 1)
                        model_name = parts[-1].lower() if len(parts) > 1 else model_str.lower()
                        
                        if model_name == search_key:
                            return self._build_output_config(output_config, key)
        
        # Fallback if not found
        return {
            "alias": model_key,
            "structure": "flat",
            "display_name": model_key.replace("_", " ").title()
        }

    def _build_output_config(self, output_config: Dict[str, Any], default_key: str) -> LLMOutputConfig:
        return {
            "alias": output_config.get("alias", default_key),
            "structure": output_config.get("structure", "flat"),
            "folder_name": output_config.get("folder_name"),
            "display_name": output_config.get("display_name", default_key)
        }

    def get_all_config(self) -> Dict[str, Any]:
        """Returns the complete LLM configuration."""
        return self._config_cache
