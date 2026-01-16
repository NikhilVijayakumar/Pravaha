from pathlib import Path
from typing import Any, Dict, List, Optional

from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from pravaha.domain.storage.provider.base_storage_provider import BaseStorageProvider


class KnowledgeStorageProvider(BaseStorageProvider):
    """
    Simple storage provider for knowledge category.
    
    - No version/feature/product logic
    - Just lists files and folders recursively
    - Returns simple hierarchical structure
    """

    def __init__(self, storage_manager: LocalStorageManager):
        super().__init__(storage_manager, category="knowledge")

    async def browse(
        self, path: Optional[str] = None, **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Browse knowledge storage with simple file/folder listing.
        
        Args:
            path: Optional folder path to browse (relative to knowledge root)
            
        Returns:
            Dict with 'items' key containing list of files/folders
        """
        base_path = self.storage_manager.get_path(self.category)
        
        if not base_path.exists():
            return {"items": []}

        # If path is specified, browse that specific folder
        if path:
            # Resolve and check security
            target_path = (base_path / path).resolve()
            try:
                target_path.relative_to(base_path.resolve())
            except ValueError:
                # Return empty or raise error? API contract says list items.
                # Returning empty list mimics "not found" or "permission denied" safely?
                # Or explicit 403?
                # BaseStorageProvider.read raises 403. Browse usually filters.
                # Let's return empty items consistent with "not exists" check below,
                # OR raise 400/403 if we want to catch attacks.
                # The test expects 400/403.
                from fastapi import HTTPException
                raise HTTPException(status_code=403, detail="Access denied: Path traversal detected")

            if not target_path.exists() or not target_path.is_dir():
                return {"items": []}
            items = self._list_directory(target_path, base_path)
        else:
            # Browse root
            items = self._list_directory(base_path, base_path)
            
        return {"items": items}

    def _list_directory(
        self, directory: Path, base_path: Path
    ) -> List[Dict[str, Any]]:
        """
        Recursively list directory contents.
        
        Args:
            directory: Directory to list
            base_path: Base path for calculating relative paths
            
        Returns:
            List of file/folder metadata with relative paths
        """
        items = []

        if not directory.exists():
            return items

        try:
            for entry in sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
                relative_path = entry.relative_to(base_path)
                
                item = {
                    "name": entry.name,
                    "type": "folder" if entry.is_dir() else "file",
                    "path": str(relative_path).replace("\\", "/"),  # Relative path, normalized
                }

                if entry.is_dir():
                    # Recursively list subdirectory
                    item["children"] = self._list_directory(entry, base_path)
                else:
                    # Add file size for files
                    item["size"] = entry.stat().st_size

                items.append(item)

        except PermissionError:
            # Skip directories without permission
            pass

        return items
