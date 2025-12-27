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
            self.router.get(f"/{cat}/folders", name=f"list_{cat}_folders")(
                self._create_folder_handler(cat)
            )
            self.router.get(f"/{cat}/{{folder_name}}/files", name=f"list_{cat}_files")(
                self._create_file_handler(cat)
            )
            self.router.get(f"/{cat}/{{folder_name}}/{{file_name}}", name=f"get_{cat}_content")(
                self._create_content_handler(cat)
            )

    async def set_storage_config(self, req: StorageConfigRequest):
        self.storage_manager.update_config(req.output_path, req.intermediate_path, req.knowledge_path)
        return {"status": "Configured successfully"}

    def _create_folder_handler(self, category: str):
        async def handler():
            base_path = self.storage_manager.get_path(category)
            return {"folders": sorted([f.name for f in base_path.iterdir() if f.is_dir()])}

        return handler

    def _create_file_handler(self, category: str):
        async def handler(folder_name: str):
            base_path = self.storage_manager.get_path(category)
            target = base_path / folder_name
            if not target.exists(): raise HTTPException(status_code=404)
            return {"files": [{"name": f.name, "size": f.stat().st_size} for f in target.iterdir() if f.is_file()]}

        return handler

    def _create_content_handler(self, category: str):
        async def handler(folder_name: str, file_name: str):
            base_path = self.storage_manager.get_path(category)
            file_path = base_path / folder_name / file_name
            if not file_path.exists(): raise HTTPException(status_code=404)

            content = file_path.read_text(encoding='utf-8')
            return {"content": json.loads(content) if file_path.suffix == ".json" else content}

        return handler