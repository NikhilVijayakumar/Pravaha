from pathlib import Path
from typing import Optional, List
import re

from pravaha.domain.storage.protocol.artifact_resolver_protocol import ArtifactVersionResolverProtocol, StorageStage
from pravaha.domain.llm.protocol.llm_config_protocol import LLMConfigManagerProtocol
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager

class ArtifactVersionResolver(ArtifactVersionResolverProtocol):
    def __init__(self, storage_manager: LocalStorageManager, llm_config_manager: LLMConfigManagerProtocol):
        self.storage_manager = storage_manager
        self.llm_config_manager = llm_config_manager

    def _get_base_directory(self, stage: StorageStage, feature: str, product: Optional[str], model_key: str) -> Path:
        if stage == StorageStage.INTERMEDIATE:
            root = self.storage_manager.get_path("intermediate")
            # Intermediate structure: .Amsha/intermediate/{feature}
            # The individual versions are in output_{timestamp} subfolders
            return root / feature
        else:
            root = self.storage_manager.get_path("output")
            if product:
                base = root / product / feature
            else:
                base = root / feature

            # Apply LLM Structure (flat vs folder) for Final stage
            output_config = self.llm_config_manager.resolve_output_config(model_key)
            if output_config["structure"] == "folder":
                folder_name = output_config.get("folder_name", output_config["alias"])
                base = base / folder_name
            
            return base

    def _resolve_model_alias(self, model_key: str) -> str:
        config = self.llm_config_manager.resolve_output_config(model_key)
        return config["alias"]

    def _get_intermediate_versions(self, base_dir: Path, alias: str) -> List[int]:
        """
        For intermediate, versions are undetermined by file suffix.
        They are determined by the existence of the file in timestamped directories:
        output_YYYYMMDDHHMMSS/{alias}.(json|yaml|md|txt)
        """
        if not base_dir.exists():
            return []

        timestamps = []
        # Regex for output_TIMESTAMP
        ts_pattern = re.compile(r"^output_(\d{14})$")
        extensions = [".json", ".yaml", ".md", ".txt"]
        
        for child in base_dir.iterdir():
            if child.is_dir() and ts_pattern.match(child.name):
                # Check if model file exists inside with any valid extension
                found = False
                for ext in extensions:
                    model_file = child / f"{alias}{ext}"
                    if model_file.exists():
                        found = True
                        break
                
                if found:
                    timestamps.append(child.name)
        
        # Sort timestamps (lexicographically work for YYYYMMDDHHMMSS)
        timestamps.sort()
        
        # Version is just the index + 1
        return list(range(1, len(timestamps) + 1))

    def _get_final_versions(self, directory: Path, alias: str) -> List[int]:
        if not directory.exists():
            return []
        
        versions = []
        escaped_alias = re.escape(alias)
        # Matches alias.(json|yaml|md|txt)
        v1_pattern = re.compile(f"^{escaped_alias}\\.(json|yaml|md|txt)$")
        # Matches alias_N.(json|yaml|md|txt)
        vn_pattern = re.compile(f"^{escaped_alias}_(\\d+)\\.(json|yaml|md|txt)$")

        for item in directory.iterdir():
            if not item.is_file():
                continue
            
            if v1_pattern.match(item.name):
                versions.append(1)
            else:
                match = vn_pattern.match(item.name)
                if match:
                    versions.append(int(match.group(1)) + 1)
        
        return sorted(list(set(versions)))

    def get_latest_version(
        self,
        stage: StorageStage,
        feature: str,
        product: Optional[str],
        model_alias: str
    ) -> Optional[int]:
        base_dir = self._get_base_directory(stage, feature, product, model_alias)
        alias = self._resolve_model_alias(model_alias)
        
        if stage == StorageStage.INTERMEDIATE:
            versions = self._get_intermediate_versions(base_dir, alias)
        else:
            versions = self._get_final_versions(base_dir, alias)
            
        return versions[-1] if versions else None

    def get_next_version(
        self,
        stage: StorageStage,
        feature: str,
        product: Optional[str],
        model_alias: str
    ) -> int:
        last = self.get_latest_version(stage, feature, product, model_alias)
        return (last or 0) + 1
