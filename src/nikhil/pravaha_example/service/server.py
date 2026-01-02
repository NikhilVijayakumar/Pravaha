from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, Type, Any

from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.bot.provider.bot_api_provider import BotAPIProvider
from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager

# Import example components
from pravaha_example.config.settings import ApplicationType, UtilsType, ExecutionTarget
from pravaha_example.domain.calculator_tool import CalculatorTool
from pravaha_example.domain.math_bot import MathBot

# Define a simple BotManager stub to wire things up
# In a real app, this might be more complex or imported from domain/bot/manager
# Sample Models
class CalculatorInput(BaseModel):
    operation: str = Field(..., description="The operation to perform: add, multiply", pattern="^(add|multiply)$")
    a: float = Field(..., description="First operand")
    b: float = Field(..., description="Second operand")

class MathBotInput(BaseModel):
    expression: str = Field(..., description="Mathematical expression to evaluate")

class GenericOutput(BaseModel):
    result: Any = Field(..., description="Result of the operation")

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
        
        self.input_models = {
            UtilsType.CALCULATOR: CalculatorInput,
            ApplicationType.MATH_ASSISTANT: MathBotInput
        }
        
        self.output_models = {
            UtilsType.CALCULATOR: GenericOutput,
            ApplicationType.MATH_ASSISTANT: GenericOutput
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

    def get_input_model(self, task) -> Optional[Type[BaseModel]]:
        # Handle string vs Enum lookup if needed, similar to run()
        # But assumes provider passes Enum if resolved
        if task in self.input_models:
            return self.input_models[task]
        # Fallback for string lookup
        for k, v in self.input_models.items():
            if k.value == task:
                return v
        return None

    def get_output_model(self, task) -> Optional[Type[BaseModel]]:
         if task in self.output_models:
            return self.output_models[task]
         for k, v in self.output_models.items():
            if k.value == task:
                return v
         return None

# Create App


# 1. Setup Storage
storage_manager = LocalStorageManager() # defaults to root output, intermediate, knowledge
storage_provider = StorageAPIProvider(storage_manager)


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


app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager,
    title="Pravaha Mock API"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
