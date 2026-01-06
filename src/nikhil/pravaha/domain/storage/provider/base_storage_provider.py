import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict
from fastapi import HTTPException

from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager


class BaseStorageProvider(ABC):
    """
    Base class for storage providers.
    
    Provides:
    - Common read handler with security checks
    - Shared dependencies
    - Abstract browse method for subclasses to implement
    """

    def __init__(self, storage_manager: LocalStorageManager, category: str):
        self.storage_manager = storage_manager
        self.category = category

    @abstractmethod
    async def browse(
        self, feature: str = None, product: str = None, **kwargs
    ) -> Any:
        """
        Browse artifacts in this storage category.
        
        Args:
            feature: Optional feature filter
            product: Optional product filter
            **kwargs: Additional category-specific filters
            
        Returns:
            Category-specific browse response
        """
        pass

    async def read(self, path: str) -> Dict[str, Any]:
        """
        Read file content with security checks.
        
        Args:
            path: Absolute path to the file
            
        Returns:
            Dict containing file content
            
        Raises:
            HTTPException: If access is denied or file not found
        """
        file_path = Path(path).resolve()
        root = self.storage_manager.get_path(self.category).resolve()

        # Security check: ensure file is within allowed root
        if not str(file_path).startswith(str(root)):
            raise HTTPException(status_code=403, detail="Access denied")

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")

        content = file_path.read_text(encoding="utf-8")
        
        # Parse JSON if applicable
        if file_path.suffix == ".json":
            try:
                return {"content": json.loads(content)}
            except json.JSONDecodeError:
                pass

        return {"content": content}
