# Bot Module - Technical Documentation

> **Audience:** Pravaha contributors and maintainers  
> **Client Documentation:** [docs/client/bot-module.md](../client/bot-module.md)

## Module Objective

The Bot module provides the **core execution engine** for Pravaha, enabling:
1. **Synchronous utility execution** - Non-blocking operations (calculators, validators, parsers)
2. **Asynchronous streaming execution** - LLM applications with real-time response streaming
3. **Schema introspection** - Expose input/output Pydantic models as JSON schemas
4. **Configuration retrieval** - Parse and serve YAML configurations as JSON

## Architecture

### Protocol-Based Design

The module follows **Dependency Inversion Principle** using Python `Protocol`:

```
┌─────────────────────┐
│  BotAPIProvider     │  (Presentation Layer - FastAPI)
│  (HTTP Interface)   │
└──────────┬──────────┘
           │ depends on
           ↓
┌─────────────────────┐
│ BotManagerProtocol  │  (Domain Layer - Interface)
│   (Protocol/ABC)    │
└──────────┬──────────┘
           │ implemented by
           ↓
┌─────────────────────┐
│  SimpleBotManager   │  (Application Layer - Concrete)
│  (User's Impl)      │
└─────────────────────┘
```

**Benefits:**
- Framework-agnostic business logic
- Easily testable (mock protocols)
- Flexible implementations (swap out bot managers)

### Components

#### 1. Protocol Layer (`src/nikhil/pravaha/domain/bot/protocol/`)

**File:** `bot_manager_protocol.py`

```python
class BotManagerProtocol(Protocol[UT, AT]):
    """
    Generic protocol for bot managers.
    
    Type Parameters:
        UT: Utility Task Enum type
        AT: Application Task Enum type
    """
    def run(self, utility_task: UT, inputs: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Synchronous execution. Must return JSON-serializable result."""
        ...
    
    def stream_run(
        self, 
        application_task: AT, 
        inputs: Optional[List[Dict[str, Any]]] = None,
        llm_config: Optional[Any] = None
    ) -> Union[Iterable[str], AsyncIterable[str]]:
        """
        Streaming execution. Can return sync or async iterables.
        Pravaha auto-converts sync to async if needed.
        """
        ...
    
    def get_input_model(self, task: Union[UT, AT]) -> Optional[Any]:
        """Returns Pydantic model class for input validation."""
        ...
    
    def get_output_model(self, task: Union[UT, AT]) -> Optional[Any]:
        """Returns Pydantic model class for output schema."""
        ...
    
    def get_config(self, task: Union[UT, AT]) -> Optional[Dict[str, Any]]:
        """Returns YAML config as dict for UI introspection."""
        ...
```

**Design Decision:** Generic types (`UT`, `AT`) allow type-safe enum usage while maintaining flexibility.

#### 2. Model Layer (`src/nikhil/pravaha/domain/bot/model/`)

**Pydantic Models for Request/Response:**

```python
class UtilityRequest(BaseModel):
    task_name: str  # Enum value
    inputs: Optional[List[Dict[str, Any]]] = None

class ApplicationRequest(BaseModel):
    task_name: str
    inputs: Optional[List[Dict[str, Any]]] = None
    llm_config_override: Optional[LLMConfigOverrideModel] = None
```

**LLM Config Override Structure:**
```python
class LLMConfigOverrideModel(BaseModel):
    model_config: ModelConfig
    llm_parameters: LLMParameters
```

This allows runtime LLM configuration without modifying task definitions.

#### 3. Provider Layer (`src/nikhil/pravaha/domain/bot/provider/`)

**File:** `bot_api_provider.py`

**Class:** `BotAPIProvider`

**Responsibilities:**
1. Create FastAPI `APIRouter`
2. Define routes and handlers
3. Map task names (strings) to Enum values
4. Handle errors and return appropriate HTTP responses
5. Convert sync iterables to async for SSE streaming

**Key Methods:**

```python
def _setup_routes(self):
    """Register all bot API routes."""
    # Utility (sync)
    self.router.post("/run/utility")(self.run_utility)
    
    # Application (async stream)
    self.router.post("/run/application/stream")(self.run_application_stream)
    
    # Enums
    self.router.get("/enums/util-types")(self.get_util_types)
    self.router.get("/enums/application-types")(self.get_application_types)
    self.router.get("/enums/execution-targets")(self.get_execution_targets)
    
    # Schemas
    self.router.get("/protocol/schema/input/{task_name}")(self.get_input_schema)
    self.router.get("/protocol/schema/output/{task_name}")(self.get_output_schema)
    
    # Config
    self.router.get("/protocol/config/{task_name}")(self.get_config)

def _get_task_enum(self, task_name: str) -> Optional[Union[UT, AT]]:
    """
    Resolve task name string to Enum value.
    Searches in UtilsType, then ApplicationType.
    """
    # Try UtilsType
    for util in self.task_config.UtilsType:
        if util.value == task_name:
            return util
    
    # Try ApplicationType
    for app in self.task_config.ApplicationType:
        if app.value == task_name:
            return app
    
    return None
```

## Data Flow

### 1. Synchronous Utility Execution

```
HTTP Request (POST /run/utility)
    ↓
BotAPIProvider.run_utility()
    ↓
Resolve task_name → Enum
    ↓
bot_manager.run(enum, inputs)
    ↓
User's implementation executes
    ↓
Result returned as JSON
    ↓
HTTP Response {"status": "success", "result": {...}}
```

### 2. Streaming Application Execution

```
HTTP Request (POST /run/application/stream)
    ↓
BotAPIProvider.run_application_stream()
    ↓
Resolve task_name → Enum
    ↓
bot_manager.stream_run(enum, inputs, llm_config)
    ↓
Returns Iterable[str] or AsyncIterable[str]
    ↓
If sync: Convert to async via stream_from_sync_iterable()
    ↓
EventSourceResponse (SSE)
    ↓
Stream chunks as "data: <chunk>\n\n"
    ↓
Final: "data: [DONE]\n\n"
```

### 3. Schema Retrieval

```
HTTP Request (GET /protocol/schema/input/{task_name})
    ↓
BotAPIProvider.get_input_schema()
    ↓
Resolve task_name → Enum
    ↓
bot_manager.get_input_model(enum)
    ↓
Returns Pydantic model class (or None)
    ↓
model.model_json_schema() - Convert to JSON Schema
    ↓
HTTP Response (JSON Schema)
```

## Design Patterns

### 1. Protocol Pattern (Structural Typing)
- Uses Python `Protocol` for duck typing
- No inheritance required
- Encourages composition over inheritance

### 2. Dependency Injection
- `BotAPIProvider` receives `bot_manager` and `task_config` via constructor
- Easily testable with mocks

### 3. Adapter Pattern
- `BotAPIProvider` adapts domain protocol to FastAPI HTTP interface
- Decouples HTTP concerns from business logic

### 4. Registry Pattern
- Bot managers typically use dicts to map tasks to implementations
- Example: `self.input_models = {UtilsType.TASK: ModelClass}`

## Key Design Decisions

### Why Protocol Instead of ABC?

**Chose:** `typing.Protocol`  
**Instead of:** `abc.ABC`

**Reasons:**
1. **Structural typing** - No explicit inheritance needed
2. **Gradual typing** - Works with existing code
3. **Composition-friendly** - Encourages flexible design
4. **Testing** - Easier to create mocks

### Why Separate Utility and Application?

**Utility:** Synchronous, simple, fast operations  
**Application:** Async streaming, LLM-based, long-running

**Reasons:**
1. **Performance** - Don't add streaming overhead to simple operations
2. **Client Experience** - Different UX for instant vs streaming responses
3. **Error Handling** - Different strategies for sync vs async
4. **Resource Management** - streaming requires connection management

### Why Generic Types?

```python
Protocol[UT, AT]  # Instead of Protocol
```

**Reasons:**
1. **Type Safety** - IDEs can provide autocomplete
2. **Documentation** - Self-documenting code
3. **Validation** - Catch type errors at development time

## Implementation Requirements

To implement a bot manager:

1. **Define Enums:**
   ```python
   class UtilsType(str, Enum):
       MY_TASK = "my_task"
   ```

2. **Implement Protocol:**
   ```python
   class MyBotManager:
       def run(self, utility_task, inputs=None):
           # Implementation
       
       def stream_run(self, application_task, inputs=None, llm_config=None):
           # Implementation
   ```

3. **Return JSON-Serializable:**
   - `run()` must return JSON-serializable data
   - `stream_run()` must yield strings

4. **Handle LLM Config:**
   - Accept `llm_config` parameter
   - Use override if provided, else use defaults

## Error Handling

### HTTP Status Codes

| Scenario | Status | Response |
|----------|--------|----------|
| Success | 200 | `{"status": "success", "result": ...}` |
| Task not found | 404 | `{"detail": "Task ... not found"}` |
| Execution error | 500 | `{"detail": "ErrorType: message"}` |

### Error Strategy

```python
try:
    result = self.bot_manager.run(task_enum, inputs)
    return {"status": "success", "result": result}
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

All exceptions propagate to FastAPI's error handling.

## Testing

### Unit Tests

Test files: `tests/unit/domain/bot/`

**Test Protocol Compliance:**
```python
def test_bot_manager_implements_protocol():
    assert isinstance(bot_manager, BotManagerProtocol)
```

**Test API Endpoints:**
```python
def test_run_utility_endpoint(client):
    response = client.post("/api/run/utility", json={
        "task_name": "calculator",
        "inputs": [{"a": 1, "b": 2}]
    })
    assert response.status_code == 200
```

### Integration Tests

Test complete flow from HTTP → BotManager → Response

## Performance Considerations

1. **Sync to Async Conversion** - Minimal overhead using `asyncio.to_thread()`
2. **SSE Streaming** - Low memory, chunks sent immediately
3. **No State** - BotManagerProtocol is stateless (scalable)

## Future Enhancements

- [ ] Rate limiting per task type
- [ ] Metrics and observability
- [ ] Request/response logging middleware
- [ ] Authentication/authorization hooks
- [ ] Task queuing for long-running operations
