# API Factory Module - Client Documentation

The API Factory is Pravaha's **one-line solution** for creating a complete FastAPI application with all modules integrated and ready to use.

## Overview

Instead of manually wiring up each module (Bot, LLM, Storage, Workflow), use `create_fastapi_app()` to get a production-ready API in one function call.

**What it does:**
- ✅ Creates FastAPI app
- ✅ Sets up CORS middleware
- ✅ Initializes all 4 modules (Bot, LLM, Storage, Workflow)
- ✅ Mounts all API routers with consistent prefixing
- ✅ Adds health check endpoint
- ✅ Configures LLM config manager
- ✅ Sets up workflow persistence

## Quick Start

### Minimal Example

```python
from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager

# 1. Create your bot manager
class MyBotManager:
    def run(self, utility_task, inputs=None):
        return {"result": "success"}
    
    def stream_run(self, application_task, inputs=None, llm_config=None):
        yield "Hello from stream!"
    
    def get_input_model(self, task):
        return None
    
    def get_output_model(self, task):
        return None
    
    def get_config(self, task):
        return None

# 2. Define task config
from enum import Enum

class UtilsType(str, Enum):
    MY_UTIL = "my_util"

class ApplicationType(str, Enum):
    MY_APP = "my_app"

class ExecutionTarget(str, Enum):
    LOCAL = "local"

class TaskConfig:
    pass

task_config = Task Config()
task_config.UtilsType = UtilsType
task_config.ApplicationType = ApplicationType
task_config.ExecutionTarget = ExecutionTarget

# 3. ONE LINE TO CREATE EVERYTHING!
bot_manager = MyBotManager()
storage_manager = LocalStorageManager()

app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager,
    title="My Pravaha App"
)

# That's it! Your API is ready with all 23 endpoints.
# Run: uvicorn main:app --reload
```

## Function Signature

```python
def create_fastapi_app(
    bot_manager,           # Your BotManager implementation
    task_config,           # Task configuration with enums
    storage_manager,       # LocalStorageManager instance
    prefix="api",          # API route prefix (default: "api")
    title="Akashvani Unified API",  # FastAPI app title
    llm_config_path: Optional[str] = None  # Path to llm_config.yaml
) -> FastAPI:
    """Create a complete FastAPI app with all Pravaha modules."""
    ...
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `bot_manager` | BotManagerProtocol | ✅ Yes | - | Your bot manager implementation |
| `task_config` | TaskConfigProtocol | ✅ Yes | - | Object with UtilsType, ApplicationType, ExecutionTarget enums |
| `storage_manager` | LocalStorageManager | ✅ Yes | - | Storage manager for file organization |
| `prefix` | str | ❌ No | `"api"` | URL prefix for all API routes |
| `title` | str | ❌ No | `"Akashvani Unified API"` | FastAPI application title (shown in docs) |
| `llm_config_path` | str | ❌ No | `None` | Path to LLM config YAML file |

## What Gets Created

When you call `create_fastapi_app()`, it automatically sets up:

### 1. Bot Module (8 endpoints)
```
POST   /api/run/utility
POST   /api/run/application/stream
GET    /api/enums/util-types
GET    /api/enums/application-types
GET    /api/enums/execution-targets
GET    /api/protocol/schema/input/{task_name}
GET    /api/protocol/schema/output/{task_name}
GET    /api/protocol/config/{task_name}
```

### 2. LLM Module (2 endpoints)
```
GET    /api/llm/configs
GET    /api/llm/config/{mode}
```

### 3. Storage Module (4 endpoints)
```
GET    /api/storage/{category}/browse
GET    /api/storage/{category}/read
POST   /api/storage/config
GET    /api/storage/config
```

### 4. Workflow Module (9 endpoints)
```
POST   /api/workflow/create
GET    /api/workflow/list
GET    /api/workflow/{id}
POST   /api/workflow/update
POST   /api/workflow/rename
DELETE /api/workflow/{id}
POST   /api/workflow/run
GET    /api/workflow/run/{run_id}
GET    /api/workflow/runs
```

### 5. Utility Endpoints
```
GET    /health
```

**Total: 24 endpoints created automatically!**

## Complete Example with All Features

```python
from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from enum import Enum
from pydantic import BaseModel
import yaml

# Define enums
class UtilsType(str, Enum):
    CALCULATOR = "calculator"

class ApplicationType(str, Enum):
    CHAT = "chat"

class ExecutionTarget(str, Enum):
    LOCAL = "local"

# Define models
class CalculatorInput(BaseModel):
    a: float
    b: float
    operation: str

# Implement bot manager
class MyBotManager:
    def __init__(self):
        self.input_models = {
            UtilsType.CALCULATOR: CalculatorInput
        }
        self.config_paths = {
            ApplicationType.CHAT: "config/chat_config.yaml"
        }
    
    def run(self, utility_task, inputs=None):
        if utility_task == UtilsType.CALCULATOR:
            a = inputs[0]['a']
            b = inputs[0]['b']
            op = inputs[0]['operation']
            
            if op == 'add':
                return {'result': a + b}
            elif op == 'multiply':
                return {'result': a * b}
        
        raise ValueError(f"Unknown task: {utility_task}")
    
    def stream_run(self, application_task, inputs=None, llm_config=None):
        if application_task == ApplicationType.CHAT:
            # Your LLM integration here
            yield "Response "
            yield "from "
            yield "LLM!"
    
    def get_input_model(self, task):
        return self.input_models.get(task)
    
    def get_output_model(self, task):
        return None
    
    def get_config(self, task):
        config_path = self.config_paths.get(task)
        if config_path:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return None

# Create task config
class TaskConfig:
    pass

task_config = TaskConfig()
task_config.UtilsType = UtilsType
task_config.ApplicationType = ApplicationType
task_config.ExecutionTarget = ExecutionTarget

# Create storage manager
storage_manager = LocalStorageManager(
    output_path="output",
    intermediate_path="intermediate",
    knowledge_path="knowledge"
)

# CREATE THE APP
app = create_fastapi_app(
    bot_manager=MyBotManager(),
    task_config=task_config,
    storage_manager=storage_manager,
    prefix="api",
    title="My Application API",
    llm_config_path="llm_config.yaml"  # Optional
)

# Run with: uvicorn main:app --reload
```

## Advanced Configuration

### Custom URL Prefix

```python
app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager,
    prefix="v1"  # URLs become /v1/run/utility, /v1/storage/..., etc.
)
```

### Multiple Instances

```python
# Create multiple apps with different configs
app_v1 = create_fastapi_app(..., prefix="v1", title="API v1")
app_v2 = create_fastapi_app(..., prefix="v2", title="API v2")
```

### Without LLM Config

```python
# LLM module still available, but no pre-configured models
app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager
    # llm_config_path not provided
)
```

## Automatic Features

### CORS Middleware
CORS is automatically configured to allow all origins (development friendly):
```python
allow_origins=["*"]
allow_methods=["*"]
allow_headers=["*"]
```

**Production**: Modify the app after creation:
```python
app = create_fastapi_app(...)

# Update CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)
```

### Workflow Persistence
Workflows automatically saved to:
- `./data/workflows.json` - Workflow definitions
- `./data/runs.json` - Workflow execution history

### Health Check
```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

## Testing Your App

```bash
# Start server
uvicorn main:app --reload

# Access Swagger UI
open http://localhost:8000/docs

# Test Bot endpoint
curl -X POST http://localhost:8000/api/run/utility \
  -H "Content-Type: application/json" \
  -d '{"task_name": "calculator", "inputs": [{"a": 5, "b": 3, "operation": "add"}]}'

# Test Storage
curl http://localhost:8000/api/storage/output/browse

# Test Workflow
curl http://localhost:8000/api/workflow/list

# Test LLM
curl http://localhost:8000/api/llm/configs
```

## Under the Hood

`create_fastapi_app()` performs these steps:

1. **Creates FastAPI app** with the specified title
2. **Adds CORS middleware** for cross-origin requests
3. **Initializes LLM Config Manager** (if path provided)
4. **Creates Storage resolvers** (path, version)
5. **Sets up Workflow components**:
   - JSON repositories for persistence
   - Task executor (bridges to your bot manager)
   - Workflow engine and service
6. **Creates API providers** for each module
7. **Mounts routers** with consistent `/api` prefix
8. **Adds health check** endpoint

## Comparison: Manual vs API Factory

### Manual Approach (Not Recommended)
```python
from fastapi import FastAPI

app = FastAPI()

# Manually set up Bot
bot_provider = BotAPIProvider(bot_manager, task_config)
app.include_router(bot_provider.router, prefix="/api")

# Manually set up Storage
storage_provider = StorageAPIProvider(storage_manager, ...)
app.include_router(storage_provider.router, prefix="/api")

# Manually set up Workflow
workflow_repo = JsonWorkflowRepository("data/workflows.json")
run_repo = JsonRunRepository("data/runs.json")
# ... 10 more lines of setup ...

# Manually set up LLM
llm_config_manager = LLMConfigManager(...)
# ... more setup ...

# Add CORS
app.add_middleware(CORSMiddleware, ...)

# Add health check
@app.get("/health")
def health():
    return {"status": "ok"}
```

### API Factory Approach (Recommended)
```python
app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager
)
```

**Result:** Same functionality, **90% less code!**

## Best Practices

1. **Always Use API Factory**: Unless you need custom routing logic
2. **Configure LLM Path**: Provide `llm_config_path` for LLM features
3. **Use Defaults**: Default prefix and title work well for most cases
4. **Test Immediately**: Check `/docs` endpoint to verify all routes
5. **Override CORS in Production**: Update CORS settings before deploying

## Common Issues

### Issue: Workflow endpoints return 500
**Solution:** Ensure `./data/` directory exists or is writable
```python
import os
os.makedirs("data", exist_ok=True)
```

### Issue: LLM endpoints return empty
**Solution:** Provide `llm_config_path` parameter
```python
app = create_fastapi_app(..., llm_config_path="llm_config.yaml")
```

### Issue: Storage paths not found
**Solution:** Initialize LocalStorageManager with correct paths
```python
storage_manager = LocalStorageManager(
    output_path="./output",
    intermediate_path="./intermediate",
    knowledge_path="./knowledge"
)
```

## Summary

The API Factory is your **one-stop shop** for creating Pravaha applications:

✅ **One Function Call** - `create_fastapi_app()`  
✅ **All 4 Modules** - Bot, LLM, Storage, Workflow  
✅ **24 Endpoints** - Automatically configured  
✅ **Production Ready** - CORS, health check, error handling  
✅ **Zero Boilerplate** - Focus on your business logic  

**Start with API Factory, customize later if needed!**
