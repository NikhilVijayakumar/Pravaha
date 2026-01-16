# Repository & Configuration Module - Technical Documentation

> **Audience:** Pravaha contributors and maintainers  
> **Client Documentation:** [docs/client/repository-module.md](../client/repository-module.md)

## Module Objective

The Repository & Configuration module provides **unified configuration persistence** with pluggable storage backends:

1. **Protocol-Based Design** - All config storage uses repository protocols
2. **Pluggable Backends** - JSON default, PostgreSQL/MongoDB/Redis support
3. **Centralized Cache Config** - Single configuration for all cache locations
4. **Client Control** - Override defaults with custom implementations

## Architecture

### Unified Repository Pattern

```
┌─────────────────────────────────────────────────────┐
│              Configuration Layer                     │
│  ┌──────────────────────────────────────────────┐   │
│  │         CachePathConfig                      │   │
│  │  - Centralized cache directory config        │   │
│  │  - Default: .Pravaha                         │   │
│  │  - Client-configurable root                  │   │
│  └──────────────────────────────────────────────┘   │
│                       ↓                              │
│  ┌──────────────────────────────────────────────┐   │
│  │      Repository Protocols                    │   │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────┐│   │
│  │  │  Storage   │  │  Workflow  │  │   LLM   ││   │
│  │  │   Config   │  │   Config   │  │  Config │││   │
│  │  │ Repository │  │ Repository │  │Repository││  │
│  │  └────────────┘  └────────────┘  └─────────┘│   │
│  └──────────────────────────────────────────────┘   │
│                       ↓                              │
│  ┌──────────────────────────────────────────────┐   │
│  │     Default Implementations (JSON)           │   │
│  │  - JsonStorageConfigRepository               │   │
│  │  - JsonWorkflowConfigRepository              │   │
│  │  - JsonLLMConfigRepository                   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Components

### 1. Cache Path Configuration

**CachePathConfig** (`src/nikhil/pravaha/domain/config/cache_config.py`)

Controls where all Pravaha cache data is stored:

```python
@dataclass
class CachePathConfig:
    cache_root: Path = Path(".Pravaha")
    storage_cache_dir: Optional[Path] = None
    llm_cache_dir: Optional[Path] = None
    workflow_cache_dir: Optional[Path] = None
    
    def get_storage_cache_dir(self) -> Path:
        return self.storage_cache_dir or (self.cache_root / "config")
```

**Usage:**
```python
# Default (.Pravaha)
config = CachePathConfig.default()

# Custom root
config = CachePathConfig.from_custom_root("/var/lib/pravaha")

# Per-component paths
config = CachePathConfig(
    cache_root=Path("/var/lib/pravaha"),
    storage_cache_dir=Path("/var/cache/pravaha/storage"),
    llm_cache_dir=Path("/var/cache/pravaha/llm")
)
```

### 2. Repository Protocols

#### StorageConfigRepositoryProtocol

```python
class StorageConfigRepositoryProtocol(Protocol):
    def get_config(self) -> Dict[str, str]:
        """Get storage paths configuration."""
        ...
    
    def update_config(self, config: Dict[str, str]) -> None:
        """Update storage configuration."""
        ...
    
    def get_path(self, category: str) -> str:
        """Get specific storage path by category."""
        ...
```

#### WorkflowConfigRepositoryProtocol

```python
class WorkflowConfigRepositoryProtocol(Protocol):
    def get_config(self) -> Dict[str, str]:
        """Get workflow paths configuration."""
        ...
    
    def update_config(self, config: Dict[str, str]) -> None:
        """Update workflow configuration."""
        ...
```

#### LLMConfigRepositoryProtocol

```python
class LLMConfigRepositoryProtocol(Protocol):
    def get_config(self) -> Dict[str, Any]:
        """Get complete LLM configuration."""
        ...
    
    def resolve_output_config(self, model_key: str) -> Dict[str, Any]:
        """Resolve output config for a model."""
        ...
```

### 3. JSON Implementations

Default implementations use JSON files for configuration storage.

**Location:** `.Pravaha/config/`
- `storage.json` - Storage paths
- `workflow.json` - Workflow paths  
- `llm_config.json` - LLM configuration

## Manager Integration

All managers now accept repository dependencies:

### Before (Hardcoded)
```python
class LocalStorageManager:
    def __init__(self):
        self.config_file = Path(".Pravaha/config/storage.json")
        # Direct file I/O
```

### After (Repository Pattern)
```python
class LocalStorageManager:
    def __init__(
        self,
        cache_config: Optional[CachePathConfig] = None,
        config_repository: Optional[StorageConfigRepositoryProtocol] = None
    ):
        if config_repository is None:
            # Default to JSON
            config_repository = JsonStorageConfigRepository(cache_config)
        
        self.config_repository = config_repository
```

**Benefits:**
- Swap storage backend without changing manager code
- Test with mock repository
- Production uses PostgreSQL, dev uses JSON

## Design Patterns

### 1. Protocol-Based Design
All configuration storage uses protocols, not concrete classes:
```python
def __init__(self, config_repository: StorageConfigRepositoryProtocol):
    # Accepts ANY implementation
    self.repository = config_repository
```

### 2. Dependency Injection
Repositories injected via constructor:
```python
# Client chooses implementation
postgres_repo = PostgreSQLStorageConfigRepository(conn)
manager = LocalStorageManager(config_repository=postgres_repo)
```

### 3. Sensible Defaults
If no repository provided, use JSON:
```python
if config_repository is None:
    config_repository = JsonStorageConfigRepository(cache_config)
```

### 4. Centralized Cache Config
Single `CachePathConfig` for all components:
```python
cache_config = CachePathConfig.from_custom_root("/var/lib/pravaha")

storage_mgr = LocalStorageManager(cache_config=cache_config)
workflow_mgr = LocalWorkflowManager(cache_config=cache_config)
llm_mgr = LLMConfigManager(cache_config=cache_config)
```

## Custom Implementation Example

### PostgreSQL Storage Config Repository

```python
class PostgreSQLStorageConfigRepository(StorageConfigRepositoryProtocol):
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        self._ensure_table()
    
    def _ensure_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS storage_config (
                    key VARCHAR(50) PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
    
    def get_config(self) -> Dict[str, str]:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT key, value FROM storage_config")
            return dict(cursor.fetchall())
    
    def update_config(self, config: Dict[str, str]) -> None:
        with self.conn.cursor() as cursor:
            for key, value in config.items():
                cursor.execute("""
                    INSERT INTO storage_config (key, value)
                    VALUES (%s, %s)
                    ON CONFLICT (key) DO UPDATE SET value = %s
                """, (key, value, value))
            self.conn.commit()
    
    def get_path(self, category: str) -> str:
        config = self.get_config()
        return config.get(category)
```

### Usage
```python
# In production
postgres_repo = PostgreSQLStorageConfigRepository(
    "postgresql://user:pass@localhost/pravaha"
)

storage_manager = LocalStorageManager(config_repository=postgres_repo)

# Now all storage config reads/writes go to PostgreSQL
```

## Configuration Flow

### Storage Configuration
```
Client Request: Update storage config
    ↓
LocalStorageManager.update_config(output="...", intermediate="...")
    ↓
config_repository.update_config({"output": "...", "intermediate": "..."})
    ↓
JSON File / PostgreSQL / MongoDB
```

### Reading Configuration
```
LocalStorageManager.get_config()
    ↓
config_repository.get_config()
    ↓
Returns: {"output": "output", "intermediate": "intermediate", ...}
```

## Testing

### Mock Repository for Testing

```python
class MockStorageConfigRepository(StorageConfigRepositoryProtocol):
    def __init__(self):
        self._config = {}
    
    def get_config(self) -> Dict[str, str]:
        return self._config
    
    def update_config(self, config: Dict[str, str]) -> None:
        self._config.update(config)
    
    def get_path(self, category: str) -> str:
        return self._config.get(category)

# In tests
def test_storage_manager():
    mock_repo = MockStorageConfigRepository()
    manager = LocalStorageManager(config_repository=mock_repo)
    
    manager.update_config(output="test/output")
    assert mock_repo.get_path("output") == "test/output"
```

## Migration Guide

### From Hardcoded to Repository Pattern

**Before:**
```python
storage_manager = LocalStorageManager()
# Config stored in .Pravaha/config/storage.json
```

**After (Default - No Changes Needed):**
```python
storage_manager = LocalStorageManager()
# Still uses JSON, but now via repository pattern
# Fully backwards compatible
```

**After (Custom Backend):**
```python
# Use PostgreSQL
postgres_repo = PostgreSQLStorageConfigRepository(conn_string)
storage_manager = LocalStorageManager(config_repository=postgres_repo)
```

## Benefits

1. **Flexibility** - Swap backends without code changes
2. **Testability** - Use mocks for unit tests
3. **Production-Ready** - PostgreSQL/MongoDB for production
4. **Backwards Compatible** - JSON default maintains compatibility
5. **Centralized Config** - Single `CachePathConfig` for all components

## Future Enhancements

- [ ] Redis repository for high-performance caching
- [ ] DynamoDB repository for AWS deployments
- [ ] Configuration versioning/migrations
- [ ] Configuration change events
- [ ] Encrypted configuration storage
