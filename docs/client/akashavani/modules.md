# Akashavani - Module Configuration Guide

**Application**: Akashavani (FastAPI Backend)  
**Framework**: Pravaha Library  
**Last Updated**: 2026-01-12

---

## Overview

Akashavani uses Pravaha's `create_fastapi_app()` factory which auto-configures all modules:
- ✅ Bot Manager (Application execution)
- ✅ Storage (Output/Intermediate/Knowledge)
- ✅ Workflow (Client-driven orchestration)
- ✅ LLM Configuration

---

## Module Status

| Module | Status | Notes |
|--------|--------|-------|
| **Bot** | ✅ Working | No changes needed |
| **Storage** | ✅ Working | Consider adding upload/delete endpoints |
| **Workflow** | ✅ **Updated** | Now uses OrchestrationEngine |
| **LLM** | ✅ Working | No changes needed |

---

## Bot Module

### Current Setup

```python
# src/bavans/akashvani/bala/kadha/application/manager/bot_manager.py
class BotManager:
    def execute_application(self, task_name: str, inputs: List[Dict], llm_config_override: Optional[Dict] = None):
        # Your custom implementation
        ...
```

**Status**: ✅ **No changes needed**

### API Endpoints Provided

- `POST /api/run/application/stream` - Execute application with streaming

### Best Practices

1. ✅ Use streaming responses for long-running tasks
2. ✅ Handle llm_config_override properly
3. ✅ Validate inputs against schema

---

## Storage Module

### Current Setup

```python
defaults = {
    "output": ".Amsha/output/final/output",
    "intermediate": ".Amsha/output/intermediate/output",
    "knowledge": "data/knowledge/Bala Kadha"
}

storage_manager = LocalStorageManager(defaults=defaults)
```

**Status**: ✅ **Working**

### API Endpoints Provided

- `GET /api/storage/config` - Get storage paths
- `POST /api/storage/config` - Update storage paths
- `GET /api/storage/{category}/browse` - Browse files
- `GET /api/storage/{category}/content` - Load file content

### Recommended Additions

#### 1. Upload Endpoint

```python
# Add to Pravaha's StorageAPIProvider (future enhancement)
@router.post("/storage/{category}/upload")
async def upload_file(
    category: str,
    file: UploadFile,
    path: Optional[str] = None
):
    # Save file to storage
    file_path = storage_manager.get_path(category) / (path or file.filename)
    with open(file_path, 'wb') as f:
        f.write(await file.read())
    return {"success": True, "path": str(file_path)}
```

#### 2. Delete Endpoint

```python
@router.delete("/storage/{category}")
async def delete_file(category: str, path: str):
    file_path = storage_manager.get_path(category) / path
    if file_path.exists():
        file_path.unlink()
        return {"success": True}
    raise HTTPException(404, "File not found")
```

#### 3. Search Endpoint

```python
@router.get("/storage/{category}/search")
async def search_files(category: str, query: str):
    base_path = storage_manager.get_path(category)
    results = []
    for file_path in base_path.rglob(f"*{query}*"):
        results.append({
            "path": str(file_path.relative_to(base_path)),
            "size": file_path.stat().st_size,
            "modified": file_path.stat().st_mtime
        })
    return results
```

**Priority**: 🟡 **Medium** - Nice to have for better UI integration

---

## Workflow Module

### ✅ Already Updated

**Change Made**: Factory now uses `SimpleOrchestrationEngine` instead of `SimpleWorkflowEngine`

**What You Need to Do**:
1. Update Pravaha: `cd E:\Python\Pravaha && pip install -e .`
2. Restart server: `uvicorn ...app.main:app --reload`

### New API Endpoints Available

- `POST /api/execution/run` - Initialize workflow execution
- `GET /api/execution/run/{id}/status` - Poll for next node
- `POST /api/execution/run/{id}/node/{node_id}/status` - Update node status
- `GET /api/execution/run/{id}/node/{node_id}/output` - Get node output

### Configuration Options

Currently hardcoded:
```python
data_dir = os.path.join(os.getcwd(), "data")
```

**Future Enhancement**: Make configurable
```python
app = create_fastapi_app(
    ...,
    workflow_data_dir=".Amsha/workflow"  # NEW parameter
)
```

---

## LLM Module

### Current Setup

```python
llm_config_path=Settings.LLM_CONFIG  # "config/llm_config.json"
```

**Status**: ✅ **Working**

### API Endpoints Provided

- `GET /api/llm/models` - List available LLM models
- `GET /api/llm/config` - Get current config
- `POST /api/llm/config` - Update config

### Best Practices

1. ✅ Store API keys securely (not in code)
2. ✅ Use environment variables for sensitive data
3. ✅ Validate model configurations

---

## Environment Configuration

### Recommended Setup

Create `.env` file:
```env
# Storage paths
OUTPUT_DIR=.Amsha/output/final/output
INTERMEDIATE_DIR=.Amsha/output/intermediate/output
KNOWLEDGE_DIR=data/knowledge/Bala Kadha

# API settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# LLM
LLM_CONFIG_PATH=config/llm_config.json

# CORS (production)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Update `settings.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    LLM_CONFIG = os.getenv("LLM_CONFIG_PATH", "config/llm_config.json")
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", ".Amsha/output/final/output")
    # ... etc
```

**Priority**: 🟡 **Medium** - Good practice for production

---

## Logging Enhancement

### Current: No logging

### Recommended:

```python
# In main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.Amsha/logs/akashavani.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("akashavani")

# Add middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

---

## Testing Recommendations

### Unit Tests

```python
# tests/test_bot_manager.py
def test_bot_manager_execute():
    bot = BotManager()
    result = bot.execute_application(
        task_name="test_task",
        inputs=[{"key": "value"}]
    )
    assert result is not None

# tests/test_storage.py
def test_storage_config():
    from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
    manager = LocalStorageManager(defaults={...})
    path = manager.get_path("output")
    assert path.exists()
```

### Integration Tests

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_workflow_execution():
    # Create workflow
    resp = client.post("/api/workflow/create", json={...})
    workflow_id = resp.json()["id"]
    
    # Start execution
    exec_resp = client.post("/api/execution/run", json={"workflow_id": workflow_id})
    run_id = exec_resp.json()["workflow_run_id"]
    
    # Poll status
    status = client.get(f"/api/execution/run/{run_id}/status")
    assert status.status_code == 200
```

---

## Deployment Checklist

### Development
- [x] Uses `create_fastapi_app` factory
- [x] LLM config path set
- [x] Storage defaults configured
- [ ] Logging added
- [ ] Environment variables configured

### Production
- [ ] Use Gunicorn + Uvicorn workers
- [ ] Configure CORS properly
- [ ] Set up HTTPS
- [ ] Use database for workflows (instead of JSON)
- [ ] Add rate limiting
- [ ] Set up monitoring
- [ ] Secure API keys
- [ ] Configure backups

---

## Summary

**Akashavani Status**: ✅ **Excellent** - Well-configured, minimal changes needed

**Recent Updates**:
- ✅ Workflow module updated to OrchestrationEngine

**Recommended Enhancements**:
1. 🟡 Add storage upload/delete/search endpoints
2. 🟡 Add environment variable configuration
3. 🟡 Add logging middleware
4. 🟢 Add unit/integration tests
5. 🟢 Production deployment config

**Priority**: Most enhancements are optional - current setup works well!
