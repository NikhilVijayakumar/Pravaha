# Logging Module

## Overview

The Logging Module is Nibandha's core feature, providing automatic logger configuration and handler management for all applications. It solves common logging challenges including handler attachment, log leakage, and child logger propagation.

## Architecture

### Handler Attachment Strategy

Nibandha attaches handlers **directly to the named logger**, not to Python's root logger:

```python
# ❌ WRONG: Python's logging.basicConfig() (old approach)
logging.basicConfig(handlers=[file_handler, console_handler])
logger = logging.getLogger("MyApp")  # Handlers on ROOT, not "MyApp"

# ✅ CORRECT: Nibandha's approach
logger = logging.getLogger("MyApp")
logger.addHandler(file_handler)      # Handler on "MyApp" directly
logger.addHandler(console_handler)
logger.propagate = False              # Prevent leakage to ROOT
```

**Why This Matters**:
- Ensures logs are written to application's file, not lost
- Prevents log leakage between applications
- Supports child logger propagation within app namespace

### Logger Hierarchy

```
Python Root Logger
└── [No Nibandha handlers]          # Clean separation

Named Logger ("MyApp")
├── FileHandler → .Nibandha/MyApp/logs/MyApp.log
├── ConsoleHandler → stdout
├── propagate = False               # Stops here
└── Child Loggers
    ├── MyApp.module1               # Inherits handlers
    ├── MyApp.module2.submodule     # Inherits handlers
    └── MyApp.utils                 # Inherits handlers
```

## Core Features

### 1. Named Logger Creation

Each application gets a properly configured named logger:

```python
from nibandha import Nibandha, AppConfig

config = AppConfig(name="MyApp")
nb = Nibandha(config).bind()

# Named logger: logging.getLogger("MyApp")
nb.logger.info("Application started")
nb.logger.warning("Warning message")
nb.logger.error("Error occurred")
```

**Logger Properties**:
- **Name**: Matches `AppConfig.name` (e.g., "Amsha", "Pravaha")
- **Level**: From `AppConfig.log_level` (default: INFO)
- **Propagate**: Set to `False` to prevent log leakage
- **Handlers**: FileHandler + Console Handler attached

### 2. File Handler

Automatically configured file handler writes logs to application's directory:

**Without Log Rotation** (default):
```
.Nibandha/MyApp/logs/MyApp.log      # Single rolling file
```

**With Log Rotation**:
```
.Nibandha/MyApp/logs/data/2026-01-15.log    # Timestamped
```

**File Handler Configuration**:
```python
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(
    logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
)
logger.addHandler(file_handler)
```

**Format Example**:
```
2026-01-15 08:15:30,123 | MyApp | INFO | Application started
2026-01-15 08:15:31,456 | MyApp.module | WARNING | Cache miss
2026-01-15 08:15:32,789 | MyApp.service | ERROR | Connection failed
```

### 3. Console Handler

StreamHandler for development and debugging:

```python
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
)
logger.addHandler(console_handler)
```

**Output**: Logs appear in both file AND console (stdout).

### 4. Child Logger Support

Child loggers automatically inherit parent's handlers:

```python
# Parent logger (configured by Nibandha)
nb = Nibandha(AppConfig(name="MyApp")).bind()

# Child loggers (inherit handlers)
import logging
module_logger = logging.getLogger("MyApp.module")
module_logger.info("From module")  # Goes to MyApp.log

service_logger = logging.getLogger("MyApp.service.api")
service_logger.warning("From service")  # Also goes to MyApp.log
```

**Hierarchy Example**:
```
MyApp                           # Root app logger (handlers attached)
├── MyApp.module                # Child (inherits)
├── MyApp.service               # Child (inherits)
│   └── MyApp.service.api       # Grandchild (inherits)
└── MyApp.utils                 # Child (inherits)
```

All child loggers write to **same log file** as parent.

### 5. No Propagation to Root

Nibandha sets `propagate=False` to prevent log leakage:

```python
self.logger.propagate = False
```

**Benefits**:
- Logs stay within application namespace
- No interference with other applications' loggers
- No duplicate log entries
- Clean separation between apps

## Log Levels

### Configuration

Set log level via `AppConfig`:

```python
# Production: Only warnings and errors
config = AppConfig(name="ProdApp", log_level="WARNING")

# Development: Verbose logging
config = AppConfig(name="DevApp", log_level="DEBUG")

# Default: INFO level
config = AppConfig(name="DefaultApp")  # log_level="INFO"
```

### Supported Levels

| Level | Numeric Value | Usage |
|-------|---------------|-------|
| DEBUG | 10 | Detailed diagnostic information |
| INFO | 20 | General informational messages |
| WARNING | 30 | Warning messages (default) |
| ERROR | 40 | Error messages |
| CRITICAL | 50 | Critical errors |

### Example Usage

```python
logger = nb.logger

logger.debug("Detailed debug info")       # DEBUG
logger.info("User logged in")             # INFO
logger.warning("Deprecated API used")     # WARNING
logger.error("Database connection failed") # ERROR
logger.critical("System shutdown")        # CRITICAL
```

## Log Format

### Standard Format

Nibandha uses a consistent format across all applications:

```
%(asctime)s | %(name)s | %(levelname)s | %(message)s
```

**Components**:
- `%(asctime)s`: Timestamp (YYYY-MM-DD HH:MM:SS,mmm)
- `%(name)s`: Logger name (e.g., "MyApp.module")
- `%(levelname)s`: Log level (INFO, WARNING, ERROR, etc.)
- `%(message)s`: Log message

**Example Output**:
```
2026-01-15 08:15:30,123 | Amsha | INFO | Crew task started
2026-01-15 08:15:31,456 | Amsha.agents | DEBUG | Agent initialized: Researcher
2026-01-15 08:15:32,789 | Pravaha.api | WARNING | Rate limit approaching
2026-01-15 08:15:33,012 | Pravaha.workflow | ERROR | Task execution failed
```

### Custom Format (Advanced)

Override format by modifying handlers directly:

```python
nb = Nibandha(config).bind()

# Custom format
custom_format = '%(levelname)s [%(name)s] %(message)s'
formatter = logging.Formatter(custom_format)

# Apply to handlers
for handler in nb.logger.handlers:
    handler.setFormatter(formatter)
```

## Integration Patterns

### Pattern 1: Single Application

```python
from nibandha import Nibandha, AppConfig

# Initialize once at application startup
config = AppConfig(name="MyApp")
nibandha_instance = Nibandha(config).bind()

# Use throughout application
def my_function():
    nibandha_instance.logger.info("Function called")

class MyClass:
    def __init__(self):
        nibandha_instance.logger.info("Class initialized")
```

### Pattern 2: Module-Level Logger

```python
# app/__init__.py
from nibandha import Nibandha, AppConfig

_nibandha = Nibandha(AppConfig(name="MyApp")).bind()

def get_logger():
    """Get application logger"""
    return _nibandha.logger

# app/module.py
from app import get_logger

logger = get_logger()
logger.info("Module loaded")
```

### Pattern 3: Child Loggers per Module

```python
# app/__init__.py
from nibandha import Nibandha, AppConfig
Nibandha(AppConfig(name="MyApp")).bind()

# app/module_a.py
import logging
logger = logging.getLogger("MyApp.module_a")
logger.info("Module A activity")

# app/module_b.py
import logging
logger = logging.getLogger("MyApp.module_b")
logger.info("Module B activity")

# Both write to same file with different logger names
```

### Pattern 4: Multi-Application

```python
# services/amsha_service.py
from nibandha import Nibandha, AppConfig
amsha_nb = Nibandha(AppConfig(name="Amsha")).bind ()
amsha_nb.logger.info("Amsha service started")

# services/pravaha_service.py
from nibandha import Nibandha, AppConfig
pravaha_nb = Nibandha(AppConfig(name="Pravaha")).bind()
pravaha_nb.logger.info("Pravaha service started")

# Result: Separate log files
# .Nibandha/Amsha/logs/Amsha.log
# .Nibandha/Pravaha/logs/Pravaha.log
```

## Bug Fix: Handler Attachment

### The Problem (Pre-Fix)

**Original Implementation** (caused empty log files):
```python
# ❌ Old approach - handlers on ROOT logger
logging.basicConfig(
    level=self.config.log_level,
    handlers=[file_handler, console_handler]
)
self.logger = logging.getLogger(self.config.name)
```

**Issue**: `basicConfig()` attaches handlers to Python's ROOT logger, not the named logger.

**Impact**:
- Log files created but remain **EMPTY** (0 bytes)
- Console logs work (StreamHandler on ROOT visible)
- File logs don't work (FileHandler on ROOT not reachable when `propagate=False`)

### The Solution (Current)

**New Implementation** (logs written correctly):
```python
# ✅ New approach - handlers on named logger
self.logger = logging.getLogger(self.config.name)
self.logger.setLevel(self.config.log_level)

file_handler = logging.FileHandler(log_file)
console_handler = logging.StreamHandler()

self.logger.addHandler(file_handler)      # Direct attachment
self.logger.addHandler(console_handler)
self.logger.propagate = False
```

**Result**:
- ✅ Log files contain actual data
- ✅ Child loggers inherit handlers
- ✅ Works correctly with `propagate=False`
- ✅ No dependency on ROOT logger

## Best Practices

### 1. Use Nibandha's Logger

```python
# ✅ Good: Use Nibandha's configured logger
nb = Nibandha(config).bind()
nb.logger.info("Message")

# ❌ Bad: Create separate logger
import logging
logger = logging.getLogger(__name__)  # Bypasses Nibandha
```

### 2. Child Loggers for Modules

```python
# ✅ Good: Child loggers inherit configuration
import logging
module_logger = logging.getLogger("MyApp.module")

# ❌ Bad: Separate root logger
module_logger = logging.getLogger("module")  # Not in namespace
```

### 3. Set Log Level Appropriately

```python
# ✅ Good: Environment-specific levels
if env == "production":
    log_level = "WARNING"
elif env == "development":
    log_level = "DEBUG"
else:
    log_level = "INFO"

config = AppConfig(name="MyApp", log_level=log_level)
```

### 4. Structured Logging

```python
# ✅ Good: Structured log messages
logger.info(f"User {user_id} logged in from {ip_address}")
logger.error(f"Database query failed: {query}", exc_info=True)

# ❌ Bad: Unstructured messages
logger.info("something happened")
logger.error("error")
```

### 5. Use exc_info for Exceptions

```python
# ✅ Good: Include full traceback
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)

# ❌ Bad: Missing stack trace
except Exception as e:
    logger.error(str(e))  # Loses context
```

## Troubleshooting

### Empty Log Files

**Symptom**: Log file exists but has 0 bytes.

**Cause**: Using old `basicConfig()` approach or handlers not flushed.

**Solution**: Ensure using Nibandha v1.0.1+ (with handler fix):
```bash
pip install --upgrade nibandha
```

### Duplicate Log Entries

**Symptom**: Each log message appears twice.

**Cause**: `propagate=True` causing logs to reach both named logger and ROOT.

**Solution**: Nibandha sets `propagate=False` automatically. If overriding:
```python
nb.logger.propagate = False  # Ensure this is set
```

### Child Logger Not Writing

**Symptom**: Child logger messages don't appear in log file.

**Cause**: Child logger name doesn't match parent namespace.

**Solution**: Ensure child logger starts with parent name:
```python
# ✅ Correct child logger
logging.getLogger("MyApp.module")

# ❌ Incorrect child logger
logging.getLogger("module")  # Not in MyApp namespace
```

### Log Level Not Working

**Symptom**: DEBUG messages not appearing.

**Cause**: Log level set too high.

**Solution**: Set level explicitly:
```python
# Set level after binding
nb = Nibandha(config).bind()
nb.logger.setLevel(logging.DEBUG)
```

## Summary

The Logging Module provides:
- ✅ **Automatic Configuration**: No manual logging setup needed
- ✅ **Proper Handler Attachment**: Logs written to correct files
- ✅ **Application Isolation**: No log leakage between apps
- ✅ **Child Logger Support**: Module loggers inherit configuration
- ✅ **Standard Format**: Consistent logging across ecosystem

Next: Learn about [Log Rotation](log-rotation.md) for managing log file sizes.
