# API Factory Module - Technical Documentation

> **Audience:** Pravaha contributors and maintainers  
> **Client Documentation:** [docs/client/api-factory.md](../client/api-factory.md)

## Module Objective

The API Factory provides **one-function application setup**, eliminating boilerplate and reducing integration complexity from 100+ lines to 10 lines.

**Key Value:** Convenience layer that orchestrates all other modules.

## Architecture

### Factory Pattern with Complete Initialization

```
create_fastapi_app()
    │
    ├─→ Creates FastAPI app
    ├─→ Adds CORS middleware
    ├─→ Initializes LLMConfigManager
    ├─→ Initializes Storage components
    │   ├─→ Path resolver
    │   └─→ Version resolver
    ├─→ Initializes Workflow components
    │   ├─→ Workflow repository (JSON)
    │   ├─→ Run repository (JSON)
    │   ├─→ Task executor (bridge to bot manager)
    │   └─→ Workflow engine
    ├─→ Creates all API providers
    │   ├─→ BotAPIProvider
    │   ├─→ StorageAPIProvider
    │   ├─→ WorkflowAPIProvider
    │   └─→ LLMAPIProvider
    ├─→ Mounts all routers
    └─→ Adds health check

Returns: Fully configured FastAPI app
```

## Implementation

### File Location
`src/nikhil/pravaha/domain/api/factory/api_factory.py`

### Function Signature

```python
def create_fastapi_app(
    bot_manager,                          # Your BotManager implementation
    task_config,                          # Task enum configuration
    storage_manager,                      # LocalStorageManager instance
    prefix: str = "api",                  # API route prefix
    title: str = "Akashvani Unified API", # App title
    llm_config_path: Optional[str] = None # Path to LLM YAML config
) -> FastAPI:
```

### Implementation Flow

```python
def create_fastapi_app(...) -> FastAPI:
    # 1. Create FastAPI app
    app = FastAPI(title=title)
    
    # 2. Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # 3. Initialize LLM Config
    llm_config_manager = LLMConfigManager(
        Path(llm_config_path) if llm_config_path else None
    )
    
    # 4. Initialize Storage components
    version_resolver = ArtifactVersionResolver(storage_manager, llm_config_manager)
    path_resolver = StoragePathResolver(storage_manager, llm_config_manager, version_resolver)
    
    storage_provider = StorageAPIProvider(
        storage_manager,
        llm_config_manager,
        path_resolver,
        version_resolver
    )
    
    # 5. Initialize Workflow components
    data_dir = os.path.join(os.getcwd(), "data")
    workflow_repo = JsonWorkflowRepository(os.path.join(data_dir, "workflows.json"))
    run_repo = JsonRunRepository(os.path.join(data_dir, "runs.json"))
    
    task_executor = PravahaTaskExecutor(bot_manager, task_config)
    engine = SimpleWorkflowEngine(task_executor, run_repo)
    workflow_service = WorkflowService(workflow_repo, run_repo, engine)
    
    workflow_provider = WorkflowAPIProvider(workflow_service)
    
    # 6. Initialize Bot provider
    bot_provider = BotAPIProvider(bot_manager, task_config)
    
    # 7. Initialize LLM provider
    llm_api_provider = LLMAPIProvider(llm_config_manager)
    
    # 8. Mount all routers
    app.include_router(bot_provider.router, prefix=f"/{prefix}")
    app.include_router(storage_provider.router, prefix=f"/{prefix}")
    app.include_router(workflow_provider.router, prefix=f"/{prefix}")
    app.include_router(llm_api_provider.router, prefix=f"/{prefix}/llm")
    
    # 9. Add health check
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    return app
```

## Design Patterns

### 1. Factory Pattern
Encapsulates complex object creation in single function.

### 2. Dependency Injection
All dependencies passed as parameters (bot_manager, task_config, storage_manager).

### 3. Facade Pattern
Provides simple interface to complex subsystem (all 4 modules).

### 4. Builder Pattern (Implicit)
Step-by-step construction of FastAPI app with all components.

## Key Design Decisions

### Why Single Function?

**Benefits:**
1. **Simplicity** - One call vs 50+ lines
2. **Convention** - Opinionated defaults
3. **Consistency** - Everyone gets same setup
4. **Maintenance** - Updates in one place

**Trade-off:** Less flexibility (but can extend returned app).

### Why Default to Current Directory for Workflows?

```python
data_dir = os.path.join(os.getcwd(), "data")
```

**Reasons:**
1. **Predictability** - Always in same place
2. **Portability** - Relative to project root
3. **Simplicity** - No path configuration needed

**Alternative:** Could accept `workflow_data_dir` parameter.

### Why Separate LLM Prefix?

```python
app.include_router(llm_api_provider.router, prefix=f"/{prefix}/llm")
```

Routes: `/api/llm/configs`, `/api/llm/config/{mode}`

**Reasons:**
1. **Namespace** - Clear LLM-specific routes
2. **RESTful** - `/llm` is a resource collection
3. **Extensibility** - Easy to add `/llm/providers`, etc.

### Why Allow Custom Prefix?

**Default:** `/api`  
**Customizable:** Can be `/v1`, `/v2`, etc.

**Benefits:**
1. **Versioning** - Multiple API versions side-by-side
2. **Migration** - Gradual rollout of new versions
3. **Flexibility** - Adapt to organization standards

## What Gets Created

### Endpoints by Module

**Bot** (8 endpoints):
```
/api/run/utility
/api/run/application/stream
/api/enums/util-types
/api/enums/application-types
/api/enums/execution-targets
/api/protocol/schema/input/{task}
/api/protocol/schema/output/{task}
/api/protocol/config/{task}
```

**Storage** (4 endpoints):
```
/api/storage/{category}/browse
/api/storage/{category}/read
/api/storage/config
/api/storage/config (GET)
```

**Workflow** (9 endpoints):
```
/api/workflow/create
/api/workflow/list
/api/workflow/{id}
/api/workflow/update
/api/workflow/rename
/api/workflow/{id} (DELETE)
/api/workflow/run
/api/workflow/run/{run_id}
/api/workflow/runs
```

**LLM** (2 endpoints):
```
/api/llm/configs
/api/llm/config/{mode}
```

**Utility** (1 endpoint):
```
/health
```

**TOTAL: 24 endpoints**

## Testing

### Unit Tests

Test the factory function itself:
```python
def test_create_fastapi_app():
    app = create_fastapi_app(bot_manager, task_config, storage_manager)
    assert isinstance(app, FastAPI)

def test_health_endpoint():
    app = create_fastapi_app(...)
    client = TestClient(app)
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
```

###Integration Tests

Test that all modules are wired correctly:
```python
def test_bot_endpoints_mounted():
    app = create_fastapi_app(...)
    client = TestClient(app)
    response = client.get("/api/enums/util-types")
    assert response.status_code == 200

def test_storage_endpoints_mounted():
    response = client.get("/api/storage/output/browse")
    assert response.status_code == 200
```

## Usage Patterns

### Standard Usage

```python
app = create_fastapi_app(
    bot_manager=MyBotManager(),
    task_config=task_config,
    storage_manager=LocalStorageManager()
)
```

### With LLM Config

```python
app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager,
    llm_config_path="llm_config.yaml"
)
```

### Custom Prefix

```python
app = create_fastapi_app(
    ...,
    prefix="v2"  # Routes become /v2/...
)
```

### Extension After Creation

```python
app = create_fastapi_app(...)

# Add custom middleware
app.add_middleware(MyCustomMiddleware)

# Add custom routes
@app.get("/custom/route")
def custom():
    return {"custom": "response"}

# Override CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_methods=["GET", "POST"]
)
```

## Performance Considerations

1. **One-Time Setup** - Factory runs once at startup
2. **No Runtime Overhead** - Same as manual setup
3. **Middleware Order** - CORS added before routers (correct order)

## Dependencies Created

The factory function creates these object graphs:

```
LLMConfigManager
    ↑
    ├─ Storage Components
    │  ├─ ArtifactVersionResolver
    │  └─ StoragePathResolver
    │
    └─ Workflow Components
       ├─ JsonWorkflowRepository
       ├─ JsonRunRepository
       ├─ PravahaTaskExecutor
       ├─ SimpleWorkflowEngine
       └─ WorkflowService
```

All injected into appropriate API providers.

## Future Enhancements

- [ ] Accept custom repository implementations
- [ ] Plugin system for additional modules
- [ ] Configuration file (YAML) instead of parameters
- [ ] Auto-detect storage manager type
- [ ] Observability integration (Prometheus, OpenTelemetry)
- [ ] Rate limiting configuration
- [ ] Authentication provider injection
