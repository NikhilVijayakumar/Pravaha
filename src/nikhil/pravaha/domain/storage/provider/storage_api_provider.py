import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, HTTPException

from pravaha.domain.storage.model.storage_config_request import StorageConfigRequest
from pravaha.domain.storage.model.artifact_metadata import (
    ArtifactMetadata,
    GroupedArtifactMetadata,
)
from pravaha.domain.storage.protocol.llm_config_protocol import LLMConfigManagerProtocol
from pravaha.domain.storage.protocol.artifact_resolver_protocol import (
    StoragePathResolverProtocol,
    ArtifactVersionResolverProtocol,
    StorageStage,
)
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager


class StorageAPIProvider:
    """
    Canonical Storage API Provider

    Responsibilities:
    - Browse logical artifacts (UI-safe, flat)
    - Read artifact content
    - Enforce correct Product / Feature semantics
    - Hide filesystem layout from consumers
    """

    def __init__(
        self,
        storage_manager: LocalStorageManager,
        llm_config_manager: LLMConfigManagerProtocol,
        path_resolver: StoragePathResolverProtocol,
        version_resolver: ArtifactVersionResolverProtocol,
    ):
        self.storage_manager = storage_manager
        self.llm_config = llm_config_manager
        self.path_resolver = path_resolver
        self.version_resolver = version_resolver

        self.router = APIRouter(prefix="/storage")
        self._setup_routes()

    # ---------------------------------------------------------------------
    # ROUTES
    # ---------------------------------------------------------------------

    def _setup_routes(self):
        self.router.post("/config")(self.set_storage_config)
        self.router.get("/config")(self.get_storage_config)
        self.router.get("/schema/config")(self.get_config_schema)

        for category in ["intermediate", "output", "knowledge"]:
            self.router.get(f"/{category}/browse")(self._create_browse_handler(category))
            self.router.get(f"/{category}/read")(self._create_read_handler(category))

    # ---------------------------------------------------------------------
    # CORE LISTING LOGIC
    # ---------------------------------------------------------------------

    async def _list_artifacts_logic(
        self,
        stage: StorageStage,
        feature: Optional[str] = None,
        product: Optional[str] = None,
        model: Optional[str] = None,
    ) -> List[ArtifactMetadata]:
        """
        Scan artifacts for a given stage and normalize into logical artifacts.
        """
        artifacts = []

        base_root = self.storage_manager.get_path(
            "intermediate" if stage == StorageStage.INTERMEDIATE else "output"
        )

        if not base_root.exists():
            return []

        # -----------------------------------------------------------------
        # INTERMEDIATE: .Amsha/intermediate/output/{feature}/output_TIMESTAMP/
        # -----------------------------------------------------------------
        if stage == StorageStage.INTERMEDIATE:
            if feature:
                self._scan_intermediate_feature(
                    base_root / feature, artifacts, feature, model
                )
            else:
                for feature_dir in base_root.iterdir():
                    if feature_dir.is_dir():
                        self._scan_intermediate_feature(
                            feature_dir, artifacts, feature_dir.name, model
                        )

        # -----------------------------------------------------------------
        # FINAL: .Amsha/final/{product}/{feature}/
        # -----------------------------------------------------------------
        else:
            for product_dir in base_root.iterdir():
                if not product_dir.is_dir():
                    continue
                if product and product_dir.name != product:
                    continue

                for feature_dir in product_dir.iterdir():
                    if not feature_dir.is_dir():
                        continue
                    if feature and feature_dir.name != feature:
                        continue

                    self._scan_final_feature(
                        feature_dir,
                        artifacts,
                        feature=feature_dir.name,
                        product=product_dir.name,
                        model_filter=model,
                    )

        return artifacts

    # ---------------------------------------------------------------------
    # INTERMEDIATE SCAN
    # ---------------------------------------------------------------------

    def _scan_intermediate_feature(
        self,
        directory: Path,
        artifacts: list,
        feature: str,
        model_filter: Optional[str],
    ):
        if not directory.exists():
            return

        ts_pattern = re.compile(r"^output_(\d{14})$")
        timestamp_dirs = sorted(
            [d for d in directory.iterdir() if d.is_dir() and ts_pattern.match(d.name)]
        )

        version_map = {d.name: i + 1 for i, d in enumerate(timestamp_dirs)}

        for ts_dir in timestamp_dirs:
            version = version_map[ts_dir.name]

            for file in ts_dir.iterdir():
                if file.suffix not in {".json", ".yaml", ".md", ".txt"}:
                    continue

                alias = file.stem
                if model_filter and alias != model_filter:
                    continue

                config = self.llm_config.resolve_output_config(alias)
                display_name = f"{config.get('display_name', alias)}{file.suffix}"

                artifacts.append(
                    {
                        "feature": feature,
                        "product": None,
                        "model": alias,
                        "version": version,
                        "stage": "intermediate",
                        "path": str(file),
                        "created_at": datetime.fromtimestamp(
                            file.stat().st_ctime
                        ).isoformat(),
                        "display_name": display_name,
                    }
                )

    # ---------------------------------------------------------------------
    # FINAL SCAN (DETERMINISTIC)
    # ---------------------------------------------------------------------

    def _scan_final_feature(
        self,
        directory: Path,
        artifacts: list,
        feature: str,
        product: str,
        model_filter: Optional[str],
    ):
        for root, _, files in os.walk(directory):
            for filename in files:
                file = Path(root) / filename
                if file.suffix not in {".json", ".yaml", ".md", ".txt"}:
                    continue

                stem = file.stem
                version = 1
                alias = stem

                if "_" in stem and stem.rsplit("_", 1)[1].isdigit():
                    alias, suffix = stem.rsplit("_", 1)
                    version = int(suffix) + 1

                if model_filter and alias != model_filter:
                    continue

                config = self.llm_config.resolve_output_config(alias)
                display_name = f"{config.get('display_name', alias)}{file.suffix}"

                artifacts.append(
                    {
                        "feature": feature,
                        "product": product,
                        "model": alias,
                        "version": version,
                        "stage": "final",
                        "path": str(file),
                        "created_at": datetime.fromtimestamp(
                            file.stat().st_ctime
                        ).isoformat(),
                        "display_name": display_name,
                    }
                )

    # ---------------------------------------------------------------------
    # GROUPING (UI-FLAT)
    # ---------------------------------------------------------------------

    def _group_artifacts(self, artifacts: List[dict]) -> List[GroupedArtifactMetadata]:
        grouped = {}

        for art in artifacts:
            key = (
                art["feature"],
                art["product"],
                art["model"],
                art["stage"],
            )

            if key not in grouped:
                grouped[key] = {
                    "feature": art["feature"],
                    "product": art["product"],
                    "model": art["model"],
                    "stage": art["stage"],
                    "display_name": art["display_name"],
                    "latest_version": 0,
                    "versions": [],
                }

            grouped[key]["versions"].append(
                {
                    "version": art["version"],
                    "path": art["path"],
                    "created_at": art["created_at"],
                }
            )

            grouped[key]["latest_version"] = max(
                grouped[key]["latest_version"], art["version"]
            )

        for group in grouped.values():
            group["versions"].sort(key=lambda v: v["version"], reverse=True)

        return list(grouped.values())

    # ---------------------------------------------------------------------
    # HANDLERS
    # ---------------------------------------------------------------------

    def _create_browse_handler(self, category: str):
        async def handler(
            feature: Optional[str] = None,
            product: Optional[str] = None,
        ):
            if category == "knowledge":
                base = self.storage_manager.get_path("knowledge")
                return {
                    "items": [
                        {
                            "name": p.name,
                            "type": "folder" if p.is_dir() else "file",
                        }
                        for p in base.iterdir()
                    ]
                }

            stage = (
                StorageStage.INTERMEDIATE
                if category == "intermediate"
                else StorageStage.FINAL
            )

            artifacts = await self._list_artifacts_logic(
                stage, feature=feature, product=product
            )
            return self._group_artifacts(artifacts)

        return handler

    def _create_read_handler(self, category: str):
        async def handler(path: str):
            file_path = Path(path).resolve()
            root = self.storage_manager.get_path(category).resolve()

            if not str(file_path).startswith(str(root)):
                raise HTTPException(status_code=403, detail="Access denied")

            if not file_path.exists() or not file_path.is_file():
                raise HTTPException(status_code=404, detail="File not found")

            content = file_path.read_text(encoding="utf-8")
            if file_path.suffix == ".json":
                try:
                    return {"content": json.loads(content)}
                except json.JSONDecodeError:
                    pass

            return {"content": content}

        return handler

    # ---------------------------------------------------------------------
    # CONFIG
    # ---------------------------------------------------------------------

    async def set_storage_config(self, req: StorageConfigRequest):
        self.storage_manager.update_config(
            req.output_path, req.intermediate_path, req.knowledge_path
        )
        return {"status": "Configured successfully"}

    async def get_storage_config(self):
        return self.storage_manager.get_config()

    async def get_config_schema(self):
        return StorageConfigRequest.model_json_schema()