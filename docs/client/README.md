# Pravaha Client Documentation

Welcome to the Pravaha client documentation! This guide will help you integrate Pravaha into your application as a dependency library.

## What is Pravaha?

Pravaha is a protocol-based FastAPI library for building LLM/Agent applications with four core modules:

- **Bot** - Execute synchronous utilities and streaming applications
- **LLM** - Manage LLM configurations and providers
- **Storage** - Organize outputs, intermediate results, and knowledge
- **Workflow** - Define and execute multi-step workflows

## Quick Start

### Installation

```bash
pip install pravaha
```

Or from source:
```bash
git clone <repository-url>
cd Pravaha
pip install -e .
```

### Create Your App (Recommended: API Factory)

The **easiest way** to use Pravaha is with the API Factory - it sets up everything in one line!

```python
from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from enum import Enum

# 1. Define task enums
class UtilsType(str, Enum):
    CALCULATOR = "calculator"

class ApplicationType(str, Enum):
    CHAT = "chat"

class ExecutionTarget(str, Enum):
    LOCAL = "local"

# 2. Implement bot manager
class MyBotManager:
    def run(self, utility_task, inputs=None):
        return {"result": "Hello from utility!"}
    
    def stream_run(self, application_task, inputs=None, llm_config=None):
        yield "Hello "
        yield "from "
        yield "stream!"
    
    def get_input_model(self, task):
        return None
    
    def get_output_model(self, task):
        return None
    
    def get_config(self, task):
        return None

# 3. Configure task config
class TaskConfig:
    pass

task_config = TaskConfig()
task_config.UtilsType = UtilsType
task_config.ApplicationType = ApplicationType
task_config.ExecutionTarget = ExecutionTarget

# 4. CREATE COMPLETE APP IN ONE LINE! 🚀
app = create_fastapi_app(
    bot_manager=MyBotManager(),
    task_config=task_config,
    storage_manager=LocalStorageManager(),
    title="My Pravaha App"
)

# That's it! You get 24 endpoints across 4 modules automatically.
# Run: uvicorn main:app --reload
```

**What you get:**
- ✅ Bot module (8 endpoints) - Task execution
- ✅ LLM module (2 endpoints) - LLM config management
- ✅ Storage module (4 endpoints) - File organization
- ✅ Workflow module (9 endpoints) - Multi-step workflows
- ✅ Health check endpoint
- ✅ CORS configured
- ✅ Swagger UI at `/docs`

### Test Your API

```bash
# Start the server
uvicorn main:app --reload

# Open Swagger UI
open http://localhost:8000/docs

# Test an endpoint
curl -X POST http://localhost:8000/api/run/utility \
  -H "Content-Type: application/json" \
  -d '{"task_name": "calculator"}'
```

## Next Steps

**Recommended Path:**
1. **[API Factory](api-factory.md)** - The easiest way! One function = complete app
2. Pick the modules you need to customize:
   - **[Bot Module](bot-module.md)** - Customize task execution
   - **[LLM Module](llm-module.md)** - Configure LLM providers
   - **[Storage Module](storage-module.md)** - Organize file storage
   - **[Workflow Module](workflow-module.md)** - Build multi-step workflows

## API Documentation

Once your app is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Architecture

Pravaha follows **protocol-based design**:

```
Your Application
   ↓
Pravaha Protocols (Interfaces)
   ↓
Your Implementations
   ↓
Pravaha API Providers (FastAPI Routers)
   ↓
REST API Endpoints
```

This means:
1. You implement the protocols (interfaces)
2. Pravaha generates the API endpoints automatically
3. Your code stays framework-agnostic

## Support

- **Examples**: See `src/nikhil/pravaha_example/`
- **Architecture**: See `docs/Architecture.md`
- **Issues**: Report bugs and feature requests in your repository's issue tracker
