# Pravaha - FastAPI Protocol Library for LLM/Agent Applications

**Version:** 1.0.0

Pravaha is a lightweight FastAPI library that provides a protocol-based architecture for building APIs that handle both synchronous non-blocking tasks and asynchronous streaming operations for LLM and agent applications.

---

## Features

✅ **Protocol-Based Design** - Define contracts using Python Protocols for flexible implementations  
✅ **Dual Execution Modes** - Support for both synchronous utilities and streaming applications  
✅ **SSE Streaming** - Server-Sent Events (SSE) for real-time LLM response streaming  
✅ **Type-Safe** - Leverages Pydantic and Python type hints for robust validation  
✅ **Framework Agnostic** - Works with any bot/agent implementation that satisfies the protocols  
✅ **Auto-Sync Conversion** - Automatically converts synchronous iterables to async for streaming

---

## Architecture Overview

Pravaha follows Clean Architecture principles with clear separation of concerns:

```
src/nikhil/pravaha/
└── domain/
    └── api/
        ├── factory/              # API factory for creating FastAPI routers
        │   └── api_factory.py    # Creates API endpoints from protocols
        ├── protocol/             # Protocol definitions (contracts)
        │   ├── bot_manager_protocol.py   # Bot manager interface
        │   └── task_config_protocol.py   # Task configuration interface
        └── streaming/            # Streaming utilities
            └── sync_to_async.py  # Convert sync iterables to async
```

### Key Components

1. **Protocols** - Define the interface contracts:
   - `BotManagerProtocol`: Interface for bot/agent execution
   - `TaskConfigProtocol`: Interface for task configuration with Enums

2. **API Factory** - Generates FastAPI routers:
   - `create_bot_api()`: Creates API router with endpoints
   - `create_fastapi_app()`: Creates full FastAPI application

3. **Streaming** - Handles async/sync conversion:
   - `stream_from_sync_iterable()`: Converts sync generators to async

---

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd Pravaha

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell
.\\venv\\Scripts\\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Install in editable mode
pip install -e .
```

### Dependencies

Pravaha has minimal dependencies:
- **FastAPI** (0.121.3) - Web framework
- **sse-starlette** (3.0.3) - Server-Sent Events support
- **PyYAML** (6.0.2) - Configuration file parsing

See [`pyproject.toml`](file:///home/dell/PycharmProjects/Pravaha/pyproject.toml) for the complete dependency list.

---

## Quick Start

### 1. Explore the Example Package
We have provided a comprehensive example in `src/nikhil/pravaha_example`.
It includes:
- **MathBot**: A streaming math assistant.
- **CalculatorTool**: A simple calculator utility.
- **Server**: A FastAPI app connecting them.

Run it with:
```bash
uvicorn pravaha_example.service.server:app --reload
```

### 2. Basic Implementation Steps

**a. Define Enums**
```python
from enum import Enum
class UtilsType(str, Enum):
    CALCULATOR = "calculator"
class ApplicationType(str, Enum):
    CHAT = "chat"
class ExecutionTarget(str, Enum):
    LOCAL = "local"
```

**b. Implement Bot Manager**
```python
from pravaha.domain.bot.protocol.bot_manager_protocol import BotManagerProtocol

class MyBotManager:
    def run(self, utility_task, inputs=None):
        return "Executed"
    
    async def stream_run(self, application_task, inputs=None):
        yield "Hello from stream"
```

**c. Create Server**
```python
from pravaha.domain.bot.provider.bot_api_provider import BotAPIProvider
from fastapi import FastAPI

# ... setup config and manager ...
bot_provider = BotAPIProvider(bot_manager, task_config)
app = FastAPI()
app.include_router(bot_provider.router)
```


### 5. Use the API

**Health Check:**
```bash
curl http://localhost:8000/health
# Response: {"status": "ok"}
```

**Run Utility Task (Synchronous):**
```bash
curl -X POST http://localhost:8000/api/run/utility \
  -H "Content-Type: application/json" \
  -d '{"task_name": "validate_input"}'

# Response: {"status": "success", "result": {"status": "valid", "message": "Input validated"}}
```

**Stream Application Task (SSE):**
```bash
curl -N http://localhost:8000/api/run/application/stream \
  -H "Content-Type: application/json" \
  -d '{"task_name": "chat"}'

# Response (SSE stream):
# data: Hello
# 
# data:  
# 
# data: from
# 
# data:  
# 
# data: LLM
# 
# data: [DONE]
```

**Get Available Enums:**
```bash
# Get utility types
curl http://localhost:8000/api/enums/util-types

# Get application types
curl http://localhost:8000/api/enums/application-types

# Get execution targets
curl http://localhost:8000/api/enums/execution-targets
```

---

## API Endpoints

Pravaha automatically creates the following endpoints:

### POST `/run/utility`
Execute synchronous utility tasks.

**Request Body:**
```json
{
  "task_name": "UtilsType enum value"
}
```

**Response:**
```json
{
  "status": "success",
  "result": <any>
}
```

### POST `/run/application/stream`
Execute streaming application tasks with SSE.

**Request Body:**
```json
{
  "task_name": "ApplicationType enum value"
}
```

**Response:** Server-Sent Events (SSE) stream

### GET `/enums/util-types`
Get all available utility task types.

### GET `/enums/application-types`
Get all available application task types.

### GET `/enums/execution-targets`
Get all available execution targets.

### GET `/health`
Health check endpoint.

---

## Protocol Definitions

### BotManagerProtocol

Defines the interface your bot manager must implement:

```python
class BotManagerProtocol(Protocol[UT, AT]):
    def run(self, utility_task: UT) -> Any:
        """Synchronous execution of a utility task"""
        ...

    def stream_run(self, application_task: AT) -> Union[Iterable[str], AsyncIterable[str]]:
        """Streamable execution of an application task"""
        ...
```

- **`UT`**: Utility Task Enum type
- **`AT`**: Application Task Enum type
- **`run()`**: For non-streaming, synchronous operations
- **`stream_run()`**: For streaming operations (can return sync or async iterables)

### TaskConfigProtocol

Defines the configuration structure:

```python
class TaskConfigProtocol(Protocol):
    UtilsType: Type[Enum]        # Enum for utility tasks
    ApplicationType: Type[Enum]   # Enum for streaming tasks
    ExecutionTarget: Type[Enum]   # Enum for execution targets
```

---

## Advanced Usage

### Async Stream from Sync Generator

Pravaha automatically handles conversion of synchronous generators to async streams using [`stream_from_sync_iterable()`](file:///home/dell/PycharmProjects/Pravaha/src/nikhil/pravaha/domain/api/streaming/sync_to_async.py):

```python
def my_sync_generator():
    """Your existing sync generator"""
    for i in range(10):
        yield f"Item {i}"

# Pravaha will automatically convert this to async
# No changes needed in your bot manager!
```

### Custom Route Prefix

```python
from nikhil.pravaha.domain.api.factory.api_factory import create_bot_api
from fastapi import FastAPI

app = FastAPI()

# Create router with custom prefix
router = create_bot_api(bot_manager, task_config, route_prefix="/custom/v1")
app.include_router(router)
```

### Error Handling

Pravaha automatically handles exceptions and returns HTTP 500 with error details:

```python
def run(self, utility_task: UtilsType):
    if utility_task == UtilsType.INVALID:
        raise ValueError("Invalid task type")
    # This will be caught and returned as:
    # {"detail": "ValueError: Invalid task type"}
```

---

## Design Principles

Pravaha follows these architectural principles:

1. **Protocol-Based** - Uses Python Protocols for structural typing
2. **Dependency Inversion** - High-level API factory depends on abstractions (protocols)
3. **Separation of Concerns** - Clear separation between domain logic and API layer
4. **Framework Agnostic** - Your bot implementation doesn't depend on FastAPI
5. **Type Safety** - Leverages Python type hints and Pydantic validation

---

## Development

### Project Structure

```
Pravaha/
├── docs/                      # Documentation
│   ├── Architecture.md        # Architecture and coding standards
│   ├── DEPENDENCIES.md        # Dependency management
│   └── VIRTUAL_ENV_USAGE.md   # Virtual environment guide
├── src/
│   └── nikhil/pravaha/
│       └── domain/api/        # Core API domain
├── pyproject.toml             # Project configuration
└── requirements.txt           # Development dependencies
```

### Virtual Environment

See [VIRTUAL_ENV_USAGE.md](file:///home/dell/PycharmProjects/Pravaha/docs/VIRTUAL_ENV_USAGE.md) for detailed virtual environment setup instructions.

### Documentation

- **[Architecture.md](file:///home/dell/PycharmProjects/Pravaha/docs/Architecture.md)** - Coding standards and architectural principles
- **[DEPENDENCIES.md](file:///home/dell/PycharmProjects/Pravaha/docs/DEPENDENCIES.md)** - Dependency management and migration roadmap

### Testing

Run unit tests and check coverage using the configured tools:

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\Activate.ps1  # Windows

# Run tests
pytest

# Run tests with coverage report
pytest --cov=src/nikhil/pravaha --cov-report=term-missing
```

---

## Use Cases

Pravaha is ideal for:

- **LLM Applications** - Chat interfaces, text generation, summarization
- **Agent Systems** - Multi-step agent workflows with streaming responses
- **CrewAI Integration** - FastAPI wrapper for CrewAI agents
- **Microservices** - Protocol-based microservice APIs
- **Bot Frameworks** - Generic bot/agent API layer

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Follow the coding standards in [Architecture.md](file:///home/dell/PycharmProjects/Pravaha/docs/Architecture.md)
2. Use virtual environments for development
3. Maintain protocol-based design
4. Add type hints to all functions
5. Write comprehensive docstrings

---

## License

[Specify your license here]

---

## Contact

[Add contact information or links]

---

## Changelog

### Version 1.0.0
- Initial release
- Protocol-based API factory
- SSE streaming support
- Sync to async conversion for streaming
- Full type safety with Pydantic
