import pytest
from unittest.mock import MagicMock
from pravaha.domain.llm.provider.llm_api_provider import LLMAPIProvider
from pravaha.domain.llm.protocol.llm_config_protocol import LLMConfigManagerProtocol

@pytest.mark.asyncio
async def test_get_config():
    llm_manager = MagicMock(spec=LLMConfigManagerProtocol)
    provider = LLMAPIProvider(llm_manager)
    
    # Mock config return
    mock_config = {"llm": {"models": {"gpt": {}}}}
    llm_manager.get_all_config.return_value = mock_config
    
    result = await provider.get_config()
    
    assert result == mock_config
    llm_manager.get_all_config.assert_called_once()
