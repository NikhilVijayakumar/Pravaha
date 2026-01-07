
import asyncio
from typing import Optional, Any, List, Dict
from pydantic import BaseModel
from pravaha.domain.bot.model.application_request import ApplicationRequest
import pravaha.domain.bot.model.application_request as app_req_module
print(f"DEBUG: ApplicationRequest imported from: {app_req_module.__file__}")

from pravaha.domain.bot.provider.bot_api_provider import BotAPIProvider

# Mock Task Config
class MockTaskConfig:
    class UtilsType:
        pass
    class ApplicationType:
        pass
    class ExecutionTarget:
        pass

# Mock Bot Manager
class MockBotManager:
    def __init__(self):
        self.last_llm_config = None

    def run(self, utility_task: Any, inputs: Optional[List[Dict[str, Any]]] = None) -> Any:
        return "mock_result"

    def stream_run(self, application_task: Any, inputs: Optional[List[Dict[str, Any]]] = None, llm_config: Optional[Any] = None):
        self.last_llm_config = llm_config
        yield "mock_stream_chunk"

    def get_input_model(self, task: Any) -> Optional[Any]:
        return BaseModel
    
    def get_output_model(self, task: Any) -> Optional[Any]:
        return BaseModel

async def verify_dynamic_llm_config():
    print("Starting verification for Dynamic LLM Configuration...")
    
    bot_manager = MockBotManager()
    task_config = MockTaskConfig()
    provider = BotAPIProvider(bot_manager=bot_manager, task_config=task_config)
    
    test_llm_config = {"model": "gpt-4", "temperature": 0.7}
    request = ApplicationRequest(
        task_name="test_task",
        inputs=[{"input": "test"}],
        llm_config=test_llm_config
    )
    
    print(f"Sending request with llm_config: {test_llm_config}")
    print(f"DEBUG: Request object: {request.dict()}")
    
    # We need to run the async method
    response = await provider.run_application_stream(request)
    
    # Consume the response to ensure execution
    async for item in response.body_iterator:
        pass

    if bot_manager.last_llm_config == test_llm_config:
        print("SUCCESS: BotManager received the correct llm_config.")
    else:
        print(f"FAILURE: BotManager received {bot_manager.last_llm_config}, expected {test_llm_config}")

if __name__ == "__main__":
    asyncio.run(verify_dynamic_llm_config())
