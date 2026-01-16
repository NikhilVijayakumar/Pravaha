# Logger Timestamp Format Issue

## Issue
The Amsha logger uses a timestamp format that includes hours, minutes, and seconds (`%Y-%m-%d_%H-%M-%S`), causing a new log file to be created on every application restart rather than appending to the daily log file.

## Impact
- **File Proliferation**: Multiple log files per day (one per restart)
- **Log Fragmentation**: Logs scattered across multiple files instead of consolidated daily logs
- **Storage**: Unnecessary file creation

## Root Cause
In `amsha/common/logger.py`, the default rotation config (line 256):
```python
'timestamp_format': '%Y-%m-%d_%H-%M-%S'
```

This creates uniquely named files for each initialization, preventing log appending.

## Recommended Fix
Change the timestamp format to daily granularity:

```python
'timestamp_format': '%Y-%m-%d'  # Daily rotation
```

This ensures:
- Logs append to the same file throughout the day
- New files created only when date changes OR size limit reached
- Better log consolidation

## Workaround for Client Applications
Client applications can override this by creating their own rotation config before calling `get_logger()`:

```python
from pathlib import Path
import yaml

config_dir = Path(".Nibandha/config")
config_dir.mkdir(parents=True, exist_ok=True)

rotation_config = {
    'enabled': True,
    'max_size_mb': 50,
    'rotation_interval_hours': 24,
    'archive_retention_days': 30,
    'log_data_dir': 'logs/data',
    'archive_dir': 'logs/archive',
    'timestamp_format': '%Y-%m-%d'  # Daily rotation
}

with open(config_dir / "rotation_config.yaml", 'w') as f:
    yaml.dump(rotation_config, f, default_flow_style=False)

# Now initialize Amsha logger
from amsha.common.logger import get_logger
logger = get_logger()
```

## Related Issues
- Similar issue exists in Nibandha defaults (may be fixed in newer versions)
- Logger propagation issue (see `logger_propagation.md`)

## Priority
**Medium** - Affects log file organization
