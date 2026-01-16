# Client Integration Guide

## Quick Start

### Minimal Integration

```python
# 1. Import Nibandha
from nibandha import Nibandha, AppConfig

# 2. Define app configuration
config = AppConfig(name="MyApp")

# 3. Bind and use
nb = Nibandha(config).bind()
nb.logger.info("Hello from MyApp!")
```

**Result**: Logs written to `.Nibandha/MyApp/logs/MyApp.log`

## Integration Patterns

### Pattern 1: Global Instance

```python
# app/__init__.py
from nibandha import Nibandha, AppConfig

# Initialize once at module level
_nibandha = Nibandha(AppConfig(name="MyApp")).bind()

def get_logger():
    """Get application logger"""
    return _nibandha.logger

# app/main.py
from app import get_logger

logger = get_logger()
logger.info("Application started")

# app/module.py
from app import get_logger

logger = get_logger()
logger.info("Module loaded")
```

### Pattern 2: Singleton

```python
# app/nibandha_singleton.py
from nibandha import Nibandha, AppConfig

class NibandhaSingleton:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            config = AppConfig(name="MyApp")
            cls._instance = Nibandha(config).bind()
        return cls._instance

# Usage anywhere in application
from app.nibandha_singleton import NibandhaSingleton

nb = NibandhaSingleton.get_instance()
nb.logger.info("Message")
```

### Pattern 3: Dependency Injection

```python
# app/core.py
from nibandha import Nibandha, AppConfig

class Application:
    def __init__(self):
        self.nibandha = Nibandha(AppConfig(name="MyApp")).bind()
        self.logger = self.nibandha.logger
    
    def run(self):
        self.logger.info("Application running")

# main.py
app = Application()
app.run()

# Services get logger from app instance
class DataService:
    def __init__(self, logger):
        self.logger = logger
    
    def process(self):
        self.logger.info("Processing data")

service = DataService(app.logger)
```

## Real-World Examples

### Example 1: FastAPI Application

```python
# main.py
from fastapi import FastAPI
from nibandha import Nibandha, AppConfig, LogRotationConfig

# Initialize Nibandha at startup
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    global nibandha
    
    config = AppConfig(name="MyAPI", log_level="INFO")
    rotation = LogRotationConfig(
        enabled=True,
        max_size_mb=100,
        backup_count=20
    )
    
    nibandha = Nibandha(config)
    nibandha.rotation_config = rotation
    nibandha._save_rotation_config(rotation)
    nibandha.bind()
    
    nibandha.logger.info("API server started")

@app.get("/")
async def root():
    nibandha.logger.info("Root endpoint accessed")
    return {"message": "Hello"}

@app.post("/data")
async def process_data(data: dict):
    nibandha.logger.info(f"Processing data: {data}")
    # Process data
    return {"status": "success"}
```

### Example 2: Flask Application

```python
# app.py
from flask import Flask
from nibandha import Nibandha, AppConfig

app = Flask(__name__)

# Initialize Nibandha
nibandha = Nibandha(AppConfig(name="FlaskApp", log_level="DEBUG")).bind()

@app.route("/")
def index():
    nibandha.logger.info("Index page accessed")
    return "Hello, World!"

@app.route("/api/data", methods=["POST"])
def api_data():
    nibandha.logger.info("API endpoint called")
    # Handle request
    return {"status": "ok"}

if __name__ == "__main__":
    nibandha.logger.info("Starting Flask server")
    app.run()
```

### Example 3: CLI Tool

```python
# cli.py
import click
from nibandha import Nibandha, AppConfig

# Initialize Nibandha
nibandha = Nibandha(AppConfig(name="MyCLI")).bind()

@click.group()
def cli():
    """My CLI Tool"""
    pass

@cli.command()
@click.argument("filename")
def process(filename):
    """Process a file"""
    nibandha.logger.info(f"Processing {filename}")
    try:
        # Process file
        nibandha.logger.info("Processing complete")
        click.echo(f"Processed {filename}")
    except Exception as e:
        nibandha.logger.error(f"Processing failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    cli()
```

### Example 4: Background Worker

```python
# worker.py
import time
from nibandha import Nibandha, AppConfig, LogRotationConfig

# Initialize with rotation for long-running process
config = AppConfig(name="Worker", log_level="INFO")
rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=50,
    rotation_interval_hours=24,
    backup_count=30
)

nibandha = Nibandha(config)
nibandha.rotation_config = rotation
nibandha._save_rotation_config(rotation)
nibandha.bind()

def process_task(task):
    nibandha.logger.info(f"Processing task: {task}")
    # Process task
    nibandha.logger.info(f"Task complete: {task}")

def main():
    nibandha.logger.info("Worker started")
    
    while True:
        # Check rotation periodically
        if nibandha.should_rotate():
            nibandha.logger.info("Rotating logs")
            nibandha.rotate_logs()
        
        # Process tasks
        tasks = get_tasks()  # Your task queue
        for task in tasks:
            process_task(task)
        
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
```

## Multi-Application Setup

### Shared .Nibandha/ Root

```python
# project/
# ├── app1/
# │   └── main.py
# ├── app2/
# │   └── main.py
# └── .Nibandha/        # Shared root
#     ├── App1/
#     └── App2/

# app1/main.py
from nibandha import Nibandha, AppConfig
nb1 = Nibandha(AppConfig(name="App1")).bind()
nb1.logger.info("App1 running")

# app2/main.py
from nibandha import Nibandha, AppConfig
nb2 = Nibandha(AppConfig(name="App2")).bind()
nb2.logger.info("App2 running")

# Both write to separate logs in shared .Nibandha/
```

## Migration Guide

### From Standard Logging

**Before** (standard Python logging):
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)

logger = logging.getLogger(__name__)
logger.info("Application started")
```

**After** (with Nibandha):
```python
from nibandha import Nibandha, AppConfig

nibandha = Nibandha(AppConfig(
    name="MyApp",
    log_level="INFO"
)).bind()

nibandha.logger.info("Application started")
```

**Benefits**:
- ✅ Automatic log rotation
- ✅ Organized directory structure
- ✅ Configuration persistence
- ✅ Archive management

### From Custom Logging Setup

**Before**:
```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("MyApp")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    'logs/myapp.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
```

**After**:
```python
from nibandha import Nibandha, AppConfig, LogRotationConfig

config = AppConfig(name="MyApp", log_level="INFO")
rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=10,
    backup_count=5
)

nibandha = Nibandha(config)
nibandha.rotation_config = rotation
nibandha._save_rotation_config(rotation)
nibandha.bind()

# All configuration handled automatically
```

## Best Practices

### 1. Initialize at Application Startup

```python
# ✅ Good: Initialize once at startup
def main():
    nb = Nibandha(AppConfig(name="MyApp")).bind()
    app = create_app(nb.logger)
    app.run()

# ❌ Bad: Initialize in hot path
def handle_request():
    nb = Nibandha(AppConfig(name="MyApp")).bind()  # Don't do this!
    nb.logger.info("Request")
```

### 2. Use Custom Folders Appropriately

```python
# ✅ Good: Define all app folders upfront
config = AppConfig(
    name="MyApp",
    custom_folders=[
        "data/inputs",
        "data/outputs",
        "models",
        "cache"
    ]
)
nb = Nibandha(config).bind()

# Access folders
input_dir = nb.app_root / "data/inputs"
output_dir = nb.app_root / "data/outputs"
```

### 3. Configure Rotation for Long-Running Services

```python
#✅ Good: Enable rotation for services
if __name__ == "__main__":
    rotation = LogRotationConfig(
        enabled=True,
        max_size_mb=100,
        backup_count=30
    )
    
    # Add rotation check to event loop
    while running:
        if nb.should_rotate():
            nb.rotate_logs()
        
        process_events()
```

### 4. Use Environment-Specific Configuration

```python
# ✅ Good: Different config per environment
import os

env = os.getenv("ENV", "development")
log_level = "DEBUG" if env == "development" else "WARNING"

config = AppConfig(name="MyApp", log_level=log_level)
```

## Troubleshooting

### Issue: Import Error

```
ModuleNotFoundError: No module named 'nibandha'
```

**Solution**: Install Nibandha
```bash
pip install nibandha
# or
pip install git+https://github.com/your-org/nibandha.git
```

### Issue: Permission Error

```
PermissionError: [Errno 13] Permission denied: '.Nibandha'
```

**Solution**: Check directory permissions
```bash
chmod -R u+rwX .Nibandha/
```

### Issue: Logs Not Appearing

**Solution**: Check log level
```python
# Lower log level to see more messages
config = AppConfig(name="MyApp", log_level="DEBUG")
```

### Issue: Multiple Applications Conflicting

**Solution**: Use unique app names
```python
# ✅ Correct: Unique names
app1 = Nibandha(AppConfig(name="App1")).bind()
app2 = Nibandha(AppConfig(name="App2")).bind()

# ❌ Wrong: Same name causes conflicts
app1 = Nibandha(AppConfig(name="MyApp")).bind()
app2 = Nibandha(AppConfig(name="MyApp")).bind()  # Conflict!
```

## Summary

Client Integration provides:
- ✅ **Simple Setup**: Minimal code to integrate
- ✅ **Flexible Patterns**: Multiple integration strategies
- ✅ **Framework Agnostic**: Works with any Python framework
- ✅ **Migration Path**: Easy migration from standard logging
- ✅ **Best Practices**: Proven patterns for production use

Now you're ready to integrate Nibandha into your application! Review other module documentation for deeper understanding of specific features.
