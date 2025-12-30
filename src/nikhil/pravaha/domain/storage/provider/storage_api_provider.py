import json
from fastapi import APIRouter, HTTPException
from pravaha.domain.storage.model.storage_config_request import StorageConfigRequest


class StorageAPIProvider:
    def __init__(self, storage_manager):
        self.storage_manager = storage_manager
        self.router = APIRouter(prefix="/storage")
        self._setup_routes()

    def _setup_routes(self):
        self.router.post("/config")(self.set_storage_config)

        # Explicit categories
        categories = ["output", "intermediate", "knowledge"]
        for cat in categories:
            # We use lambda or partial to pass the category string to the generic handlers
            
            # New flexible browse endpoint
            self.router.get(f"/{cat}/browse", name=f"browse_{cat}")(
                self._create_browse_handler(cat)
            )
            # New flexible read endpoint
            self.router.get(f"/{cat}/read", name=f"read_{cat}")(
                self._create_read_handler(cat)
            )

    async def set_storage_config(self, req: StorageConfigRequest):
        self.storage_manager.update_config(req.output_path, req.intermediate_path, req.knowledge_path)
        return {"status": "Configured successfully"}

    def _create_browse_handler(self, category: str):
        async def handler(path: str = ""):
            base_path = self.storage_manager.get_path(category)
            target = (base_path / path).resolve()

            # Security check: Ensure target is within base_path
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

        return handler

    def _create_read_handler(self, category: str):
        async def handler(path: str):
            base_path = self.storage_manager.get_path(category)
            file_path = (base_path / path).resolve()

            # Security check
            if not str(file_path).startswith(str(base_path.resolve())):
                raise HTTPException(status_code=403, detail="Access denied")

            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            
            if not file_path.is_file():
                 raise HTTPException(status_code=400, detail="Path is not a file")

            content = file_path.read_text(encoding='utf-8')
            return {"content": json.loads(content) if file_path.suffix == ".json" else content}

        return handler