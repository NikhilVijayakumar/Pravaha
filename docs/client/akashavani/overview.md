# Akashavani (Backend) - Code Review & Improvements

**Repository**: `E:\Python\Pravaha\NikhilVijayakumar-akashavani-8c5029d59e90`

**Purpose**: FastAPI backend application using Pravaha library for domain applications

**Review Date**: 2026-01-12

---

## Current Architecture

### ✅ Strengths

1. **Uses Pravaha API Factory** 
   - File: `src/bavans/akashvani/bala/kadha/application/app/main.py`
   - Clean, minimal setup using `create_fastapi_app()`
   - Auto-configures all modules (bot, storage, workflow, LLM)

2. **Good Configuration Management**
   - Centralized settings in `Settings` class
   - LLM config path configurable
   - Storage defaults properly set

3. **Follows Pravaha Patterns**
   - Uses `BotManager` protocol
   - Uses `LocalStorageManager` for storage
   - Proper separation of config and application logic

### Current Setup Code

```python
# src.bavans.akashvani.application.app.api.py
from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager

from src.bavans.akashvani.bala.kadha.application.config.settings import Settings
from src.bavans.akashvani.bala.kadha.application.config.task_config import AppTaskConfig
from src.bavans.akashvani.bala.kadha.application.manager.bot_manager import BotManager

# Create instances
bot_manager_instance = BotManager()
task_config_instance = AppTaskConfig()

defaults = {
    "output": ".Amsha/output/final/output",
    "intermediate": ".Amsha/output/intermediate/output",
    "knowledge": "data/knowledge/Bala Kadha"
}

storage_manager = LocalStorageManager(defaults=defaults)

# Auto-configure everything!
app = create_fastapi_app(
    bot_manager=bot_manager_instance,
    task_config=task_config_instance,
    storage_manager=storage_manager,
    llm_config_path=Settings.LLM_CONFIG
)
```

---

## ✅ ALREADY FIXED: Workflow Engine Update

### What Was Wrong
- Pravaha's `create_fastapi_app()` was using old `SimpleWorkflowEngine`
- Wouldn't work with new client-driven execution

### What We Fixed
- Updated `api_factory.py` to use `SimpleOrchestrationEngine`
- Removed dependency on `PravahaTaskExecutor` (no longer needed)

### What Akashavani Needs to Do
1. **Update Pravaha package**:
   ```bash
   cd E:\Python\Pravaha
   pip install -e .
   ```

2. **Restart Akashavani server**:
   ```bash
   cd E:\Python\Pravaha\NikhilVijayakumar-akashavani-8c5029d59e90
   uvicorn src.bavans.akashvani.bala.kadha.application.app.main:app --reload
   ```

3. **Verify new endpoints**:
   ```bash
   curl http://localhost:8000/docs
   ```
   Should see:
   - POST `/api/execution/run`
   - GET `/api/execution/run/{id}/status`
   - POST `/api/execution/run/{id}/node/{node_id}/status`
   - GET `/api/execution/run/{id}/node/{node_id}/output`

---

## 🟡 Medium Priority Improvements

### 1. Workflow Data Persistence Location

**Current**:
```python
# In api_factory.py
data_dir = os.path.join(os.getcwd(), "data")
workflow_repo = JsonWorkflowRepository(os.path.join(data_dir, "workflows.json"))
run_repo = JsonRunRepository(os.path.join(data_dir, "runs.json"))
```

**Issue**: Hardcoded to `data/` directory in CWD

**Improvement**: Make configurable like storage paths

**Suggested Change in Akashavani**:
```python
# In main.py
app = create_fastapi_app(
    bot_manager=bot_manager_instance,
    task_config=task_config_instance,
    storage_manager=storage_manager,
    llm_config_path=Settings.LLM_CONFIG,
    workflow_data_dir=".Amsha/workflow"  # NEW parameter (optional)
)
```

**Requires**: Update to Pravaha's `create_fastapi_app` signature (future enhancement)

**Priority**: 🟡 **MEDIUM** - Current behavior works, but not flexible

---

### 2. Health Check Enhancement

**Current**:
```python
@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Improvement**: Include service status checks

**Suggested**:
```python
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "services": {
            "bot_manager": "ok",
            "storage": "ok",
            "workflow": "ok",
            "llm_config": "ok"
        },
        "version": "1.0.0"
    }
```

**Priority**: 🟡 **MEDIUM**

---

### 3. CORS Configuration

**Current**: Allows all origins (`*`)

**Security Risk**: ⚠️ Not suitable for production

**Improvement**:
```python
# In main.py or settings.py
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Sangama UI dev
    "http://localhost:5173",  # Vite dev server
    # Add production URLs
]

app = create_fastapi_app(...)

# Override CORS after creation
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Priority**: 🟠 **HIGH for production**, 🟢 Low for development

---

### 4. Environment-Based Configuration

**Current**: Hardcoded defaults

**Improvement**: Use environment variables

```python
# settings.py
import os
from pathlib import Path

class Settings:
    # Existing
    LLM_CONFIG = Path("config/llm_config.json")
    
    # Add environment support
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", ".Amsha/output/final/output")
    INTERMEDIATE_DIR = os.getenv("INTERMEDIATE_DIR", ".Amsha/output/intermediate/output")
    KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "data/knowledge/Bala Kadha")
    
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
```

**Usage**:
```bash
export OUTPUT_DIR="/custom/path/output"
uvicorn main:app --host $API_HOST --port $API_PORT
```

**Priority**: 🟡 **MEDIUM**

---

## 🟢 Low Priority / Nice-to-Have

### 5. API Documentation Enhancement

**Current**: Auto-generated Swagger docs

**Improvement**: Add detailed descriptions

```python
app = create_fastapi_app(
    ...,
    title="Bala Kadha API",  # Already done
    description="""
    ## Features
    - 🤖 Bot/Application execution
    - 📁 Storage management
    - 🔄 Workflow orchestration
    - 🧠 LLM configuration
    
    ## Workflow Execution
    Client-driven workflow execution model. See /docs for details.
    """,
    version="1.0.0"
)
```

---

### 6. Logging and Monitoring

**Current**: No structured logging

**Improvement**: Add logging middleware

```python
import logging
from fastapi import Request
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("akashavani")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.3f}s "
        f"status={response.status_code}"
    )
    
    return response
```

---

### 7. Request Validation Error Handling

**Current**: Default FastAPI error responses

**Improvement**: Consistent error format

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )
```

---

## 📂 Suggested Project Structure

### Current (Good!)
```
src/bavans/akashvani/bala/kadha/
├── application/
│   ├── app/
│   │   └── main.py  ← Entry point
│   ├── config/
│   │   ├── settings.py
│   │   └── task_config.py
│   └── manager/
│       └── bot_manager.py
├── data/  ← Workflow/run storage (created at runtime)
└── config/
    └── llm_config.json
```

### Recommended Additions
```
src/bavans/akashvani/bala/kadha/
├── application/
│   ├── app/
│   │   ├── main.py
│   │   ├── middleware.py  [NEW - logging, CORS]
│   │   └── exceptions.py  [NEW - error handlers]
│   ├── config/
│   │   ├── settings.py  [UPDATE - add env vars]
│   │   └── task_config.py
│   └── manager/
│       └── bot_manager.py
├── .env  [NEW - environment variables]
└── .env.example  [NEW - template]
```

---

## Testing Recommendations

### Currently Missing
- No tests found in repository
- Should add basic endpoint tests

### Suggested Test Structure
```
tests/
├── test_api/
│   ├── test_workflow_endpoints.py
│   ├── test_bot_endpoints.py
│   └── test_storage_endpoints.py
├── test_integration/
│   └── test_workflow_execution.py
└── conftest.py  # pytest fixtures
```

### Example Test
```python
# test_workflow_endpoints.py
from fastapi.testclient import TestClient
from src.bavans.akashvani.bala.kadha.application.app.main import app

client = TestClient(app)

def test_create_workflow():
    response = client.post("/api/workflow/create", json={
        "name": "Test Workflow",
        "nodes": [],
        "edges": []
    })
    assert response.status_code == 200
    assert "id" in response.json()

def test_execution_flow():
    # Create workflow
    workflow_resp = client.post("/api/workflow/create", json={...})
    workflow_id = workflow_resp.json()["id"]
    
    # Start execution
    exec_resp = client.post("/api/execution/run", json={
        "workflow_id": workflow_id
    })
    assert exec_resp.status_code == 200
    run_id = exec_resp.json()["workflow_run_id"]
    
    # Poll status
    status_resp = client.get(f"/api/execution/run/{run_id}/status")
    assert status_resp.status_code == 200
    assert "current_node" in status_resp.json()
```

---

## Deployment Recommendations

### Development
**Current**: Good for local development

### Production Checklist
- [ ] Use production WSGI server (Gunicorn + Uvicorn workers)
- [ ] Configure CORS properly
- [ ] Set up logging to file/service
- [ ] Use environment variables for all config
- [ ] Add rate limiting
- [ ] Enable HTTPS
- [ ] Set up monitoring (health checks, metrics)
- [ ] Database for workflows (instead of JSON files)

### Example Production Command
```bash
gunicorn src.bavans.akashvani.bala.kadha.application.app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

---

## Summary

**Overall Code Quality**: 🟢 **Good** (8/10)

**Strengths**:
- ✅ Clean setup using API factory
- ✅ Good configuration management
- ✅ Follows Pravaha patterns
- ✅ Minimal boilerplate

**Already Updated**:
- ✅ Workflow engine now uses OrchestrationEngine (via Pravaha update)

**Recommended Next Steps**:
1. 🔴 **Update Pravaha package** and restart server (Critical)
2. 🟡 Test new execution endpoints with Swagger/curl (High)
3. 🟡 Add environment-based configuration (Medium)
4. 🟢 Add basic endpoint tests (Low)
5. 🟢 Enhanced logging (Low)

**No Breaking Changes Required**: Application continues to work as-is, just with enhanced workflow capabilities!
