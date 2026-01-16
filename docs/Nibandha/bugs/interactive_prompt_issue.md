# Bug: Interactive Prompts in Non-Interactive Environments

**Bug ID:** NIB-001  
**Title:** Nibandha prompts for user input during bind(), breaking non-interactive deployments  
**Severity:** Critical  
**Status:** Reported

---

## Problem Description

Nibandha's `bind()` method prompts for user input when no rotation config file exists. This breaks deployments in non-interactive environments such as:
- Docker containers
- CI/CD pipelines
- Systemd services
- FastAPI applications
- Background workers
- Any headless/automated environment

## Steps to Reproduce

1. Start with no `.Nibandha/config/rotation_config.yaml` file
2. Initialize Nibandha in code:
   ```python
   from nibandha import Nibandha, AppConfig
   
   config = AppConfig(name="MyApp")
   nb = Nibandha(config).bind()  # <-- Blocks here waiting for input
   ```
3. Observe interactive prompt:
   ```
   📋 Log Rotation Configuration
   ==================================================
   Enable log rotation? (y/n) [n]:
   ```

## Expected Behavior

Backend libraries should **NEVER** prompt for user input during initialization. They should:
1. Use sensible defaults if no config exists
2. Allow programmatic configuration only
3. Work in completely non-interactive environments

## Actual Behavior

`Nibandha.bind()` calls `_prompt_and_cache_rotation_config()` which uses `input()` to prompt the user. This:
- **Blocks** execution indefinitely in non-interactive environments
- **Fails** in Docker containers with no TTY
- **Breaks** CI/CD pipelines
- **Prevents** use in production API servers

## Environment

- **OS:** Linux (Ubuntu 22.04)
- **Python:** 3.12
- **Nibandha:** Installed from `git+https://github.com/NikhilVijayakumar/Nibandha.git@main`
- **Use Case:** Backend library (Pravaha) used in FastAPI applications

## Impact

### High Impact Use Cases:
1. **Docker Deployments:** Container startup hangs waiting for input
2. **Kubernetes:** Pods fail to start
3. **CI/CD:** Build pipelines hang
4. **Systemd Services:** Service activation fails
5. **Cloud Functions:** Lambda/Cloud Run timeout
6. **FastAPI Apps:** Server initialization blocks

### Real-World Example:

```python
# FastAPI application
from fastapi import FastAPI
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager

# This hangs in Docker if rotation config doesn't exist
logger = PravphaLoggingManager.get_logger()  # Calls Nibandha.bind() internally

app = FastAPI()  # Never reached - server doesn't start
```

## Stack Trace

```
File "/path/to/nibandha/core.py", line 49, in bind
    self.rotation_config = self._prompt_and_cache_rotation_config()
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/path/to/nibandha/core.py", line 85, in _prompt_and_cache_rotation_config
    enable = input("Enable log rotation? (y/n) [n]: ").strip().lower()
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

## Recommended Fix

### Option 1: Default to No Rotation (Simplest)

```python
def _prompt_and_cache_rotation_config(self) -> LogRotationConfig:
    """Load or create rotation config - NO user prompts."""
    config_path = self.workspace_root / "config" / "rotation_config.yaml"
    
    if config_path.exists():
        # Load existing config
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            return LogRotationConfig(**data)
    else:
        # Default to disabled - no prompts
        config = LogRotationConfig(enabled=False)
        
        # Optionally cache the default
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config.dict(), f)
        
        return config
```

### Option 2: Create Default Enabled Config

```python
def _prompt_and_cache_rotation_config(self) -> LogRotationConfig:
    """Load or create rotation config - NO user prompts."""
    config_path = self.workspace_root / "config" / "rotation_config.yaml"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            return LogRotationConfig(**data)
    else:
        # Create production-ready defaults
        config = LogRotationConfig(
            enabled=True,
            max_size_mb=50,
            rotation_interval_hours=24,
            archive_retention_days=30,
            log_data_dir='logs/data',
            archive_dir='logs/archive',
            timestamp_format='%Y-%m-%d'  # Daily, not per-restart
        )
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            yaml.dump(config.dict(), f)
        
        return config
```

### Option 3: Environment Variable Override

```python
import os

def _prompt_and_cache_rotation_config(self) -> LogRotationConfig:
    """Load or create rotation config - respects NIBANDHA_NO_PROMPTS env var."""
    config_path = self.workspace_root / "config" / "rotation_config.yaml"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            return LogRotationConfig(**data)
    
    # Check if we're in non-interactive mode
    if os.getenv('NIBANDHA_NO_PROMPTS', '').lower() in ('1', 'true', 'yes'):
        # Use defaults without prompting
        config = LogRotationConfig(enabled=True, ...)
        # ... cache and return
    else:
        # Original interactive prompt (for CLI tools only)
        enable = input("Enable log rotation? (y/n) [n]: ").strip().lower()
        # ...
```

## Priority

**CRITICAL** - This bug prevents Nibandha from being used in:
- Production deployments
- Containerized environments
- Backend services
- Automated systems

## Workaround (Pravaha Implementation)

Pravaha has implemented a workaround by ensuring rotation config exists **before** calling `Nibandha.bind()`:

```python
# In PravphaLoggingManager.initialize()
from pravaha.domain.logging.utils.rotation_utils import LogRotationUtils

# Ensure config exists to prevent prompts
config_path = Path(".Nibandha/config/rotation_config.yaml")
if not config_path.exists():
    LogRotationUtils.setup_rotation()  # Creates default config

# Now safe to initialize Nibandha
nb = Nibandha(config).bind()  # No prompts
```

This workaround is **not ideal** because:
1. Every library using Nibandha must implement this
2. It requires knowledge of Nibandha internals
3. The fix belongs in Nibandha itself

## Related Issues

This violates the principle that **libraries should be non-interactive by default**. Interactive configuration is appropriate for:
- CLI tools
- Setup wizards
- Interactive notebooks

But **never** for:
- Backend libraries
- API frameworks
- Background workers

## Proposed Solution

**Recommended:** Option 2 (production-ready defaults)

Benefits:
1. ✅ Works in all environments
2. ✅ No breaking changes for existing users
3. ✅ Sensible defaults for production
4. ✅ Still allows customization via config file
5. ✅ No dependency on environment variables

---

**Reported by:** Pravaha Development Team  
**Date:** 2026-01-15  
**Affected Projects:** Pravaha, potentially Amsha and other Nibandha users
