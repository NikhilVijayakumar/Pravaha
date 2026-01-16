import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from pravaha.domain.llm.protocol.llm_config_protocol import LLMConfigManagerProtocol
from pravaha.domain.storage.provider.base_storage_provider import BaseStorageProvider


class IntermediateStorageProvider(BaseStorageProvider):
    """
    Storage provider for intermediate category.
    
    Handles:
    - Feature-based organization
    - Timestamp-based versioning (output_TIMESTAMP directories)
    - Model/alias resolution via LLM config
    """

    def __init__(
        self,
        storage_manager: LocalStorageManager,
        llm_config_manager: LLMConfigManagerProtocol,
    ):
        super().__init__(storage_manager, category="intermediate")
        self.llm_config = llm_config_manager

    async def browse(
        self, feature: Optional[str] = None, product: Optional[str] = None, **kwargs
    ) -> List[dict]:
        """
        Browse intermediate artifacts with version/feature logic.
        
        Args:
            feature: Optional feature filter
            product: Ignored for intermediate (no product hierarchy)
            **kwargs: Can include 'model' filter
            
        Returns:
            List of grouped artifact metadata
        """
        model_filter = kwargs.get("model")
        artifacts = []

        base_root = self.storage_manager.get_path(self.category)
        if not base_root.exists():
            return []

        # Scan features
        if feature:
            self._scan_intermediate_feature(
                base_root / feature, artifacts, feature, model_filter
            )
        else:
            for feature_dir in base_root.iterdir():
                if feature_dir.is_dir():
                    self._scan_intermediate_feature(
                        feature_dir, artifacts, feature_dir.name, model_filter
                    )

        return self._group_artifacts(artifacts)

    def _scan_intermediate_feature(
        self,
        directory: Path,
        artifacts: list,
        feature: str,
        model_filter: Optional[str],
    ):
        """Scan intermediate feature directory for versioned artifacts."""
        if not directory.exists():
            return

        storage_root = self.storage_manager.get_path(self.category)
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
                
                # Use relative path from storage root
                relative_path = str(file.relative_to(storage_root)).replace("\\", "/")

                artifacts.append(
                    {
                        "feature": feature,
                        "product": None,
                        "model": alias,
                        "version": version,
                        "stage": "intermediate",
                        "path": relative_path,
                        "created_at": datetime.fromtimestamp(
                            file.stat().st_ctime
                        ).isoformat(),
                        "display_name": display_name,
                    }
                )

    def _group_artifacts(self, artifacts: List[dict]) -> List[dict]:
        """Group artifacts by feature/product/model."""
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
