import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pravaha.domain.storage.provider.base_storage_provider import BaseStorageProvider
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from pravaha.domain.storage.protocol.llm_config_protocol import LLMConfigManagerProtocol


class OutputStorageProvider(BaseStorageProvider):
    """
    Storage provider for output (final) category.
    
    Handles:
    - Product/Feature hierarchy
    - File suffix-based versioning
    - Model/alias resolution via LLM config
    """

    def __init__(
        self,
        storage_manager: LocalStorageManager,
        llm_config_manager: LLMConfigManagerProtocol,
    ):
        super().__init__(storage_manager, category="output")
        self.llm_config = llm_config_manager

    async def browse(
        self, feature: Optional[str] = None, product: Optional[str] = None, **kwargs
    ) -> List[dict]:
        """
        Browse output artifacts with product/feature/version logic.
        
        Args:
            feature: Optional feature filter
            product: Optional product filter
            **kwargs: Can include 'model' filter
            
        Returns:
            List of grouped artifact metadata
        """
        model_filter = kwargs.get("model")
        artifacts = []

        base_root = self.storage_manager.get_path(self.category)
        if not base_root.exists():
            return []

        # Scan product/feature hierarchy
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
                    model_filter=model_filter,
                )

        return self._group_artifacts(artifacts)

    def _scan_final_feature(
        self,
        directory: Path,
        artifacts: list,
        feature: str,
        product: str,
        model_filter: Optional[str],
    ):
        """Scan output feature directory for versioned artifacts."""
        for root, _, files in os.walk(directory):
            for filename in files:
                file = Path(root) / filename
                if file.suffix not in {".json", ".yaml", ".md", ".txt"}:
                    continue

                stem = file.stem
                version = 1
                alias = stem

                # Detect version from file suffix (e.g., model_1 -> version 2)
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
