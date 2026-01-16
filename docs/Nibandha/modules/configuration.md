# Configuration System

## Overview

Nibandha's configuration system provides flexible, hierarchical configuration management for both global and application-specific settings.

## Configuration Levels

### Level 1: Global Configuration
Location: `.Nibandha/config/`

Shared across all applications:
- `rotation_config.yaml` - Log rotation settings

### Level 2: Application Configuration  
Defined in code via `AppConfig`:
- Application name and identity
- Custom folder structure
- Log level

## AppConfig

### Definition

```python
class AppConfig(BaseModel):
    name: str                          # Required: Application name
    custom_folders: List[str] = []     # Optional: App-specific folders
    log_level: str = "INFO"            # Optional: Logging level
```

### Usage

```python
from nibandha import AppConfig

# Minimal configuration
config = AppConfig(name="MyApp")

# Full configuration
config = AppConfig(
    name="MyApp",
    custom_folders=["data", "output", "models", "cache"],
    log_level="DEBUG"
)
```

### Parameters

#### name (Required)
Application identifier. Used for:
- Logger name: `logging.getLogger(name)`
- Directory name: `.Nibandha/{name}/`
- Log file name: `{name}.log`

```python
# Creates .Nibandha/Amsha/
AppConfig(name="Amsha")

# Creates .Nibandha/Pravaha/
AppConfig(name="Pravaha")
```

#### custom_folders (Optional)
List of application-specific directories to create.

```python
AppConfig(
    name="MyApp",
    custom_folders=[
        "data/raw",            # .Nibandha/MyApp/data/raw/
        "data/processed",      # .Nibandha/MyApp/data/processed/
        "models",              # .Nibandha/MyApp/models/
        "output"               # .Nibandha/MyApp/output/
    ]
)
```

#### log_level (Optional)
Python logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

```python
# Production
AppConfig(name="ProdApp", log_level="WARNING")

# Development
AppConfig(name="DevApp", log_level="DEBUG")
```

## LogRotationConfig

### Definition

```python
class LogRotationConfig(BaseModel):
    enabled: bool = False
    max_size_mb: int = 10
    rotation_interval_hours: int = 24
    archive_retention_days: int = 30
    backup_count: int = 1
    log_data_dir: str = "logs/data"
    archive_dir: str = "logs/archive"
    timestamp_format: str = "%Y-%m-%d"
```

### Configuration Methods

#### Method 1: Programmatic

```python
from nibandha import LogRotationConfig

config = LogRotationConfig(
    enabled=True,
    max_size_mb=100,
    rotation_interval_hours=24,
    archive_retention_days=90,
    backup_count=10,
    timestamp_format="%Y-%m-%d"
)
```

#### Method 2: YAML File

Create `.Nibandha/config/rotation_config.yaml`:

```yaml
enabled: true
max_size_mb: 100  
rotation_interval_hours: 24
archive_retention_days: 90
backup_count: 10
log_data_dir: logs/data
archive_dir: logs/archive
timestamp_format: '%Y-%m-%d'
```

#### Method 3: JSON File

Create `.Nibandha/config/rotation_config.json`:

```json
{
  "enabled": true,
  "max_size_mb": 100,
  "rotation_interval_hours": 24,
  "archive_retention_days": 90,
  "backup_count": 10,
  "log_data_dir": "logs/data",
  "archive_dir": "logs/archive",
  "timestamp_format": "%Y-%m-%d"
}
```

### Loading Priority

Nibandha checks for config files in this order:
1. `rotation_config.yaml`
2. `rotation_config.yml`  
3. `rotation_config.json`
4. If none exist: Interactive prompt (first run)

```python
# Automatic loading
nb = Nibandha(config).bind()  # Loads cached config if exists
```

### Saving Configuration

```python
# Save programmatic config
nb = Nibandha(app_config)
nb.rotation_config = rotation_config
nb._save_rotation_config(rotation_config)  # Writes to .yaml
nb.bind()
```

## Environment-Specific Configuration

### Pattern: Config Factory

```python
# config.py
import os
from nibandha import AppConfig, LogRotationConfig

def get_app_config():
    env = os.getenv("ENV", "development")
    
    if env == "production":
        return AppConfig(
            name="MyApp",
            log_level="WARNING",
            custom_folders=["data", "output"]
        )
    elif env == "staging":
        return AppConfig(
            name="MyApp-Staging",
            log_level="INFO",
            custom_folders=["data", "output", "debug"]
        )
    else:  # development
        return AppConfig(
            name="MyApp-Dev",
            log_level="DEBUG",
            custom_folders=["data", "output", "debug", "temp"]
        )

def get_rotation_config():
    env = os.getenv("ENV", "development")
    
    if env == "production":
        return LogRotationConfig(
            enabled=True,
            max_size_mb=200,
            backup_count=30,
            archive_retention_days=90
        )
    else:  # development/staging
        return LogRotationConfig(
            enabled=True,
            max_size_mb=10,
            backup_count=5,
            archive_retention_days=7
        )

# main.py
from config import get_app_config, get_rotation_config
from nibandha import Nibandha

nb = Nibandha(get_app_config())
nb.rotation_config = get_rotation_config()
nb._save_rotation_config(nb.rotation_config)
nb.bind()
```

## Best Practices

### 1. Centralize Configuration

```python
# ✅ Good: Single config module
# config/nibandha_config.py
from nibandha import AppConfig, LogRotationConfig

APP_CONFIG = AppConfig(name="MyApp", log_level="INFO")
ROTATION_CONFIG = LogRotationConfig(enabled=True, max_size_mb=50)

# main.py
from config.nibandha_config import APP_CONFIG, ROTATION_CONFIG
```

### 2. Use Environment Variables

```python
import os

log_level = os.getenv("LOG_LEVEL", "INFO")
max_size = int(os.getenv("LOG_MAX_SIZE_MB", "50"))

config = AppConfig(name="MyApp", log_level=log_level)
rotation = LogRotationConfig(enabled=True, max_size_mb=max_size)
```

### 3. Validate Configuration

```python
from pydantic import ValidationError

try:
    config = AppConfig(name="MyApp", log_level="INVALID")
except ValidationError as e:
    print(f"Invalid config: {e}")
```

### 4. Document Defaults

```python
# config.py
"""
Application Configuration

Default Settings:
- Log Level: INFO
- Rotation: Enabled
- Max Size: 100MB
- Retention: 30 days
- Backup Count: 10
"""

DEFAULT_APP_CONFIG = AppConfig(name="MyApp", log_level="INFO")
DEFAULT_ROTATION = LogRotationConfig(
    enabled=True,
    max_size_mb=100,
    archive_retention_days=30,
    backup_count=10
)
```

## Summary

Configuration System provides:
- ✅ **Flexible Configuration**: Programmatic, file-based, or interactive
- ✅ **Environment-Specific**: Easy to customize per environment
- ✅ **Type-Safe**: Pydantic validation
- ✅ **Persistent**: Cached configuration across runs

Next: [Client Integration](client-integration.md) guide shows how to integrate Nibandha into your application.
