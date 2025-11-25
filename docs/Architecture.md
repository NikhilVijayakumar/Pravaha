# Pravaha Library - Coding Constitution & Standards

**Role:** You are a Senior Architect working on `Pravaha`, a FastAPI protocol library for LLM/agent applications.  
**Goal:** Maintain strict adherence to Clean Architecture, SOLID principles, and Protocol-based design while ensuring flexibility for multiple bot/agent implementations.

---

## 1. Architectural Boundaries (The "Law")

This project follows **Clean Architecture**. You must strictly adhere to the Dependency Rule:

*   **Inner Layers (Domain)** must NEVER depend on **Outer Layers (Infrastructure/API)**.
*   **Domain (`src/nikhil/pravaha/domain`)**: Pure Python protocols and domain logic. NO framework dependencies.
*   **Protocol Interfaces (`domain/api/protocol`)**: Abstract contracts only. NO implementation details.
*   **API Factory (`domain/api/factory`)**: Creates FastAPI routers from protocols.
*   **Streaming (`domain/api/streaming`)**: Utility functions for async/sync conversion.

**Layer Dependencies (Inner → Outer):**
```
Protocols (Domain) ← API Factory ← FastAPI Application (Infrastructure)
```

---

## 2. Interface Design: Protocol-First Architecture

**Critical Distinction:** Pravaha uses **Protocol** for all external contracts.

### When to Use `Protocol`

**Purpose:** Structural typing (duck typing) for **all external boundaries**.

**Use for:**
- Client-facing interfaces (`BotManagerProtocol`, `TaskConfigProtocol`)
- Plugin/extension points where clients provide implementations
- Public API contracts where you want flexibility without inheritance

**Example:**
```python
from typing import Protocol, Any, Union, Iterable, AsyncIterable
from enum import Enum

class BotManagerProtocol(Protocol[UT, AT]):
    def run(self, utility_task: UT) -> Any:
        """Client implements this without inheriting"""
        ...
    
    def stream_run(self, application_task: AT) -> Union[Iterable[str], AsyncIterable[str]]:
        """Supports both sync and async streaming"""
        ...
```

**Rule of Thumb:**
- **All external boundaries** → `Protocol`
- **No ABC required** for this library (all contracts are external)

---

## 3. Protocol-Based Design Philosophy

**Core Principle:** Pravaha does NOT dictate implementation. It defines contracts.

### What Pravaha Provides
1. **Protocols** - Interface definitions
2. **API Factory** - Converts protocol implementations to FastAPI endpoints
3. **Utilities** - Helper functions (async conversion)

### What Clients Provide
1. **Bot Manager** - Implementation of `BotManagerProtocol`
2. **Task Config** - Implementation of `TaskConfigProtocol`
3. **Business Logic** - All domain-specific logic

**Example Client Implementation:**
```python
class MyBotManager:
    """Client implementation - no inheritance required"""
    
    def run(self, utility_task: UtilsType) -> dict:
        # Client's logic here
        return {"result": "processed"}
    
    def stream_run(self, application_task: ApplicationType):
        # Client's streaming logic
        for chunk in self.process_stream(application_task):
            yield chunk
```

---

## 4. SOLID Principles

*   **SRP (Single Responsibility):** 
    - `BotManagerProtocol`: Defines execution contract
    - `TaskConfigProtocol`: Defines configuration contract
    - `create_bot_api()`: Creates API router
    - `create_fastapi_app()`: Creates FastAPI application

*   **OCP (Open/Closed):** 
    - New bot implementations can be added without changing Pravaha
    - Protocol-based design allows extensions

*   **LSP (Liskov Substitution):** 
    - Any `BotManagerProtocol` implementation must be swappable
    - Sync and async streams are handled transparently

*   **ISP (Interface Segregation):** 
    - `BotManagerProtocol` has only essential methods
    - `TaskConfigProtocol` requires only Enum definitions

*   **DIP (Dependency Inversion):** 
    - API factory depends on `BotManagerProtocol`, not concrete implementations
    - Clients depend on protocols, not framework internals

---

## 5. Type Safety Standards

**Critical Rule:** All public functions must have complete type hints.

### Required Type Hints

1. **Function Parameters and Returns:**
    ```python
    def create_bot_api(
        bot_manager: BotManagerProtocol,
        task_config: TaskConfigProtocol,
        *,
        route_prefix: str = "",
    ) -> APIRouter:
        """All types explicitly defined"""
        ...
    ```

2. **Pydantic Models for Request/Response:**
    ```python
    class UtilityRequest(BaseModel):
        task_name: UtilsType  # Enum type from client
    
    class ApplicationRequest(BaseModel):
        task_name: ApplicationType
    ```

3. **Generic Protocols:**
    ```python
    from typing import Protocol, TypeVar
    from enum import Enum
    
    UT = TypeVar('UT', bound=Enum)  # Utility Task Type
    AT = TypeVar('AT', bound=Enum)  # Application Task Type
    
    class BotManagerProtocol(Protocol[UT, AT]):
        ...
    ```

---

## 6. Async/Await Guidelines

**Current State:** Async is used throughout the API layer.

**Rules:**

1. **Required for:**
    - All FastAPI endpoints (async def)
    - Streaming operations (`EventSourceResponse`)
    - Stream conversion utilities

2. **Flexible for Clients:**
    - Clients can provide sync or async `stream_run()`
    - Pravaha handles conversion automatically via `stream_from_sync_iterable()`

3. **Pattern:**
    ```python
    async def run_application_stream(req: ApplicationRequest):
        stream = bot_manager.stream_run(req.task_name)
        
        async def event_generator():
            # Handle both sync and async streams
            if inspect.isasyncgen(stream):
                async for chunk in stream:
                    yield _sse_format(str(chunk))
            elif hasattr(stream, "__iter__"):
                async for chunk in stream_from_sync_iterable(stream):
                    yield _sse_format(str(chunk))
    ```

---

## 7. Exception Handling Strategy

**Standard:**

1. **All Exceptions Caught at API Layer:**
    ```python
    @router.post("/run/utility")
    async def run_utility(req: UtilityRequest):
        try:
            result = bot_manager.run(req.task_name)
            return {"status": "success", "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    ```

2. **Client Exceptions Preserved:**
    - Exception type name is included in error response
    - Original error message is preserved
    - HTTP 500 used for all server errors

3. **SSE Stream Error Handling:**
    ```python
    # Errors before streaming starts → HTTP 500
    # Errors during streaming → Included in event stream
    ```

---

## 8. Streaming Architecture

**Core Pattern:** Support both sync and async streaming transparently.

### Client Streaming Options

**Option 1: Synchronous Generator**
```python
def stream_run(self, task: ApplicationType):
    for chunk in self.process():
        yield chunk
```

**Option 2: Asynchronous Generator**
```python
async def stream_run(self, task: ApplicationType):
    async for chunk in self.async_process():
        yield chunk
```

**Option 3: Iterator**
```python
def stream_run(self, task: ApplicationType):
    return iter(["chunk1", "chunk2", "chunk3"])
```

### Pravaha's Handling

Pravaha automatically detects the type and converts as needed:

```python
# Async generator → Direct async iteration
if inspect.isasyncgen(stream):
    async for chunk in stream:
        yield chunk

# Sync iterable → Convert to async
elif hasattr(stream, "__iter__"):
    async for chunk in stream_from_sync_iterable(stream):
        yield chunk
```

---

## 9. SSE (Server-Sent Events) Format

**Standard Format:**
```
data: <chunk>

data: <chunk>

data: [DONE]

```

**Implementation:**
```python
def _sse_format(data: str) -> str:
    return f"data: {data}\n\n"
```

**Client Expectations:**
- Each chunk is prefixed with `data: `
- Each chunk ends with double newline `\n\n`
- Stream ends with `data: [DONE]\n\n`

---

## 10. Public API & Client Communication

**Rule:** All communication between Pravaha and clients is via **Protocols**.

### 1. Protocol-Only Public Interface

```python
# Client never imports internal implementation
from nikhil.pravaha.domain.api.protocol.bot_manager_protocol import BotManagerProtocol
from nikhil.pravaha.domain.api.protocol.task_config_protocol import TaskConfigProtocol
from nikhil.pravaha.domain.api.factory.api_factory import create_bot_api, create_fastapi_app
```

### 2. Implementation is Client's Responsibility

Clients implement protocols structurally (duck typing):

```python
# No inheritance required!
class MyBot:  # Satisfies BotManagerProtocol
    def run(self, task): ...
    def stream_run(self, task): ...

class MyConfig:  # Satisfies TaskConfigProtocol
    UtilsType = MyUtilsEnum
    ApplicationType = MyAppEnum
    ExecutionTarget = MyTargetEnum
```

### 3. Public API Exports

Only essential functions exposed through `__init__.py`:

```python
# src/nikhil/pravaha/__init__.py
from .domain.api.factory.api_factory import create_bot_api, create_fastapi_app
from .domain.api.protocol.bot_manager_protocol import BotManagerProtocol
from .domain.api.protocol.task_config_protocol import TaskConfigProtocol

__all__ = [
    'create_bot_api',
    'create_fastapi_app',
    'BotManagerProtocol',
    'TaskConfigProtocol',
]
```

---

## 11. Versioning & Backward Compatibility

**Current Version:** 1.0.0

### Semantic Versioning (MAJOR.MINOR.PATCH)

*   **MAJOR (1.x.x):** Breaking changes to protocol interfaces
    - Changing `BotManagerProtocol` method signatures
    - Changing `TaskConfigProtocol` structure
    - Removing public functions

*   **MINOR (x.1.x):** New features, backward-compatible
    - Adding new optional parameters
    - Adding new utility functions
    - New streaming capabilities

*   **PATCH (x.x.1):** Bug fixes, backward-compatible
    - Fixing streaming bugs
    - Performance improvements
    - Documentation updates

### Deprecation Policy

1. **Mark as Deprecated:** Add warning
    ```python
    import warnings
    
    def old_function():
        warnings.warn("Deprecated, use new_function()", DeprecationWarning)
    ```

2. **Keep for 1 MINOR Version**

3. **Remove in MAJOR Version**

---

## 12. Testing Standards

**Philosophy:** Protocol-based libraries must be thoroughly tested.

### Test Structure
```
tests/
├── unit/              # Protocol and factory tests
├── integration/       # Full API integration tests
└── examples/          # Example usage tests
```

### Testing Rules

1. **Protocol Validation:**
    ```python
    def test_protocol_compliance():
        # Verify client implementation satisfies protocol
        assert callable(getattr(bot_manager, 'run'))
        assert callable(getattr(bot_manager, 'stream_run'))
    ```

2. **API Factory Tests:**
    ```python
    def test_create_bot_api():
        router = create_bot_api(mock_bot, mock_config)
        assert router.prefix == ""
        assert len(router.routes) > 0
    ```

3. **Streaming Tests:**
    ```python
    async def test_sync_to_async_conversion():
        def sync_gen():
            yield from ["a", "b", "c"]
        
        chunks = []
        async for chunk in stream_from_sync_iterable(sync_gen()):
            chunks.append(chunk)
        
        assert chunks == ["a", "b", "c"]
    ```

4. **Integration Tests:**
    ```python
    from fastapi.testclient import TestClient
    
    def test_utility_endpoint():
        client = TestClient(app)
        response = client.post("/api/run/utility", json={"task_name": "test"})
        assert response.status_code == 200
    ```

---

## 13. Documentation Standards

### Code Documentation

1. **Docstrings Required For:**
    - All public functions
    - All Protocol definitions
    - Complex algorithms

2. **Docstring Format:**
    ```python
    def create_bot_api(
        bot_manager: BotManagerProtocol,
        task_config: TaskConfigProtocol,
        *,
        route_prefix: str = "",
    ) -> APIRouter:
        """
        Create an APIRouter with bot management endpoints.
        
        Args:
            bot_manager: Implementation of BotManagerProtocol
            task_config: Implementation of TaskConfigProtocol
            route_prefix: Optional prefix for all routes
            
        Returns:
            Configured FastAPI APIRouter instance
            
        Raises:
            HTTPException: If bot_manager execution fails
        """
    ```

3. **Type Hints:**
    - All parameters and return types
    - Use `Union`, `Optional`, `Iterable` from `typing`
    - Pydantic models for structured data

---

## 14. Common Patterns & Anti-Patterns

### ✅ DO: Patterns to Follow

```python
# ✅ Protocol-Based Design
class MyBot:  # No inheritance
    def run(self, task): ...

# ✅ Type Hints
def process(data: MyEnum) -> dict[str, Any]: ...

# ✅ Flexible Streaming
def stream_run(self, task):
    yield "chunk"  # Can be sync or async

# ✅ Error Preservation
except Exception as e:
    raise HTTPException(detail=f"{type(e).__name__}: {e}")
```

### ❌ DON'T: Anti-Patterns

```python
# ❌ Forcing Inheritance
class MyBot(BaseBot):  # Not needed with protocols

# ❌ Missing Type Hints
def process(data):  # Missing types

# ❌ Ignoring Exceptions
except Exception:
    pass  # Should propagate or handle

# ❌ Hardcoding Enums
if task == "chat":  # Should use Enum types
```

---

## Quick Reference Checklist

Before committing code, verify:

- [ ] **Architecture:** Follows protocol-based design?
- [ ] **Protocols:** Used for all external interfaces?
- [ ] **Type Hints:** All parameters and returns have types?
- [ ] **Streaming:** Supports both sync and async?
- [ ] **Error Handling:** Exceptions caught and propagated correctly?
- [ ] **Docs:** Public functions have docstrings?
- [ ] **Tests:** New features have tests?
- [ ] **Versioning:** Breaking change? Bump MAJOR version?

---

## 14. Dependency Management Standards

**Critical Rule:** Keep dependencies minimal and well-isolated.

### Production Dependencies (pyproject.toml)

```toml
[project]
dependencies = [
    "PyYAML==6.0.2",        # Config file parsing
    "sse-starlette==3.0.3", # SSE streaming support
    "fastapi==0.121.3"      # Web framework
]
```

### Why These Dependencies?

1. **FastAPI** - API framework (isolated to factory layer)
2. **sse-starlette** - SSE support (isolated to streaming)
3. **PyYAML** - Config parsing (optional utility)

### Rules

1. **Minimal Dependencies:**
   - Only add if absolutely necessary
   - Prefer stdlib when possible

2. **Version Pinning:**
   - Pin exact versions (`==1.2.3`)
   - Ensures reproducibility

3. **Layer Isolation:**
   - FastAPI only in `factory/`
   - SSE only in streaming endpoints
   - Domain layer has ZERO dependencies

---

## 15. Framework Isolation

**Goal:** FastAPI is in the outermost layer and easily replaceable.

### Current Isolation Status: ✅ **Excellent**

```
Domain (Protocols) ← API Factory (FastAPI) ← Application
     ↑                    ↑
  No deps            FastAPI only
```

### If FastAPI Needs Replacement:

1. Create new factory (e.g., `create_flask_api()`)
2. Same protocols, different framework
3. Client code unchanged

**Example Alternative:**
```python
# flask_factory.py
def create_flask_api(bot_manager: BotManagerProtocol, task_config: TaskConfigProtocol):
    app = Flask(__name__)
    
    @app.route('/run/utility', methods=['POST'])
    def run_utility():
        data = request.json
        task = task_config.UtilsType(data['task_name'])
        result = bot_manager.run(task)
        return {"status": "success", "result": result}
    
    return app
```

---

**Remember:** Pravaha is a **thin protocol layer** for FastAPI. Keep it simple, flexible, and framework-agnostic where possible.