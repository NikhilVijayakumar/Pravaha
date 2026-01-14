# Nibandha Integration Guide

## Overview

Pravaha uses [Nibandha](https://github.com/NikhilVijayakumar/Nibandha) for centralized logging and storage management. All logging in Pravaha flows through Nibandha's logger, providing unified log files with automatic rotation and archival capabilities.

## Directory Structure

When initialized, Nibandha creates the following structure:

```
.Nibandha/
├── config/
│   └── rotation_config.yaml       # Log rotation configuration
└── Pravaha/
    ├── logs/
    │   ├── data/                   # Active log files (timestamped)
    │   └── archive/                # Archived logs (rotated files)
    ├── workflow/
    │   ├── details/                # Workflow definitions
    │   └── run/                    # Workflow run data
    └── config/                     # Pravaha-specific config
```

## For Pravaha Contributors

### Using the Logger

All Pravaha modules use the centralized `PravphaLoggingManager`:

```python
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager

# Get logger instance (auto-initializes if needed)
logger = PravphaLoggingManager.get_logger()

# Use standard logging levels
logger.debug("Detailed diagnostic information")
logger.info("General informational messages")
logger.warning("Warning messages for recoverable issues")
logger.error("Error messages for failures")
```

### Logging Guidelines

**Log Levels:**
- **DEBUG**: Low-level operations (file I/O, state updates in repositories)
- **INFO**: Business logic events (workflow created, run started, node completed)
- **WARNING**: Recoverable issues (invalid files skipped, workflow not found)
- **ERROR**: Failures requiring attention (exceptions, validation errors)

**Best Practices:**
- Include relevant context (IDs, paths, status values)
- Log at decision points and state transitions
- Use f-strings for formatted log messages
- Don't log sensitive data (passwords, tokens)

**Example:**
```python
# Good logging
self.logger.info(f"Workflow created successfully: {workflow.id}")
self.logger.debug(f"Saving workflow to file: {file_path}")
self.logger.error(f"Failed to save workflow {workflow.id}: {e}")

# Avoid
logger.info("Workflow created")  # Too vague
logger.debug(f"Data: {sensitive_token}")  # Contains sensitive data
```

---

## For Client Applications

Client applications (like Akashavani or Sangama) that use Pravaha should set up log rotation at startup.

### Basic Setup

The simplest integration requires no configuration:

```python
from pravaha.domain.api.factory.api_factory import create_fastapi_app

# Nibandha initializes automatically when first logger is used
app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager,
    title="My Application"
)
```

Logs will be created with default settings (no rotation).

---

### Log Rotation Setup (Recommended)

For production deployments, configure log rotation at application startup:

```python
from pravaha.domain.logging.utils.rotation_utils import LogRotationUtils
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager
from pravaha.domain.api.factory.api_factory import create_fastapi_app

# 1. Setup rotation configuration (one-time at startup)
LogRotationUtils.setup_rotation(
    max_size_mb=50,              # Rotate when log exceeds 50MB
    rotation_interval_hours=24,   # Or every 24 hours
    archive_retention_days=30     # Keep archives for 30 days
)

# 2. Initialize logging
logger = PravphaLoggingManager.get_logger()
logger.info("Application starting...")

# 3. Create app
app = create_fastapi_app(...)
```

---

### Scheduling Log Rotation

Nibandha provides utilities for rotation, but **does not automatically trigger rotation**. The client application must schedule rotation checks.

**Option 1: FastAPI Background Task (Recommended)**

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from pravaha.domain.logging.utils.rotation_utils import LogRotationUtils
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager

async def rotation_scheduler():
    """Background task to check log rotation every hour."""
    while True:
        await asyncio.sleep(3600)  # Check every hour
        try:
            nb = PravphaLoggingManager.get_instance()
            if nb and LogRotationUtils.check_and_rotate(nb):
                logger = PravphaLoggingManager.get_logger()
                logger.info("Log rotation performed")
            
            # Cleanup old archives
            if nb:
                deleted = LogRotationUtils.cleanup_old_logs(nb)
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} old archive file(s)")
        except Exception as e:
            logger.error(f"Error in rotation scheduler: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task = asyncio.create_task(rotation_scheduler())
    yield
    # Shutdown
    task.cancel()

app = FastAPI(lifespan=lifespan)
```

**Option 2: System Cron Job**

Create a separate script for rotation and trigger via cron:

```python
# rotate_logs.py
from pravaha.domain.logging.utils.rotation_utils import LogRotationUtils
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager

nb = PravphaLoggingManager.get_instance()
if nb:
    if LogRotationUtils.check_and_rotate(nb):
        print("Log rotated successfully")
    
    deleted = LogRotationUtils.cleanup_old_logs(nb)
    print(f"Cleaned up {deleted} old archive file(s)")
```

Crontab entry (run every hour):
```bash
0 * * * * /path/to/venv/bin/python /path/to/rotate_logs.py
```

**Option 3: APScheduler**

```python
from apscheduler.schedulers.background import BackgroundScheduler
from pravaha.domain.logging.utils.rotation_utils import LogRotationUtils
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager

def check_rotation():
    nb = PravphaLoggingManager.get_instance()
    if nb:
        LogRotationUtils.check_and_rotate(nb)
        LogRotationUtils.cleanup_old_logs(nb)

scheduler = BackgroundScheduler()
scheduler.add_job(check_rotation, 'interval', hours=1)
scheduler.start()

# On shutdown
scheduler.shutdown()
```

---

### Configuration Options

All rotation parameters are configurable:

```python
LogRotationUtils.setup_rotation(
    max_size_mb=100,              # Default: 50MB
    rotation_interval_hours=12,    # Default: 24 hours
    archive_retention_days=60      # Default: 30 days
)
```

The configuration is stored in `.Nibandha/config/rotation_config.yaml`.

---

### Manual Rotation

You can also trigger rotation manually:

```python
from pravaha.domain.logging.utils.rotation_utils import LogRotationUtils
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager

nb = PravphaLoggingManager.get_instance()
if nb:
    # Check if rotation is needed
    if nb.should_rotate():
        nb.rotate_logs()
        print("Logs rotated")
    
    # Clean up old archives
    deleted_count = nb.cleanup_old_archives()
    print(f"Cleaned up {deleted_count} archive(s)")
```

---

## Log File Format

Log messages use a consistent format:

```
<timestamp> | <logger_name> | <level> | <message>
```

Example:
```
2026-01-14 07:12:23,989 | Pravaha | INFO | Nibandha initialized at .Nibandha\Pravaha
2026-01-14 07:12:23,990 | Pravaha | INFO | Workflow created successfully: abc-123
2026-01-14 07:12:24,123 | Pravaha | WARNING | Skipping invalid workflow file: corrupted.json
2026-01-14 07:12:25,456 | Pravaha | ERROR | Failed to save run xyz-789: Permission denied
```

---

## Troubleshooting

### Issue: No log files created

**Solution**: Ensure the logger is initialized:
```python
logger = PravphaLoggingManager.get_logger()
logger.info("Test message")
```

### Issue: Logs not rotating

**Possible causes:**
1. No rotation scheduler configured → See "Scheduling Log Rotation" above
2. Rotation config missing → Run `LogRotationUtils.setup_rotation()`
3. File size/time thresholds not met → Check `.Nibandha/config/rotation_config.yaml`

### Issue: Permission errors

**Solution**: Ensure write permissions for `.Nibandha/` directory

### Issue: Interactive prompts during rotation setup

**This should not happen** in the current implementation. If you encounter prompts, ensure you're calling `LogRotationUtils.setup_rotation()` before any logging operations.

---

## Architecture

### Components

1. **`PravphaLoggingManager`**: Singleton wrapper around Nibandha
   - Auto-initializes on first use
   - Provides centralized logger instance
   - Located: `pravaha.domain.logging.manager.logging_manager`

2. **`LogRotationUtils`**: Utility class for rotation management
   - Creates rotation configuration
   - Provides rotation check/cleanup methods
   - Located: `pravaha.domain.logging.utils.rotation_utils`

3. **Nibandha**: Underlying logging library
   - Manages workspace structure
   - Handles file rotation and archival
   - Dependency: `git+https://github.com/NikhilVijayakumar/Nibandha.git@main`

### Design Decisions

- **Library-level responsibility**: Pravaha initializes Nibandha but does NOT auto-rotate logs
- **Client-level responsibility**: Applications using Pravaha schedule rotation as needed
- **Default configuration**: Production-ready defaults (50MB, 24hrs, 30-day retention)
- **Singleton pattern**: Ensures one Nibandha instance per application runtime

---

## Reporting Issues

### Nibandha Library Issues

If you encounter issues with Nibandha itself (the logging library), create a bug report or change request:

- **Bugs**: `docs/Nibandha/bugs/`
- **Feature Requests**: `docs/Nibandha/CR/`

**Do NOT modify** the `Nibandha-main/` directory directly.

### Pravaha Integration Issues

For issues with Pravaha's use of Nibandha, file a standard issue in the Pravaha repository.

---

## Summary

**For Contributors:**
- Use `PravphaLoggingManager.get_logger()` for all logging
- Follow logging level guidelines (DEBUG/INFO/WARNING/ERROR)
- Include context in log messages

**For Client Applications:**
- Call `LogRotationUtils.setup_rotation()` at startup
- Schedule rotation checks (FastAPI background task, cron, or APScheduler)
- Use default configurations unless specific requirements exist

**Key Files:**
- Logger: `pravaha/domain/logging/manager/logging_manager.py`
- Utils: `pravaha/domain/logging/utils/rotation_utils.py`
- Example: `docs/examples/example_rotation_scheduler.py`
