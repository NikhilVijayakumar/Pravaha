# Log Rotation

## Overview

Log Rotation is Nibandha's automatic log management system that prevents disk space issues by rotating, archiving, and cleaning up log files based on configurable triggers.

## Features

- **Size-Based Rotation**: Rotate when log file exceeds configured size (e.g., 50MB)
- **Time-Based Rotation**: Rotate after configured interval (e.g., 24 hours)
- **Automatic Archival**: Move rotated logs to archive directory
- **Backup Count Limit**: Keep only N most recent backup files
- **Time Retention**: Remove archives older than configured period
- **Timestamped Files**: Daily log files with format `YYYY-MM-DD.log`

## Configuration

### LogRotationConfig Parameters

```python
class LogRotationConfig(BaseModel):
    enabled: bool = False                    # Enable/disable rotation
    max_size_mb: int = 10                    # Size trigger (MB)
    rotation_interval_hours: int = 24        # Time trigger (hours)
    archive_retention_days: int = 30         # Archive cleanup (days)
    backup_count: int = 1                    # Max backups to keep
    log_data_dir: str = "logs/data"          # Active logs directory
    archive_dir: str = "logs/archive"        # Archive directory
    timestamp_format: str = "%Y-%m-%d"      # Daily consolidation
```

**All parameters are overridable by clients.**

### Default Behavior

**Without Rotation** (default):
```python
config = AppConfig(name="MyApp")
nb = Nibandha(config).bind()

# Creates: .Nibandha/MyApp/logs/MyApp.log (single file)
```

**With Rotation Enabled**:
```python
config = AppConfig(name="MyApp")
rotation = LogRotationConfig(enabled=True)

nb = Nibandha(config)
nb.rotation_config = rotation
nb._save_rotation_config(rotation)
nb.bind()

# Creates:
# .Nibandha/MyApp/logs/data/2026-01-15.log (current)
# .Nibandha/MyApp/logs/archive/ (for rotated files)
```

## Setup Methods

### Method 1: Interactive Prompt

First-time initialization prompts for settings:

```python
from nibandha import Nibandha, AppConfig

config = AppConfig(name="MyApp")
nb = Nibandha(config).bind()

# Prompts:
# 📋 Log Rotation Configuration
# ==================================================
# Enable log rotation? (y/n) [n]: y
# Max log size in MB before rotation [10]: 50
# Rotation interval in hours [24]: 24
# Archive retention in days [30]: 30
# Number of backup files to keep in archive [1]: 5
# ✅ Configuration saved to .Nibandha/config/rotation_config.yaml
```

**Subsequent runs**: Configuration is cached, no prompts.

### Method 2: Programmatic Configuration

Skip prompts with direct configuration:

```python
from nibandha import Nibandha, AppConfig, LogRotationConfig

# Define rotation policy
rotation_config = LogRotationConfig(
    enabled=True,
    max_size_mb=100,                  # Rotate at 100MB
    rotation_interval_hours=24,       # OR every 24 hours
    archive_retention_days=90,        # Keep 90 days
    backup_count=10                   # Keep 10 most recent backups
)

# Apply to Nibandha instance
config = AppConfig(name="MyApp")
nb = Nibandha(config)
nb.rotation_config = rotation_config
nb._save_rotation_config(rotation_config)  # Cache for future runs
nb.bind()
```

### Method 3: Config File

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

Nibandha loads this automatically on `bind()`.

### Method 4: Client Utility (Amsha Pattern)

Create a setup utility for your application:

```python
# myapp/rotation_setup.py
from nibandha import Nibandha, AppConfig, LogRotationConfig
from pathlib import Path
import yaml

def setup_rotation(
    enabled=True,
    max_size_mb=50,
    rotation_interval=24,
    retention_days=30,
    backup_count=5,
    timestamp_format='%Y-%m-%d'
):
    """Setup log rotation for MyApp"""
    config_dir = Path(".Nibandha/config")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    rotation_config = {
        'enabled': enabled,
        'max_size_mb': max_size_mb,
        'rotation_interval_hours': rotation_interval,
        'archive_retention_days': retention_days,
        'backup_count': backup_count,
        'log_data_dir': 'logs/data',
        'archive_dir': 'logs/archive',
        'timestamp_format': timestamp_format
    }
    
    with open(config_dir / 'rotation_config.yaml', 'w') as f:
        yaml.dump(rotation_config, f, default_flow_style=False)

# Usage in application startup
if __name__ == "__main__":
    setup_rotation(
        enabled=True,
        max_size_mb=100,
        backup_count=10
    )
    
    # Now bind normally
    nb = Nibandha(AppConfig(name="MyApp")).bind()
```

## Directory Structure

### With Rotation Enabled

```
.Nibandha/
├── config/
│   └── rotation_config.yaml      # Cached configuration
│
└── MyApp/
    └── logs/
        ├── data/                  # Active logs
        │   ├── 2026-01-15.log     # Today's log
        │   └── 2026-01-14.log     # Yesterday (if not rotated)
        │
        └── archive/               # Rotated logs
            ├── 2026-01-13.log
            ├── 2026-01-12.log
            ├── 2026-01-11.log
            ├── 2026-01-10.log
            └── 2026-01-09.log
```

### Timestamp Format

**Default Format**: `%Y-%m-%d` (daily consolidation)

**Example Filenames**:
- `2026-01-15.log` - January 15, 2026
- `2026-01-14.log` - January 14, 2026
- `2026-12-31.log` - December 31, 2026

**Why Daily Format?**:
- Same-day logs consolidate into one file
- New file created only on date change or size limit
- Better log organization for daily review

**Custom Formats**:
```python
# Weekly rotation
LogRotationConfig(timestamp_format="%Y-W%W")  # 2026-W03.log

# Monthly rotation
LogRotationConfig(timestamp_format="%Y-%m")   # 2026-01.log

# Hourly rotation (not recommended)
LogRotationConfig(timestamp_format="%Y-%m-%d_%H")  # 2026-01-15_14.log
```

## Rotation Triggers

### Trigger 1: Size Limit

Rotate when current log file exceeds `max_size_mb`:

```python
rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=50  # Rotate at 50MB
)

# Log file grows...
# At 50MB: Rotation triggered
# Result:
#   - 50MB file moved to archive/
#   - New empty file created in data/
```

### Trigger 2: Time Interval

Rotate after `rotation_interval_hours` elapsed:

```python
rotation = LogRotationConfig(
    enabled=True,
    rotation_interval_hours=24  # Rotate every 24 hours
)

# Log created at 2026-01-15 08:00:00
# At 2026-01-16 08:00:00: Rotation triggered
```

### Combined Triggers

**Either** condition triggers rotation:

```python
rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=100,              # Rotate at 100MB
    rotation_interval_hours=168   # OR every week
)

# Rotates when FIRST condition is met:
# - 100MB size limit reached, OR
# - 168 hours (7 days) elapsed
```

## Rotation Workflow

### Automatic Rotation

```python
nb = Nibandha(config).bind()

# Client application checks periodically
if nb.should_rotate():
    nb.rotate_logs()
```

### Manual Rotation

Force rotation regardless of triggers:

```python
# Force rotation (e.g., during deployment)
nb.rotate_logs()

# Result:
#   - Current log moved to archive/
#   - New timestamped log created
#   - Logger handlers updated to new file
```

### Rotation Steps

When `rotate_logs()` is called:

1. **Close Current Handlers**: All file handlers on logger are closed
2. **Move to Archive**: Current log file moved from `logs/data/` to `logs/archive/`
3. **Create New Log**: New timestamped log file created in `logs/data/`
4. **Attach Handlers**: New file handler created and attached to logger
5. **Log Event**: "Log rotated" message written to new file

```python
# Before rotation
.Nibandha/MyApp/logs/data/2026-01-15.log  (current, 60MB)

# After rotation
.Nibandha/MyApp/logs/archive/2026-01-15.log  (archived, 60MB)
.Nibandha/MyApp/logs/data/2026-01-15.log     (new, <1KB)
```

## Archive Cleanup

Nibandha provides dual cleanup strategies:

### Strategy 1: Backup Count Limit

Keep **N most recent** backup files:

```python
rotation = LogRotationConfig(
    enabled=True,
    backup_count=5  # Keep only 5 most recent backups
)

# Archives sorted by modification time (newest first):
# 1. 2026-01-15.log  ← Keep
# 2. 2026-01-14.log  ← Keep
# 3. 2026-01-13.log  ← Keep
# 4. 2026-01-12.log  ← Keep
# 5. 2026-01-11.log  ← Keep
# 6. 2026-01-10.log  ← DELETE (exceeds backup_count)
# 7. 2026-01-09.log  ← DELETE (exceeds backup_count)
```

### Strategy 2: Time-Based Retention

Remove archives **older than** retention period:

```python
rotation = LogRotationConfig(
    enabled=True,
    archive_retention_days=30  # Delete files older than 30 days
)

# Today: 2026-01-15
# Cutoff: 2025-12-16

# 2026-01-10.log  ← Keep (within 30 days)
# 2025-12-20.log  ← Keep (within 30 days)
# 2025-12-15.log  ← DELETE (older than 30 days)
# 2025-11-01.log  ← DELETE (older than 30 days)
```

### Combined Cleanup

Both strategies are applied:

```python
rotation = LogRotationConfig(
    enabled=True,
    backup_count=10,             # Keep max 10 backups
    archive_retention_days=90    # AND remove anything older than 90 days
)

# Whichever is more restrictive applies:
# - If 10 files within 90 days: Keeps 10 most recent
# - If 15 files within 90 days: Keeps 10 most recent (backup_count limit)
# - If 5 files, 2 older than 90 days: Keeps 3 recent, deletes 2 old
```

### Manual Cleanup

```python
# Run cleanup manually
deleted_count = nb.cleanup_old_archives()
nb.logger.info(f"Cleaned up {deleted_count} old archives")
```

### Scheduled Cleanup

**Linux/Mac - Cron**:
```bash
# cleanup-logs.sh
#!/bin/bash
cd /path/to/app
python -c "
from nibandha import Nibandha, AppConfig
nb = Nibandha(AppConfig(name='MyApp')).bind()
deleted = nb.cleanup_old_archives()
print(f'Deleted {deleted} archives')
"

# Crontab: Run daily at 2 AM
0 2 * * * /path/to/cleanup-logs.sh
```

**Windows - Task Scheduler**:
```python
# cleanup_logs.py
from nibandha import Nibandha, AppConfig

nb = Nibandha(AppConfig(name="MyApp")).bind()
deleted = nb.cleanup_old_archives()
print(f"Deleted {deleted} archives")

# Schedule this in Task Scheduler to run daily
```

## Client Override Examples

All rotation settings are overridable:

### Production Configuration

```python
# High-volume production service
rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=200,                # Large files before rotation
    rotation_interval_hours=6,      # Rotate 4 times per day
    archive_retention_days=90,      # Keep 3 months
    backup_count=50                 # Keep 50 most recent backups
)
```

### Development Configuration

```python
# Local development
rotation = LogRotationConfig(
    enabled=False   # Disable rotation for development
)

# Or minimal rotation
rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=10,                 # Small files
    backup_count=3                  # Keep only 3 backups
)
```

### Low-Disk Environment

```python
# Constrained storage
rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=10,                 # Rotate often
    archive_retention_days=7,       # Short retention
    backup_count=5                  # Minimal backups
)
```

### Archive-Heavy Environment

```python
# Long-term archival for compliance
rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=500,                # Large files
    rotation_interval_hours=168,    # Weekly rotation
    archive_retention_days=365,     # Keep 1 year
    backup_count=100                # High backup limit
)
```

## Best Practices

### 1. Match Interval to Format

Align `rotation_interval_hours` with `timestamp_format`:

```python
# ✅ Good: Daily format + 24-hour interval
LogRotationConfig(
    timestamp_format="%Y-%m-%d",
    rotation_interval_hours=24
)

# ✅ Good: Weekly format + 168-hour interval
LogRotationConfig(
    timestamp_format="%Y-W%W",
    rotation_interval_hours=168
)

# ❌ Bad: Daily format + hourly interval (many files!)
LogRotationConfig(
    timestamp_format="%Y-%m-%d",
    rotation_interval_hours=1  # Creates new file every hour
)
```

### 2. Balance backup_count and retention_days

```python
# ✅ Good: Balanced retention
LogRotationConfig(
    backup_count=30,              # ~1 month of backups
    archive_retention_days=30     # Aligned with count
)

# ❌ Bad: Conflicting settings
LogRotationConfig(
    backup_count=5,               # Keep 5 files
    archive_retention_days=365    # But delete after 1 year (confusing)
)
```

### 3. Monitor Disk Usage

```bash
# Check log directory size
du -sh .Nibandha/*/logs/

# Check archive size specifically
du -sh .Nibandha/*/logs/archive/

# Count archive files
find .Nibandha/*/logs/archive/ -name "*.log" | wc -l
```

### 4. Test Rotation Before Production

```python
# Test rotation with small values
test_rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=1,               # 1MB for testing
    rotation_interval_hours=1,   # 1 hour for testing
    backup_count=3
)

# Verify rotation works
nb = Nibandha(config)
nb.rotation_config = test_rotation
nb.bind()

# Generate logs and verify rotation
for i in range(10000):
    nb.logger.info(f"Test message {i}" * 100)  # Force size limit

assert nb.should_rotate()
nb.rotate_logs()
```

### 5. Centralize Configuration

```python
# config.py - Single source of truth
from nibandha import LogRotationConfig
import os

def get_rotation_config():
    """Get rotation config based on environment"""
    env = os.getenv("ENV", "development")
    
    if env == "production":
        return LogRotationConfig(
            enabled=True,
            max_size_mb=100,
            backup_count=30
        )
    elif env == "staging":
        return LogRotationConfig(
            enabled=True,
            max_size_mb=50,
            backup_count=10
        )
    else:  # development
        return LogRotationConfig(enabled=False)

# app.py - Use centralized config
from config import get_rotation_config
rotation = get_rotation_config()
```

## Troubleshooting

### Issue: Rotation Not Triggering

**Symptom**: Log file exceeds size limit but doesn't rotate.

**Cause**: Application not checking `should_rotate()`.

**Solution**: Add rotation check to application loop:
```python
import time

while True:
    # Application logic
    process_task()
    
    # Check and rotate if needed
    if nb.should_rotate():
        nb.rotate_logs()
    
    time.sleep(60)  # Check every minute
```

### Issue: Too Many Archive Files

**Symptom**: Archive directory growing without bound.

**Cause**: Not running `cleanup_old_archives()`.

**Solution**: Add cleanup to scheduled task:
```python
# Daily cleanup
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    lambda: nb.cleanup_old_archives(),
    'cron',
    hour=2  # Run at 2 AM
)
scheduler.start()
```

### Issue: Multiple Files Same Day

**Symptom**: Multiple files like `2026-01-15_10-30-15.log`, `2026-01-15_14-45-22.log`.

**Cause**: Old timestamp format with time component.

**Solution**: Update to Nibandha v1.0.1+ with daily format:
```bash
pip install --upgrade nibandha
```

Verify format:
```python
from nibandha import LogRotationConfig
config = LogRotationConfig()
assert config.timestamp_format == "%Y-%m-%d"
```

## Summary

Log Rotation provides:
- ✅ **Automatic Management**: Size and time-based rotation
- ✅ **Dual Cleanup**: Backup count + time retention
- ✅ **Daily Consolidation**: One file per day with daily format
- ✅ **Fully Override able**: All settings customizable
- ✅ **Production-Ready**: Prevents disk space issues

Next: Learn about [Configuration System](configuration.md) and [Client Integration](client-integration.md).
