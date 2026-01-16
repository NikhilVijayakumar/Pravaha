# Nibandha Module Documentation

Welcome to the Nibandha module documentation. This directory contains comprehensive guides for all features and modules of the Nibandha logging and storage management library.

## Documentation Structure

### Core Concepts
- [**Overview**](overview.md) - Introduction to Nibandha, architecture, and core principles
- [**Unified Root**](unified-root.md) - Understanding the `.Nibandha/` workspace structure
- [**Application Isolation**](application-isolation.md) - How apps maintain separate namespaces

### Logging System
- [**Logging Module**](logging.md) - Core logging functionality and handler management
- [**Log Rotation**](log-rotation.md) - Automatic log rotation, archival, and cleanup
- [**Log Configuration**](log-configuration.md) - Configuring log levels, formats, and retention

### Configuration
- [**Configuration System**](configuration.md) - Global and app-specific configuration
- [**Client Integration**](client-integration.md) - Integrating Nibandha into your application

### Advanced Features
- [**Rotation Utilities**](rotation-utilities.md) - Manual rotation, cleanup, and scheduling
- [**Custom Folders**](custom-folders.md) - Defining application-specific folder structures

## Quick Start

```python
from nibandha import Nibandha, AppConfig, LogRotationConfig

# Basic setup
config = AppConfig(name="MyApp")
nb = Nibandha(config).bind()
nb.logger.info("Hello from Nibandha!")

# With custom folders and rotation
config = AppConfig(
    name="MyApp",
    custom_folders=["data", "output", "config"]
)
rotation = LogRotationConfig(
    enabled=True,
    max_size_mb=50,
    backup_count=5
)
nb = Nibandha(config)
nb.rotation_config = rotation
nb._save_rotation_config(rotation)
nb.bind()
```

## Module Overview

| Module | Purpose | Documentation |
|--------|---------|---------------|
| **Core** | Main Nibandha class and app binding | [overview.md](overview.md) |
| **Logging** | Logger initialization and handler management | [logging.md](logging.md) |
| **Rotation** | Log rotation, archival, and cleanup | [log-rotation.md](log-rotation.md) |
| **Configuration** | Config loading and management | [configuration.md](configuration.md) |

## Key Features

### 1. Unified Root Directory
All applications share a single `.Nibandha/` root while maintaining complete isolation.

### 2. Automatic Logging
Each application gets a configured logger with file and console handlers automatically attached.

### 3. Log Rotation
Configurable size-based and time-based log rotation with automatic archival and cleanup.

### 4. Application Isolation
Each app has its own namespace preventing conflicts and log leakage.

### 5. Client-Driven Configuration
All settings are easily overridable via config files or programmatic API.

## Design Principles

1. **Protocol-Based**: Lean design following simple configuration contracts
2. **Zero-Config Default**: Works out-of-the-box with sensible defaults
3. **Fully Customizable**: Every aspect can be overridden by clients
4. **Application-Centric**: Each app controls its own folder structure and settings
5. **Production-Ready**: Built for reliability with comprehensive error handling

## Getting Help

- Check specific module documentation for detailed information
- See [client-integration.md](client-integration.md) for integration examples
- Review [log-rotation.md](log-rotation.md) for rotation setup and troubleshooting
