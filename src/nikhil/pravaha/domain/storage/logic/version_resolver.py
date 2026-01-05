from pathlib import Path
from typing import Optional, List
import re

from pravaha.domain.storage.protocol.artifact_resolver_protocol import ArtifactVersionResolverProtocol, StorageStage
from pravaha.domain.storage.protocol.llm_config_protocol import LLMConfigManagerProtocol
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager

class ArtifactVersionResolver(ArtifactVersionResolverProtocol):
    def __init__(self, storage_manager: LocalStorageManager, llm_config_manager: LLMConfigManagerProtocol):
        self.storage_manager = storage_manager
        self.llm_config_manager = llm_config_manager

    def _get_base_directory(self, stage: StorageStage, feature: str, product: Optional[str], model_key: str) -> Path:
        # Determine root based on stage
        if stage == StorageStage.INTERMEDIATE:
            root = self.storage_manager.get_path("intermediate")
            # Spec: .Amsha/output/intermediate/output/{FeatureName}/
            # We assume 'root' points to .Amsha/output/intermediate or similar.
            # We append 'output' as per spec if implied, but let's stick to cleaner:
            # root / feature
            # If strictly following spec line 86: .Amsha/output/intermediate/output/{FeatureName}
            # If the config 'intermediate' points to .Amsha/output/intermediate
            # Then we might need to add 'output'.
            # Let's assume the config points to the PARENT of feature folders.
            base = root / feature
        else:
            root = self.storage_manager.get_path("output") # Mapped to Final
            if product:
                base = root / product / feature
            else:
                base = root / feature

        # Apply LLM Structure (flat vs folder)
        output_config = self.llm_config_manager.resolve_output_config(model_key)
        if output_config["structure"] == "folder":
            folder_name = output_config.get("folder_name", output_config["alias"])
            base = base / folder_name
        
        return base

    def _resolve_model_alias(self, model_key: str) -> str:
        config = self.llm_config_manager.resolve_output_config(model_key)
        return config["alias"]

    def _get_versions(self, directory: Path, alias: str) -> List[int]:
        if not directory.exists():
            return []
        
        versions = []
        # Pattern: {alias}.json (v1) or {alias}_{N}.json (vN+1)
        # Regex to capture version
        # Escape alias for regex safety
        escaped_alias = re.escape(alias)
        
        # Matches alias.json
        v1_pattern = re.compile(f"^{escaped_alias}\\.json$")
        # Matches alias_N.json
        vn_pattern = re.compile(f"^{escaped_alias}_(\\d+)\\.json$")

        for item in directory.iterdir():
            if not item.is_file():
                continue
            
            if v1_pattern.match(item.name):
                versions.append(1)
            else:
                match = vn_pattern.match(item.name)
                if match:
                    # _K -> version K+1
                    k = int(match.group(1))
                    versions.append(k + 1)
        
        return sorted(versions)

    def get_latest_version(
        self,
        stage: StorageStage,
        feature: str,
        product: Optional[str],
        model_alias: str
    ) -> Optional[int]:
        # 'model_alias' argument name in protocol matches 'model_key' usage intent?
        # The protocol says 'model_alias', but caller might pass key.
        # Assuming caller passes the key to lookup config, or we treat it as key.
        # Let's assume the argument is the 'model identifier/key' used in config.
        
        base_dir = self._get_base_directory(stage, feature, product, model_alias)
        alias = self._resolve_model_alias(model_alias)
        
        versions = self._get_versions(base_dir, alias)
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
