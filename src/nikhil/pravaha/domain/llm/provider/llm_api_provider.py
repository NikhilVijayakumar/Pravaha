from typing import Dict, Any
from fastapi import APIRouter
from pravaha.domain.llm.protocol.llm_config_protocol import LLMConfigManagerProtocol

class LLMAPIProvider:
    def __init__(self, llm_config_manager: LLMConfigManagerProtocol):
        self.llm_config = llm_config_manager
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        self.router.get("/config")(self.get_config)

    async def get_config(self) -> Dict[str, Any]:
        """Exposes the full LLM configuration."""
        return self.llm_config.get_all_config()
