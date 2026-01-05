import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from pravaha.domain.storage.model.storage_config_request import StorageConfigRequest
from pravaha.domain.storage.model.artifact_metadata import ArtifactMetadata
from pravaha.domain.storage.protocol.llm_config_protocol import LLMConfigManagerProtocol
from pravaha.domain.storage.protocol.artifact_resolver_protocol import (
    StoragePathResolverProtocol, 
    ArtifactVersionResolverProtocol,
    StorageStage
)
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager

class StorageAPIProvider:
    def __init__(
        self, 
        storage_manager: LocalStorageManager,
        llm_config_manager: LLMConfigManagerProtocol,
        path_resolver: StoragePathResolverProtocol,
        version_resolver: ArtifactVersionResolverProtocol
    ):
        self.storage_manager = storage_manager
        self.llm_config = llm_config_manager
        self.path_resolver = path_resolver
        self.version_resolver = version_resolver
        
        self.router = APIRouter(prefix="/storage")
        self._setup_routes()

    def _setup_routes(self):
        # Config Endpoints
        self.router.post("/config")(self.set_storage_config)
        self.router.get("/config")(self.get_storage_config)
        self.router.get("/schema/config")(self.get_config_schema)
        
        # Hybrid Endpoints
        # ... (rest of the code)

    # ... (existing methods)

    async def _list_artifacts_logic(
        self, 
        stage: StorageStage,
        feature: Optional[str] = None, 
        product: Optional[str] = None,
        model: Optional[str] = None
    ) -> List[ArtifactMetadata]:
        """
        Internal method to scan artifacts for a specific stage.
        """
        artifacts = []
        base_root = self.storage_manager.get_path("intermediate" if stage == StorageStage.INTERMEDIATE else "output")
        if not base_root.exists():
            return []

        # Logic adapted from previous list_artifacts, specific to one stage
        if stage == StorageStage.INTERMEDIATE:
             # Structure: base_root / feature
            if feature:
                 self._scan_dir(base_root / feature, artifacts, stage, feature, None, model)
            else:
                for child in base_root.iterdir():
                    if child.is_dir():
                        self._scan_dir(child, artifacts, stage, child.name, None, model)
        
        elif stage == StorageStage.FINAL:
            if product and feature:
                 self._scan_dir(base_root / product / feature, artifacts, stage, feature, product, model)
            elif feature and not product:
                if (base_root / feature).exists():
                     self._scan_dir(base_root / feature, artifacts, stage, feature, None, model)
                for child in base_root.iterdir():
                    if child.is_dir() and (child / feature).exists():
                         self._scan_dir(child / feature, artifacts, stage, feature, child.name, model)
            else:
                 for l1 in base_root.iterdir():
                     if l1.is_dir():
                         # Assume depth-1 is Feature if no product, or Product if subdirs exist?
                         # Heuristic: treat as feature first
                         self._scan_dir(l1, artifacts, stage, l1.name, None, model)
                         
                         # treat as product
                         for l2 in l1.iterdir():
                             if l2.is_dir():
                                 self._scan_dir(l2, artifacts, stage, l2.name, l1.name, model)
        return artifacts

    def _scan_dir(self, directory: Path, artifacts: List[dict], stage: StorageStage, feature: str, product: Optional[str], model_filter: Optional[str]):
        if not directory.exists():
            return
            
        stage_str = "intermediate" if stage == StorageStage.INTERMEDIATE else "final"
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if not file.endswith(".json"):
                    continue
                
                stem = Path(file).stem
                parts = stem.rsplit("_", 1)
                
                version = 1
                alias = stem
                
                if len(parts) == 2 and parts[1].isdigit():
                    alias = parts[0]
                    version = int(parts[1]) + 1
                
                if model_filter and alias != model_filter:
                    continue
                
                # Resolve Display Name
                config = self.llm_config.resolve_output_config(alias)
                display_name = config.get("display_name", alias)
                
                full_path = Path(root) / file
                stats = full_path.stat()
                created_at = datetime.fromtimestamp(stats.st_ctime).isoformat()
                
                artifacts.append({
                    "feature": feature,
                    "product": product,
                    "model": alias,
                    "version": version,
                    "stage": stage_str,
                    "path": str(full_path),
                    "created_at": created_at,
                    "display_name": display_name
                })

    def _create_browse_handler(self, category: str):
        async def handler(path: str = "", feature: Optional[str] = None, product: Optional[str] = None):
            if category == "knowledge":
                # Legacy Logic
                base_path = self.storage_manager.get_path(category)
                target = (base_path / path).resolve()

                if not str(target).startswith(str(base_path.resolve())):
                    raise HTTPException(status_code=403, detail="Access denied: Invalid path")

                if not target.exists():
                    raise HTTPException(status_code=404, detail="Path not found")
                
                if not target.is_dir():
                     raise HTTPException(status_code=400, detail="Path is not a directory")

                items = []
                for item in target.iterdir():
                    items.append({
                        "name": item.name,
                        "type": "folder" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else 0
                    })
                return {"items": sorted(items, key=lambda x: (x["type"] != "folder", x["name"]))}
            
            else:
                # Artifact Logic
                stage = StorageStage.INTERMEDIATE if category == "intermediate" else StorageStage.FINAL
                return await self._list_artifacts_logic(stage, feature, product)

        return handler

    def _create_read_handler(self, category: str):
        async def handler(path: str):
            if category == "knowledge":
                # Legacy Logic (Relative Path)
                base_path = self.storage_manager.get_path(category)
                file_path = (base_path / path).resolve()
            else:
                # Artifact Logic (Absolute Path check)
                # The 'path' param here comes from the artifact metadata 'path' field which is absolute.
                # However, FastAPI might receive it as a query param.
                file_path = Path(path).resolve()
            
            # General Security Validation for all
            # For artifacts, we need to ensure it's within allowed roots (intermediate or output)
            if category == "knowledge":
                root = self.storage_manager.get_path("knowledge").resolve()
                if not str(file_path).startswith(str(root)):
                     raise HTTPException(status_code=403, detail="Access denied")
            else:
                # For output/intermediate, strictly check against their specific root
                root = self.storage_manager.get_path(category).resolve()
                if not str(file_path).startswith(str(root)):
                     raise HTTPException(status_code=403, detail=f"Access denied: {path} not in {category}")

            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            
            if not file_path.is_file():
                 raise HTTPException(status_code=400, detail="Path is not a file")

            content = file_path.read_text(encoding='utf-8')
            parsed_content = content
            if file_path.suffix == ".json":
                try:
                    parsed_content = json.loads(content)
                except json.JSONDecodeError:
                    parsed_content = content
            
            return {"content": parsed_content}
        return handler

    # ... Existing methods set_storage_config, get_storage_config etc. ...
    async def set_storage_config(self, req: StorageConfigRequest):
        self.storage_manager.update_config(req.output_path, req.intermediate_path, req.knowledge_path)
        return {"status": "Configured successfully"}

    async def get_storage_config(self):
        config = self.storage_manager.get_config()
        return {
            "output_path": config.get("output"),
            "intermediate_path": config.get("intermediate"),
            "knowledge_path": config.get("knowledge")
        }

    async def get_config_schema(self):
        return StorageConfigRequest.model_json_schema()