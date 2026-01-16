# Nibandha Overview

## What is Nibandha?

**Nibandha** (निबन्ध) means "binding" or "record-keeping" in Sanskrit. It is a universal, protocol-based **Logger and Storage Manager** designed to provide a unified workspace for AI ecosystem applications.

Nibandha serves as the foundational infrastructure layer for applications like:
- **Amsha** - AI Agent framework (CrewAI-based)
- **Pravaha** - Workflow and API management
- **Akashavani** - Voice and communication services
- Any Python application requiring standardized logging and storage

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────┐
│          Client Applications                │
│  (Amsha, Pravaha, Akashavani, etc.)        │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│             Nibandha Core                   │
│  ┌─────────────┬──────────────┬──────────┐ │
│  │   Logging   │   Storage    │  Config  │ │
│  │   Module    │   Manager    │  System  │ │
│  └─────────────┴──────────────┴──────────┘ │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│        .Nibandha/ Root Directory            │
│                                             │
│  ├── config/          # Global config      │
│  ├── Amsha/           # App namespaces     │
│  ├── Pravaha/                              │
│  └── Akashavani/                           │
└─────────────────────────────────────────────┘
```

### Core Components

#### 1. Nibandha Class
The main entry point for applications. Handles initialization, directory creation, and logger binding.

```python
class Nibandha:
    def __init__(self, config: AppConfig, root_name: str = ".Nibandha")
    def bind(self) -> 'Nibandha'
    def rotate_logs(self) -> None
    def cleanup_old_archives(self) -> int
```

#### 2. AppConfig
Defines application identity and custom folder requirements.

```python
class AppConfig(BaseModel):
    name: str                          # Application name (e.g., "Amsha")
    custom_folders: List[str] = []     # App-specific folders
    log_level: str = "INFO"            # Logging level
```

#### 3. LogRotationConfig
Configures log rotation, archival, and retention policies.

```python
class LogRotationConfig(BaseModel):
    enabled: bool = False
    max_size_mb: int = 10                    # Size trigger
    rotation_interval_hours: int = 24        # Time trigger
    archive_retention_days: int = 30         # Archive cleanup
    backup_count: int = 1                    # Max backups to keep
    log_data_dir: str = "logs/data"
    archive_dir: str = "logs/archive"
    timestamp_format: str = "%Y-%m-%d"      # Daily format
```

## Key Features

### 1. **Unified Root Directory**
All applications share a single `.Nibandha/` root, providing:
- Central location for all AI ecosystem data
- Easy backup and version control
- Simplified deployment and monitoring

### 2. **Application Isolation**
Each application receives its own namespace:
```
.Nibandha/
├── Amsha/              # Isolated workspace
│   ├── logs/
│   └── output/
├── Pravaha/            # Separate namespace
│   ├── logs/
│   └── workflow/
└── YourApp/            # Your app's space
    └── logs/
```

### 3. **Automatic Logging**
Nibandha automatically configures logging for each application:
- **Named Logger**: Application-specific logger (e.g., `logging.getLogger("Amsha")`)
- **File Handler**: Writes logs to application's log directory
- **Console Handler**: Outputs to stdout for development
- **No Propagation**: Prevents log leakage to root logger

### 4. **Log Rotation & Archival**
Built-in log rotation with multiple triggers:
- **Size-based**: Rotate when log exceeds configured size (e.g., 50MB)
- **Time-based**: Rotate after configured interval (e.g., 24 hours)
- **Backup Limit**: Keep only N most recent backup files
- **Time Retention**: Remove archives older than configured period

### 5. **Protocol-Based Design**
Nibandha follows a simple protocol contract:
1. Define `AppConfig` with app name and folders
2. Create `Nibandha` instance
3. Call `bind()` to initialize
4. Use `logger` for logging

## Design Principles

### 1. Zero-Config Default
Works out-of-the-box with sensible defaults:
```python
# Minimal setup - just works!
from nibandha import Nibandha, AppConfig

config = AppConfig(name="MyApp")
nb = Nibandha(config).bind()
nb.logger.info("Hello!")
```

### 2. Fully Customizable
Every aspect can be overridden:
```python
# Custom configuration
config = AppConfig(
    name="MyApp",
    custom_folders=["data", "models", "output"],
    log_level="DEBUG"
)

rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=100,
    rotation_interval_hours=12,
    backup_count=10
)

nb = Nibandha(config)
nb.rotation_config = rotation
nb._save_rotation_config(rotation)
nb.bind()
```

### 3. Application-Centric
Applications control their own structure:
```python
# Amsha defines its own folders
amsha_config = AppConfig(
    name="Amsha",
    custom_folders=["output/final", "output/intermediate"]
)

# Pravaha defines different folders
pravaha_config = AppConfig(
    name="Pravaha",
    custom_folders=["workflow/details", "workflow/run", "config"]
)
```

### 4. Configuration Persistence
Settings are cached to avoid repeated prompts:
- First run: Interactive prompts or programmatic config
- Subsequent runs: Cached config loaded automatically
- Override: Modify `.Nibandha/config/rotation_config.yaml` anytime

### 5. Production-Ready
Built for reliability:
- Comprehensive error handling
- Safe file operations with atomic writes
- Automatic cleanup of old archives
- Configurable retention policies

## Module Relationships

```
┌──────────────────┐
│   Client App     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌────────────────┐
│  Nibandha Core   │────→│   AppConfig    │
└────────┬─────────┘     └────────────────┘
         │
         ├──→ Logging Module
         │    ├── Handler Attachment
         │    ├── Logger Configuration
         │    └── Child Logger Support
         │
         ├──→ Rotation Module
         │    ├── Size & Time Triggers
         │    ├── Archive Management
         │    └── Cleanup Utilities
         │
         └──→ Configuration Module
              ├── Config Loading
              ├── Config Caching
              └── Interactive Prompts
```

## Use Cases

### 1. AI Agent Framework (Amsha)
```python
# Amsha needs structured output directories
config = AppConfig(
    name="Amsha",
    custom_folders=["output/final/output", "output/intermediate/output"]
)
nb = Nibandha(config).bind()
```

### 2. Workflow Engine (Pravaha)
```python
# Pravaha needs workflow and config storage
config = AppConfig(
    name="Pravaha",
    custom_folders=["workflow/details", "workflow/run", "config"]
)
nb = Nibandha(config).bind()
```

### 3. Production Service
```python
# Production setup with aggressive rotation
config = AppConfig(name="ProductionAPI", log_level="WARNING")
rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=100,
    rotation_interval_hours=6,  # Rotate every 6 hours
    archive_retention_days=90,  # Keep 90 days
    backup_count=20             # Keep 20 most recent
)
```

### 4. Development Environment
```python
# Development with verbose logging
config = AppConfig(name="DevApp", log_level="DEBUG")
rotation = LogRotationConfig(enabled=False)  # Disabled for dev
```

## Benefits

### For Developers
- ✅ **Quick Integration**: Minimal code to get started
- ✅ **Predictable Structure**: Standard directory layout
- ✅ **No Configuration**: Works out-of-the-box
- ✅ **Full Control**: Override anything when needed

### For Operations
- ✅ **Centralized Logs**: All apps in one `.Nibandha/` directory
- ✅ **Automatic Rotation**: Prevents disk space issues
- ✅ **Configurable Retention**: Balance storage vs. history
- ✅ **Easy Backup**: Single directory to backup/sync

### For the AI Ecosystem
- ✅ **Unified Workspace**: Common foundation for all tools
- ✅ **Application Isolation**: No conflicts between apps
- ✅ **Extensible**: Easy to add new applications
- ✅ **Future-Ready**: Built for cloud sync, metrics, versioning

## Next Steps

- Learn about the [Unified Root](unified-root.md) directory structure
- Understand [Logging Module](logging.md) internals
- Configure [Log Rotation](log-rotation.md) for your needs
- Integrate Nibandha via [Client Integration](client-integration.md) guide
