# Akashavani - FastAPI Setup & Configuration

**Application**: Akashavani (FastAPI Backend)  
**Framework**: FastAPI + Pravaha  
**Last Updated**: 2026-01-12

---

## Quick Start

### Minimal Setup (Current)

```python
# main.py
from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager

from src.bavans.akashvani.bala.kadha.application.config.settings import Settings
from src.bavans.akashvani.bala.kadha.application.config.task_config import AppTaskConfig
from src.bavans.akashvani.bala.kadha.application.manager.bot_manager import BotManager

# Create instances
bot_manager = BotManager()
task_config = AppTaskConfig()
storage_manager = LocalStorageManager(defaults={
    "output": ".Amsha/output/final/output",
    "intermediate": ".Amsha/output/intermediate/output",
    "knowledge": "data/knowledge/Bala Kadha"
})

# One-line app creation!
app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager,
    llm_config_path=Settings.LLM_CONFIG
)
```

**Run**:
```bash
uvicorn src.bavans.akashvani.bala.kadha.application.app.main:app --reload
```

---

## What `create_fastapi_app` Provides

### Auto-Configured Modules

1. **Bot Manager API** (`/api/run/*`)
   - Application execution with streaming
   - Schema introspection

2. **Storage API** (`/api/storage/*`)
   - File browsing (output/intermediate/knowledge)
   - Content loading
   - Configuration management

3. **Workflow API** (`/api/workflow/*` + `/api/execution/*`)
   - Workflow CRUD
   - Client-driven execution endpoints

4. **LLM API** (`/api/llm/*`)
   - Model listing
   - Configuration management

### Built-in Features

- ✅ **CORS**: Pre-configured (adjustable)
- ✅ **Auto Documentation**: Swagger UI at `/docs`
- ✅ **Health Check**: `/health` endpoint
- ✅ **Error Handling**: Structured error responses

---

## Enhanced Setup

### With Environment Variables

```python
# .env
OUTPUT_DIR=.Amsha/output/final/output
INTERMEDIATE_DIR=.Amsha/output/intermediate/output
KNOWLEDGE_DIR=data/knowledge/Bala Kadha
LLM_CONFIG_PATH=config/llm_config.json
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# settings.py
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings:
    # LLM
    LLM_CONFIG = Path(os.getenv("LLM_CONFIG_PATH", "config/llm_config.json"))
    
    # Storage
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", ".Amsha/output/final/output")
    INTERMEDIATE_DIR = os.getenv("INTERMEDIATE_DIR", ".Amsha/output/intermediate/output")
    KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "data/knowledge/Bala Kadha")
    
    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# main.py
storage_manager = LocalStorageManager(defaults={
    "output": Settings.OUTPUT_DIR,
    "intermediate": Settings.INTERMEDIATE_DIR,
    "knowledge": Settings.KNOWLEDGE_DIR
})

app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager,
    llm_config_path=str(Settings.LLM_CONFIG),
    title="Bala Kadha API",
    prefix="api"
)

# Override CORS if needed
if not Settings.DEBUG:
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=Settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

---

## Middleware Enhancements

### 1. Logging Middleware

```python
# middleware.py
import logging
import time
from fastapi import Request

logger = logging.getLogger("akashavani")

async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} "
        f"({process_time:.3f}s) "
        f"{request.method} {request.url.path}"
    )
    
    return response

# In main.py:
from .middleware import log_requests

app.middleware("http")(log_requests)
```

### 2. Request ID Middleware

```python
import uuid
from fastapi import Request

async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

app.middleware("http")(add_request_id)
```

### 3. Error Handling Middleware

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None)
        }
    )
```

---

## Custom Endpoints

### Adding Custom Routes

```python
from fastapi import APIRouter

custom_router = APIRouter(prefix="/custom")

@custom_router.get("/status")
async def custom_status():
    return {
        "app": "Bala Kadha",
        "version": "1.0.0",
        "modules": ["bot", "storage", "workflow", "llm"]
    }

# In main.py after app creation:
app.include_router(custom_router, prefix="/api")
```

---

## Production Configuration

### Using Gunicorn

```bash
# Install
pip install gunicorn uvicorn[standard]

# Run with workers
gunicorn src.bavans.akashvani.bala.kadha.application.app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info
```

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p data logs .Amsha/output

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "src.bavans.akashvani.bala.kadha.application.app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  akashavani:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
      - ./.Amsha:/app/.Amsha
    environment:
      - DEBUG=false
      - ALLOWED_ORIGINS=https://your-frontend.com
    restart: unless-stopped
```

---

## Logging Configuration

```python
# logging_config.py
import logging
from pathlib import Path

def setup_logging():
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/akashavani.log'),
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

# In main.py:
from .logging_config import setup_logging

setup_logging()
```

---

## Testing

### Unit Tests

```python
# tests/test_main.py
from fastapi.testclient import TestClient
from src.bavans.akashvani.bala.kadha.application.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_workflow_endpoints():
    # Create workflow
    response = client.post("/api/workflow/create", json={
        "name": "Test Workflow",
        "nodes": [],
        "edges": []
    })
    assert response.status_code == 200
    assert "id" in response.json()

def test_storage_config():
    response = client.get("/api/storage/config")
    assert response.status_code == 200
    assert "output" in response.json()
```

### Load Testing

```python
# tests/load_test.py
from locust import HttpUser, task, between

class AkashavaniUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def health_check(self):
        self.client.get("/health")
    
    @task(3)
    def list_workflows(self):
        self.client.get("/api/workflow/list")
    
    @task(2)
    def browse_storage(self):
        self.client.get("/api/storage/output/browse")
```

Run:
```bash
locust -f tests/load_test.py --host=http://localhost:8000
```

---

## Monitoring

### Health Check Enhancement

```python
@app.get("/health/detailed")
async def detailed_health():
    from pathlib import Path
    
    checks = {
        "api": "ok",
        "storage": {
            "output": Path(".Amsha/output").exists(),
            "knowledge": Path("data/knowledge").exists()
        },
        "config": {
            "llm": Path(Settings.LLM_CONFIG).exists()
        }
    }
    
    all_ok = all([
        checks["api"] == "ok",
        all(checks["storage"].values()),
        all(checks["config"].values())
    ])
    
    return {
        "status": "ok" if all_ok else "degraded",
        "checks": checks
    }
```

---

## Summary

**Current Setup**: ✅ Excellent - Uses factory pattern

**Enhancements**:
- 🟡 Environment variables (medium priority)
- 🟡 Logging middleware (medium priority)
- 🟢 Custom endpoints (as needed)
- 🟢 Docker setup (for deployment)
- 🟢 Monitoring (for production)

**Next Steps**:
1. Add `.env` file for configuration
2. Implement logging middleware
3. Set up tests
4. Configure for production deployment

**Status**: Ready for production with enhancements!
