# Unified Root Directory

## Concept

The **Unified Root** is Nibandha's core architectural principle: **all applications share a single `.Nibandha/` directory** while maintaining complete isolation through namespaced subdirectories.

This design provides centralization without conflicts, simplifying management while ensuring application independence.

## Directory Structure

### Root Layout

```
.Nibandha/
├── config/                 # Global configuration
│   └── rotation_config.yaml
│
├── Amsha/                  # AI Agent workspace
│   ├── logs/
│   │   ├── data/           # Active logs
│   │   └── archive/        # Archived logs
│   └── output/
│       ├── final/
│       └── intermediate/
│
├── Pravaha/                # Workflow & API workspace
│   ├── logs/
│   │   ├── data/
│   │   └── archive/
│   ├── workflow/
│   │   ├── details/
│   │   └── run/
│   └── config/
│
├── Akashavani/             # Voice services workspace
│   ├── logs/
│   │   ├── data/
│   │   └── archive/
│   └── recordings/
│
└── [AnyApp]/               # Your application
    ├── logs/
    └── [custom folders]
```

### Components

#### 1. Global Config Directory
**Location**: `.Nibandha/config/`

Stores configuration shared across all applications:
- `rotation_config.yaml` - Log rotation settings
- Future: Cloud sync config, metrics config

```yaml
# .Nibandha/config/rotation_config.yaml
enabled: true
max_size_mb: 50
rotation_interval_hours: 24
archive_retention_days: 30
backup_count: 5
```

#### 2. Application Namespaces
**Location**: `.Nibandha/{AppName}/`

Each application gets its own isolated directory:
- **Naming**: Matches `AppConfig.name` (e.g., "Amsha", "Pravaha")
- **Isolation**: Apps cannot access each other's directories
- **Structure**: Controlled by app's `custom_folders` configuration

#### 3. Standard Logs Directory
**Location**: `.Nibandha/{AppName}/logs/`

Every application gets a `logs/` directory:

**Without Rotation** (default):
```
Amsha/logs/
└── Amsha.log               # Single rolling log file
```

**With Rotation Enabled**:
```
Amsha/logs/
├── data/                   # Active timestamped logs
│   ├── 2026-01-15.log      # Current day's log
│   └── 2026-01-14.log      # Previous day (if still active)
└── archive/                # Rotated/old logs
    ├── 2026-01-13.log
    ├── 2026-01-12.log
    └── 2026-01-11.log
```

## Benefits

### 1. Single Backup Location
Backup entire AI ecosystem with one command:
```bash
# Backup all application data
tar -czf nibandha-backup-$(date +%Y%m%d).tar.gz .Nibandha/

# Or sync to cloud
rclone sync .Nibandha/ remote:nibandha-backup/
```

### 2. Centralized Monitoring
Monitor all applications from one location:
```bash
# View all recent logs
tail -f .Nibandha/*/logs/data/*.log

# Check total storage usage
du -sh .Nibandha/*

# Find errors across all apps
grep -r "ERROR" .Nibandha/*/logs/
```

### 3. Easy Deployment
Deploy to new environments simply:
```bash
# Development
git clone <repo>
python app.py                    # Creates .Nibandha/ automatically

# Production
rsync -av .Nibandha/ prod:/opt/  # Sync workspace
```

### 4. Version Control Friendly
Standard `.gitignore` pattern:
```gitignore
# Ignore workspace, but keep structure
.Nibandha/
!.Nibandha/config/
```

### 5. Application Isolation
Apps can't interfere with each other:
```python
# Amsha writes here
.Nibandha/Amsha/output/final/

# Pravaha writes here - completely separate
.Nibandha/Pravaha/workflow/details/
```

## Creation Workflow

### Automatic Creation

Nibandha creates the unified root automatically on first `bind()`:

```python
from nibandha import Nibandha, AppConfig

# First run - creates .Nibandha/ and subdirectories
config = AppConfig(name="MyApp", custom_folders=["data", "output"])
nb = Nibandha(config).bind()
```

**Result**:
```
.Nibandha/
├── config/                 # Created for global config
└── MyApp/                  # Created with app name
    ├── logs/               # Standard logs directory
    ├── data/               # Custom folder
    └── output/             # Custom folder
```

### Idempotent Operations

Nibandha safely handles repeated calls:
```python
# Safe to call multiple times
nb1 = Nibandha(AppConfig(name="App1")).bind()
nb2 = Nibandha(AppConfig(name="App2")).bind()
nb1_again = Nibandha(AppConfig(name="App1")).bind()

# Result: App1 and App2 directories coexist
.Nibandha/
├── App1/
└── App2/
```

### Custom Root Location

Override the root directory name:
```python
# Use custom root name (e.g., for testing)
nb = Nibandha(config, root_name=".MyCustomRoot").bind()

# Creates: .MyCustomRoot/ instead of .Nibandha/
```

## Multi-Application Scenarios

### Scenario 1: Development Machine
Developer working on multiple projects:

```
project/
├── amsha/                  # Amsha codebase
├── pravaha/                # Pravaha codebase
├── akashavani/             # Akashavani codebase
└── .Nibandha/              # Shared workspace
    ├── Amsha/
    ├── Pravaha/
    └── Akashavani/
```

All three applications share `.Nibandha/` in project root.

### Scenario 2: Production Server
Multiple services running:

```
/opt/ai-ecosystem/
├── .Nibandha/              # Single unified workspace
│   ├── Amsha/
│   ├── Pravaha/
│   └── Akashavani/
├── services/
│   ├── amsha-service.py
│   ├── pravaha-api.py
│   └── akashavani-bot.py
└── supervisor.conf         # Process management
```

Single `.Nibandha/` serves all production services.

### Scenario 3: Containerized Deployment
Each container mounts shared volume:

```yaml
# docker-compose.yml
services:
  amsha:
    volumes:
      - nibandha_workspace:/app/.Nibandha
  pravaha:
    volumes:
      - nibandha_workspace:/app/.Nibandha
volumes:
  nibandha_workspace:         # Shared Docker volume
```

## Best Practices

### 1. Keep Root Clean
Only Nibandha should create files in `.Nibandha/`:
```python
# ✅ Good: Use Nibandha to manage paths
nb = Nibandha(config).bind()
output_dir = nb.app_root / "output"
output_dir / "result.json"

# ❌ Bad: Manual path construction
Path(".Nibandha/MyApp/output/result.json")  # Fragile
```

### 2. Use Custom Folders
Define all app-specific directories upfront:
```python
config = AppConfig(
    name="MyApp",
    custom_folders=[
        "data/raw",
        "data/processed",
        "models",
        "output/artifacts"
    ]
)
```

### 3. Respect Namespaces
Don't access other applications' directories:
```python
# ✅ Good: Stay in your namespace
amsha_nb = Nibandha(AppConfig(name="Amsha")).bind()
file = amsha_nb.app_root / "output" / "result.txt"

# ❌ Bad: Cross-namespace access
pravaha_file = Path(".Nibandha/Pravaha/workflow/details.json")
```

### 4. Environment Variables
Use environment variables for root customization:
```bash
# Development
export NIBANDHA_ROOT=".Nibandha-dev"

# Testing
export NIBANDHA_ROOT=".test-workspace"

# Docker
ENV NIBANDHA_ROOT=/var/nibandha
```

### 5. Backup Strategy
Regular backups of unified root:
```bash
#!/bin/bash
# backup-nibandha.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/nibandha"

# Exclude large files if needed
tar -czf "$BACKUP_DIR/nibandha-$TIMESTAMP.tar.gz" \
    --exclude='.Nibandha/*/logs/archive/*' \
    .Nibandha/

# Keep only last 30 days
find "$BACKUP_DIR" -name "nibandha-*.tar.gz" -mtime +30 -delete
```

## Migration Guide

### From Separate Directories

**Before** (traditional approach):
```
project/
├── amsha-logs/
├── amsha-output/
├── pravaha-logs/
└── pravaha-workflows/
```

**After** (unified root):
```
project/
└── .Nibandha/
    ├── Amsha/
    │   ├── logs/
    │   └── output/
    └── Pravaha/
        ├── logs/
        └── workflows/
```

**Migration Steps**:
1. Create `.Nibandha/` directory
2. Move `amsha-logs/` → `.Nibandha/Amsha/logs/`
3. Move `amsha-output/` → `.Nibandha/Amsha/output/`
4. Move `pravaha-logs/` → `.Nibandha/Pravaha/logs/`
5. Move `pravaha-workflows/` → `.Nibandha/Pravaha/workflows/`
6. Update application code to use Nibandha
7. Remove old directories

### From Legacy Logging

**Before**:
```python
import logging
logging.basicConfig(filename='app.log')
logger = logging.getLogger(__name__)
```

**After**:
```python
from nibandha import Nibandha, AppConfig

nb = Nibandha(AppConfig(name="MyApp")).bind()
logger = nb.logger  # Replaces basicConfig
```

## Troubleshooting

### Issue: Permission Denied
```bash
PermissionError: [Errno 13] Permission denied: '.Nibandha/Amsha'
```

**Solution**: Check directory permissions:
```bash
chmod -R u+rwX .Nibandha/
```

### Issue: Multiple Roots
```bash
# Accidentally created both
.Nibandha/
.nibandha/
```

**Solution**: Use consistent casing:
```python
# Always use same root name
nb = Nibandha(config, root_name=".Nibandha").bind()
```

### Issue: Disk Space
```bash
du -sh .Nibandha/
# Output: 10G .Nibandha/
```

**Solution**: Enable log rotation and cleanup:
```python
rotation = LogRotationConfig(
    enabled=True,
    backup_count=5,              # Keep only 5 backups
    archive_retention_days=7     # Delete after 7 days
)
nb.cleanup_old_archives()        # Manual cleanup
```

## Summary

The Unified Root provides:
- ✅ **Single Source**: All data in one location
- ✅ **Application Isolation**: No conflicts between apps
- ✅ **Easy Management**: Backup, monitor, deploy from one directory
- ✅ **Standard Structure**: Predictable layout for all applications
- ✅ **Scalability**: Add new applications without restructuring

Next: Learn about the [Logging Module](logging.md) that powers the unified root.
