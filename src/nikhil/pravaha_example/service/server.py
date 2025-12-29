from fastapi import FastAPI
from pravaha.domain.bot.provider.bot_api_provider import BotAPIProvider
from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager

# Import example components
from pravaha_example.config.settings import ApplicationType, UtilsType, ExecutionTarget
from pravaha_example.domain.calculator_tool import CalculatorTool
from pravaha_example.domain.math_bot import MathBot

# Define a simple BotManager stub to wire things up
# In a real app, this might be more complex or imported from domain/bot/manager
class SimpleBotManager:
    def __init__(self):
        self.apps = {
           ApplicationType.MATH_ASSISTANT: MathBot()
        }
        self.utils = {
           UtilsType.CALCULATOR: CalculatorTool()
        }

    def run(self, utility_task: str, inputs=None):
        # Convert string to Enum if needed, or just look up by value if we change map
        # Ideally the Manager should expect the Enum type but FastAPI might pass string if not correctly typed in endpoint?
        # Actually endpoint calls `req.task_name` which is typed as Enum in `_setup_routes`. Pydantic should convert it.
        # But `SimpleBotManager` keys are Enums.
        # Let's verify what is actually passed.
        # If the keys in self.utils are Enums, and utility_task is Enum, it should work.
        # If utility_task comes as string, we need to convert.
        
        # Safe lookup handling both or ensuring conversion
        tool = None
        if utility_task in self.utils:
            tool = self.utils[utility_task]
        else:
             # Try converting from string value
             for k, v in self.utils.items():
                 if k.value == utility_task:
                     tool = v
                     break
        
        if not tool:
            raise ValueError(f"Tool {utility_task} not found")
        return tool.run(inputs)

    def stream_run(self, application_task: str, inputs=None):
        app = None
        if application_task in self.apps:
            app = self.apps[application_task]
        else:
             for k, v in self.apps.items():
                 if k.value == application_task:
                     app = v
                     break
        
        if not app:
             async def error_gen():
                 yield f"Error: App {application_task} not found"
             return error_gen()
        return app.stream_run(inputs)

# Create App
app = FastAPI(title="Pravaha Example Server")

# 1. Setup Storage
storage_manager = LocalStorageManager() # defaults to root output, intermediate, knowledge
storage_provider = StorageAPIProvider(storage_manager)
app.include_router(storage_provider.router)

# 2. Setup Bot
# Mocking a task_config object that has the Enums as attributes
class TaskConfig:
    pass
task_config = TaskConfig()
task_config.ApplicationType = ApplicationType
task_config.UtilsType = UtilsType
task_config.ExecutionTarget = ExecutionTarget

bot_manager = SimpleBotManager()
bot_provider = BotAPIProvider(bot_manager, task_config)
app.include_router(bot_provider.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
