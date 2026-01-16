# Logger Propagation Issue

## Issue
The Pravaha logger does not disable propagation after Nibandha initialization, causing Pravaha logs to propagate to the root logger if one exists. In multi-component applications, this can cause unexpected log routing.

## Impact
- **Log Leakage**: Pravaha logs may appear in parent logger files
- **Root Logger Pollution**: If Pravaha initializes first and becomes the root logger, it captures logs from all other components
- **Log Separation**: Cannot properly isolate Pravaha-specific logs

## Root Cause
Similar to Amsha, Pravaha's logger initialization does not set `propagate = False` after creating the Nibandha instance.

## Recommended Fix
In Pravaha's logger initialization code, add:

```python
_pravaha_nibandha = Nibandha(config).bind()

# Disable propagation to prevent logs from going to root logger
_pravaha_nibandha.logger.propagate = False

_pravaha_nibandha.logger.info("Pravaha logger initialized via Nibandha")
```

## Workaround for Client Applications
Client applications can set propagation after Pravaha initializes:

```python
import logging

# After Pravaha imports/initializes
logging.getLogger("Pravaha").propagate = False
```

## Notes
- Pravaha often initializes first in applications using the API factory pattern
- This makes it the de facto root logger, capturing all logs
- Setting `propagate = False` on Pravaha AND other components ensures proper separation

## Related Issues
- Similar issue in Amsha (see `docs/amsha/bugs/logger_propagation.md`)
- Timestamp format issue may also exist (needs verification)

## Priority
**High** - Affects all multi-component applications using Pravaha
