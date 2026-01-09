# Bot Module - Client Documentation

> **💡 Quick Start:** Use **[API Factory](api-factory.md)** for one-line setup! This guide shows manual implementation for advanced customization.

The Bot module is Pravaha's core execution engine for running synchronous utilities and streaming applications.

## Overview

The Bot module provides:
- **Synchronous execution** for utilities (calculators, validators, etc.)
- **Streaming execution** for LLM applications (chat, generation, etc.)
- **Schema introspection** for input/output validation
- **Config retrieval** for YAML configurations

## Protocol Definition

Your bot manager must implement `BotManagerProtocol`:

```python
from typing import Protocol, Optional, List, Dict, Any, Union, Iterable, AsyncIterable
from enum import Enum

class BotManagerProtocol(Protocol[UT, AT]):
    def run(self, utility_task: UT, inputs: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Execute synchronous utility task."""
        ...
    
    def stream_run(self, application_task: AT, inputs: Optional[List[Dict[str, Any]]] = None, llm_config: Optional[Any] = None) -> Union[Iterable[str], AsyncIterable[str]]:
        """Execute streaming application task."""
        ...
    
    def get_input_model(self, task: Union[UT, AT]) -> Optional[Any]:
        """Returns the Pydantic model for the task's input."""
        ...
    
    def get_output_model(self, task: Union[UT, AT]) -> Optional[Any]:
        """Returns the Pydantic model for the task's output."""
        ...
    
    def get_config(self, task: Union[UT, AT]) -> Optional[Dict[str, Any]]:
        """Returns the YAML configuration for the task as a dictionary."""
        ...
```

## Implementation Guide

### Step 1: Define Task Enums

```python
from enum import Enum

class UtilsType(str, Enum):
    CALCULATOR = "calculator"
    VALIDATOR = "validator"

class ApplicationType(str, Enum):
    CHAT_BOT = "chat_bot"
    TEXT_GENERATOR = "text_generator"
```

### Step 2: Implement Bot Manager

```python
from pydantic import BaseModel, Field
import yaml

class CalculatorInput(BaseModel):
    operation: str = Field(..., pattern="^(add|subtract|multiply|divide)$")
    a: float
    b: float

class MyBotManager:
    def __init__(self):
        # Input/output model registry
        self.input_models = {
            UtilsType.CALCULATOR: CalculatorInput
        }
        self.output_models = {}
        
        # Config path registry
        self.config_paths = {
            ApplicationType.CHAT_BOT: "config/chat_config.yaml"
        }
    
    def run(self, utility_task, inputs=None):
        """Execute synchronous utility."""
        if utility_task == UtilsType.CALCULATOR:
            op = inputs[0]['operation']
            a = inputs[0]['a']
            b = inputs[0]['b']
            
            if op == 'add':
                return {'result': a + b}
            elif op == 'multiply':
                return {'result': a * b}
        
        raise ValueError(f"Unknown task: {utility_task}")
    
    def stream_run(self, application_task, inputs=None, llm_config=None):
        """Execute streaming application."""
        if application_task == ApplicationType.CHAT_BOT:
            # Your LLM integration here
            yield "Hello, "
            yield "I'm "
            yield "a chatbot!"
        else:
            yield f"Unknown application: {application_task}"
    
    def get_input_model(self, task):
        return self.input_models.get(task)
    
    def get_output_model(self, task):
        return self.output_models.get(task)
    
    def get_config(self, task):
        """Get YAML config for task."""
        config_path = self.config_paths.get(task)
        if not config_path:
            return None
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return None
```

### Step 3: Create Task Config

```python
class TaskConfig:
    pass

task_config = TaskConfig()
task_config.UtilsType = UtilsType
task_config.ApplicationType = ApplicationType
task_config.ExecutionTarget = ExecutionTarget  # Define this enum
```

### Step 4: Wire Up API

```python
from pravaha.domain.bot.provider.bot_api_provider import BotAPIProvider
from fastapi import FastAPI

app = FastAPI()
bot_manager = MyBotManager()

provider = BotAPIProvider(bot_manager, task_config)
app.include_router(provider.router, prefix="/api")
```

## API Endpoints

The `BotAPIProvider` creates these endpoints:

### POST `/api/run/utility`
Execute synchronous utility task.

**Request:**
```json
{
  "task_name": "calculator",
  "inputs": [
    {
      "operation": "add",
      "a": 5,
      "b": 3
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "result": {"result": 8}
}
```

### POST `/api/run/application/stream`
Execute streaming application with SSE.

**Request:**
```json
{
  "task_name": "chat_bot",
  "inputs": [
    {
      "message": "Hello!"
    }
  ],
  "llm_config_override": {
    "model_config": {
      "model": "gpt-4",
      "api_key": "your-key"
    },
    "llm_parameters": {
      "temperature": 0.7
    }
  }
}
```

**Response:** Server-Sent Events stream
```
data: Hello, 

data: I'm 

data: a chatbot!

data: [DONE]
```

### GET `/api/enums/util-types`
Get available utility task types.

**Response:**
```json
["calculator", "validator"]
```

### GET `/api/enums/application-types`
Get available application task types.

**Response:**
```json
["chat_bot", "text_generator"]
```

### GET `/api/protocol/schema/input/{task_name}`
Get Pydantic JSON schema for task input.

**Example:** `GET /api/protocol/schema/input/calculator`

**Response:**
```json
{
  "type": "object",
  "properties": {
    "operation": {"type": "string", "pattern": "^(add|subtract|multiply|divide)$"},
    "a": {"type": "number"},
    "b": {"type": "number"}
  },
  "required": ["operation", "a", "b"]
}
```

### GET `/api/protocol/schema/output/{task_name}`
Get Pydantic JSON schema for task output.

### GET `/api/protocol/config/{task_name}`
Get YAML configuration as JSON.

**Example:** `GET /api/protocol/config/chat_bot`

**Response:** Parsed YAML config as JSON

## Best Practices

1. **Registry Pattern**: Use dictionaries to map tasks to models/configs
2. **Error Handling**: Raise `ValueError` for unknown tasks
3. **Type Safety**: Define Pydantic models for inputs/outputs
4. **Config Management**: Store YAML configs in predictable locations
5. **LLM Config Override**: Support `llm_config_override` parameter for runtime config

## Example: Complete Bot Manager

See `src/nikhil/pravaha_example/service/server.py` for a complete working example.

## Testing Your Implementation

```bash
# Start server
uvicorn main:app --reload

# Test utility
curl -X POST http://localhost:8000/api/run/utility \
  -H "Content-Type: application/json" \
  -d '{"task_name": "calculator", "inputs": [{"operation": "add", "a": 5, "b": 3}]}'

# Test streaming
curl -N http://localhost:8000/api/run/application/stream \
  -H "Content-Type: application/json" \
  -d '{"task_name": "chat_bot"}'

# Get schemas
curl http://localhost:8000/api/protocol/schema/input/calculator
curl http://localhost:8000/api/protocol/config/chat_bot
```
