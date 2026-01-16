# Application Isolation

## Concept

**Application Isolation** ensures that each application using Nibandha has its own dedicated namespace within the unified `.Nibandha/` root, preventing conflicts and maintaining clean separation.

## How It Works

### Namespace Separation

Each application is identified by its `AppConfig.name` and receives:
- **Dedicated Directory**: `.Nibandha/{AppName}/`
- **Independent Logger**: `logging.getLogger(AppName)`
- **Isolated Handlers**: Handlers attached only to named logger
- **No Propagation**: `propagate=False` prevents log leakage

```
.Nibandha/
├── Amsha/              # Amsha application (isolated)
│   ├── logs/
│   └── output/
├── Pravaha/            # Pravaha application (isolated)
│   ├── logs/
│   └── workflow/
└── Akashavani/         # Akashavani application (isolated)
    ├── logs/
    └── recordings/
```

### Logger Hierarchy

```
Python Root Logger
└── [No Nibandha interference]

Amsha Logger (propagate=False)
├── FileHandler → .Nibandha/Amsha/logs/
├── ConsoleHandler → stdout
└── Child Loggers (Amsha.*)
    └── All write to Amsha logs

Pravaha Logger (propagate=False)
├── FileHandler → .Nibandha/Pravaha/logs/
├── ConsoleHandler → stdout
└── Child Loggers (Pravaha.*)
    └── All write to Pravaha logs
```

## Benefits

### 1. No Log Leakage

Logs stay within application namespace:

```python
# Amsha logs
amsha_nb = Nibandha(AppConfig(name="Amsha")).bind()
amsha_nb.logger.info("Amsha message")
# → .Nibandha/Amsha/logs/Amsha.log

# Pravaha logs
pravaha_nb = Nibandha(AppConfig(name="Pravaha")).bind()
pravaha_nb.logger.info("Pravaha message")
# → .Nibandha/Pravaha/logs/Pravaha.log

# No cross-contamination!
```

### 2. Independent Configuration

Each app controls its own settings:

```python
# Amsha: Aggressive rotation
amsha_rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=50,
    backup_count=10
)

# Pravaha: Minimal rotation
pravaha_rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=200,
    backup_count=3
)
```

### 3. Conflict-Free Deployment

Multiple applications coexist peacefully:

```python
# Multiple apps in same process
amsha = Nibandha(AppConfig(name="Amsha")).bind()
pravaha = Nibandha(AppConfig(name="Pravaha")).bind()
akashavani = Nibandha(AppConfig(name="Akashavani")).bind()

# All work independently
amsha.logger.info("Amsha running")
pravaha.logger.info("Pravaha running")
akashavani.logger.info("Akashavani running")
```

### 4. Easy Debugging

Find issues per application:

```bash
# View only Amsha logs
tail -f .Nibandha/Amsha/logs/data/*.log

# Search for Pravaha errors
grep "ERROR" .Nibandha/Pravaha/logs/data/*.log

# Check Amsha storage usage
du -sh .Nibandha/Amsha/
```

## Implementation

### Handler Attachment

Handlers are attached to **named logger**, not ROOT:

```python
# Nibandha implementation
def _init_logger(self):
    # Get NAMED logger first
    self.logger = logging.getLogger(self.config.name)
    
    # Attach handlers to NAMED logger
    self.logger.addHandler(file_handler)
    self.logger.addHandler(console_handler)
    
    # Prevent propagation to ROOT
    self.logger.propagate = False
```

**Result**: Complete isolation from ROOT logger and other applications.

### Propagation Control

`propagate=False` ensures logs don't leak to ROOT:

```python
# Without propagate=False
Amsha Logger → [Handlers] → ROOT Logger → [Other handlers]
                                    ↓
                              Pravaha sees Amsha logs! ❌

# With propagate=False (Nibandha's approach)
Amsha Logger → [Handlers] ✓
    (stops here, doesn't propagate)

Pravaha Logger → [Handlers] ✓
    (completely separate)
```

## Best Practices

### 1. Unique Application Names

```python
# ✅ Good: Unique names
Nibandha(AppConfig(name="Amsha")).bind()
Nibandha(AppConfig(name="Pravaha")).bind()

# ❌ Bad: Duplicate names
Nibandha(AppConfig(name="MyApp")).bind()
Nibandha(AppConfig(name="MyApp")).bind()  # Conflict!
```

### 2. Respect Namespaces

```python
# ✅ Good: Stay in your namespace
amsha_nb = Nibandha(AppConfig(name="Amsha")).bind()
output_dir = amsha_nb.app_root / "output"

# ❌ Bad: Cross-namespace access
pravaha_dir = Path(".Nibandha/Pravaha/workflow")  # Don't do this
```

### 3. Use Child Loggers Within Namespace

```python
# ✅ Good: Child loggers in same namespace
import logging
amsha_module = logging.getLogger("Amsha.module")
amsha_service = logging.getLogger("Amsha.service")

# ❌ Bad: Outside namespace
other_logger = logging.getLogger("module")  # Not in Amsha namespace
```

## Multi-Application Scenarios

### Scenario 1: Microservices

```python
# service1/main.py
from nibandha import Nibandha, AppConfig
nb = Nibandha(AppConfig(name="Service1")).bind()

# service2/main.py
from nibandha import Nibandha, AppConfig
nb = Nibandha(AppConfig(name="Service2")).bind()

# Both share .Nibandha/ but completely isolated
```

### Scenario 2: Monorepo

```
monorepo/
├── frontend-api/
├── worker/
├── scheduler/
└── .Nibandha/
    ├── FrontendAPI/    # Isolated
    ├── Worker/         # Isolated
    └── Scheduler/      # Isolated
```

## Summary

Application Isolation provides:
- ✅ **Clean Separation**: No log/config conflicts
- ✅ **Independent Control**: Each app manages its own settings
- ✅ **Easy Debugging**: Per-application log analysis
- ✅ **Scalable**: Add new apps without restructuring

This completes the Nibandha module documentation suite!
