from pathlib import Path
from typing import Optional

from pravaha.domain.storage.protocol.artifact_resolver_protocol import (
    StoragePathResolverProtocol, 
    ArtifactVersionResolverProtocol, 
    StorageStage
)
from pravaha.domain.storage.protocol.llm_config_protocol import LLMConfigManagerProtocol
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager

class StoragePathResolver(StoragePathResolverProtocol):
    def __init__(
        self, 
        storage_manager: LocalStorageManager,
        llm_config_manager: LLMConfigManagerProtocol,
        version_resolver: ArtifactVersionResolverProtocol
    ):
        self.storage_manager = storage_manager
        self.llm_config_manager = llm_config_manager
        self.version_resolver = version_resolver

    def resolve_output_path(
        self,
        stage: StorageStage,
        feature: str,
        product: Optional[str],
        model_key: str
    ) -> Path:
        # 1. Get Next Version
        next_version = self.version_resolver.get_next_version(stage, feature, product, model_key)
        
        # 2. Resolve Base Directory (reusing logic or calling resolver if it exposed it?)
        # Since VersionResolver doesn't expose base dir publicly in protocol, we reconstruct it.
        # Ideally, this logic belongs in one place. 
        # But for now, we duplicate the base directory resolution logic or make it shared.
        # Let's clean this up by adding a shared helper or just duplicating strictly for now.
        
        # Copied logic from VersionResolver._get_base_directory to ensure consistency
        if stage == StorageStage.INTERMEDIATE:
            root = self.storage_manager.get_path("intermediate")
            base = root / feature
        else:
            root = self.storage_manager.get_path("output")
            if product:
                base = root / product / feature
            else:
                base = root / feature

        output_config = self.llm_config_manager.resolve_output_config(model_key)
        if output_config["structure"] == "folder":
             folder_name = output_config.get("folder_name", output_config["alias"])
             base = base / folder_name

        # 3. Construct Filename
        alias = output_config["alias"]
        
        # Versioning:
        # v1 -> {alias}.json
        # vN -> {alias}_{N-1}.json
        
        if next_version == 1:
            filename = f"{alias}.json"
        else:
            # version 2 -> _1.json
            filename = f"{alias}_{next_version - 1}.json"
            
        full_path = base / filename
        
        # Ensure parent exists? 
        # The resolver responsiblity is just to return path.
        # But for convenience, we don't. The writer should ensure directory exists.
        
        return full_path
