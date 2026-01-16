# Storage Module - Technical Documentation

> **Audience:** Pravaha contributors and maintainers  
> **Client Documentation:** [docs/client/storage-module.md](../client/storage-module.md)

## Module Objective

The Storage module provides **organized file system management** with hierarchical structure for three distinct data categories:

1. **Output** - Final results (Version/Feature/Product hierarchy)
2. **Intermediate** - Work-in-progress data (Version/Feature/Product hierarchy)
3. **Knowledge** - Reference data (simple file tree)

## Architecture

### Coordinator Pattern with Specialized Providers

```
┌────────────────────────┐
│  StorageAPIProvider    │  (Main Coordinator)
│  (Routes & Delegation) │
└──────────┬─────────────┘
           │ delegates to
           ├──→ KnowledgeStorageProvider (Simple listing)
           ├──→ IntermediateStorageProvider (Feature + Timestamp)
           └──→ OutputStorageProvider (Product/Feature + Suffix)
```

**Why Specialized Providers?**
- **Separation of Concerns** - Each category has unique requirements
- **Maintainability** - Changes to one don't affect others
- **Testability** - Test each provider independently

### Components

#### 1. Manager Layer (`src/nikhil/pravaha/domain/storage/manager/`)

**LocalStorageManager**
- Manages root paths for 3 categories
- Uses **repository pattern** for config persistence
- Configurable cache location via `CachePathConfig`
- Supports custom repository backends (PostgreSQL, MongoDB, etc.)

```python
class LocalStorageManager:
    def __init__(
        self,
        defaults: Optional[dict[str, str]] = None,
        config_path: Optional[Path] = None,
        cache_config: Optional[CachePathConfig] = None,  # NEW
        config_repository: Optional[StorageConfigRepositoryProtocol] = None  # NEW
    ):
        # Use custom cache location if provided
        if cache_config is None:
            cache_config = CachePathConfig.default()  # .Pravaha
        
        # Use custom repository or default to JSON
        if config_repository is None:
            config_repository = JsonStorageConfigRepository(cache_config)
        
        self.config_repository = config_repository
        self._ensure_directories()
```

**Benefits of Repository Pattern:**
- **Pluggable Storage**: JSON (default), PostgreSQL, MongoDB, Redis
- **Testing**: Use mock repositories in tests
- **Flexibility**: Different backends for dev vs production
- **Centralized Config**: `CachePathConfig` controls all cache locations

**See Also:** [Repository & Configuration Module](repository-config.md)

**LLMConfigManager**
- Loads YAML/JSON LLM configurations  
- Uses **repository pattern** for config persistence
- Provides config lookup by mode (creative/evaluation)
- Supports environment variable expansion
- Configurable cache location

#### 2. Provider Layer (`src/nikhil/pravaha/domain/storage/provider/`)

**StorageAPIProvider** (Coordinator)
- Creates FastAPI routes
- Delegates to specialized providers
- Handles configuration endpoints

**KnowledgeStorageProvider** (Simple)
- File tree browsing
- No versioning or metadata
- Direct path-based access

**IntermediateStorageProvider** (Feature + Timestamp)
- Version: Extracted from path or default
- Feature: From directory structure
- Timestamp-based versioning (YYYYMMDD_HHMMSS suffix)

**OutputStorageProvider** (Product/Feature + Suffix)
- Version: Semantic format (v1.0, v2.0)
- Feature: Business feature name
- Product: LLM model/config variant
- Suffix-based versioning (Model_v1, Model_v2)

#### 3. Logic Layer (`src/nikhil/pravaha/domain/storage/logic/`)

**StoragePathResolver**
- Resolves relative paths to absolute
- Handles path validation
- Supports all 3 categories

**ArtifactVersionResolver**
- Extracts version from filenames
- Parses timestamps and suffixes
- Determines "latest" version

## Data Flow

### Browse Request Flow

```
GET /api/storage/output/browse?feature=my-feature&product=gpt-4
    ↓
StorageAPIProvider._create_browse_handler("output")
    ↓
Delegates to OutputStorageProvider.browse(feature, product, model)
    ↓
1. Resolve base path: output_path / feature / product
2. Scan directory for files
3. Extract metadata (version, feature, product, display_name)
4. Build tree structure
5. Return JSON tree
    ↓
HTTP Response (JSON tree)
```

### Read Request Flow

```
GET /api/storage/output/read?path=v1.0/feature-a/gpt-4/result.json
    ↓
StorageAPIProvider._create_read_handler("output")
    ↓
Delegates to OutputStorageProvider.read(path)
    ↓
1. Resolve absolute path
2. Check file exists
3. Read file content
4. If .json: Parse and return object
5. Else: Return string content
    ↓
HTTP Response (JSON or string)
```

## Hierarchical Structure

### Output/Intermediate Hierarchy

```
output/
└── v1.0/                           # Version
    └── content-generation/         # Feature
        ├── gpt-4/                  # Product
        │   ├── article_v1.json
        │   └── article_v2.json     # Suffix versioning
        └── claude-3/               # Product
            └── article_v1.json
```

**Extraction Logic:**
- **Version**: First directory level (`v1.0`)
- **Feature**: Second directory level (`content-generation`)
- **Product**: Third directory level (`gpt-4`)
- **File Version**: Suffix in filename (`_v2`)

### Knowledge Simple Structure

```
knowledge/
├── docs/
│   └── guide.md
└── schemas/
    └── input.json
```

No metadata extraction - simple file browsing.

## Design Patterns

### 1. Coordinator Pattern
`StorageAPIProvider` coordinates multiple specialized providers without implementing browse/read logic itself.

### 2. Strategy Pattern
Different providers implement same interface (`browse`, `read`) with category-specific strategies.

### 3. Dependency Injection
Providers receive dependencies via constructor:
```python
def __init__(
    self,
    storage_manager: LocalStorageManager,
    llm_config_manager: LLMConfigManagerProtocol,
    path_resolver: StoragePathResolverProtocol,
    version_resolver: ArtifactVersionResolverProtocol
):
```

### 4. Protocol-Based Design
Uses protocols for `LLMConfigManagerProtocol`, `StoragePathResolverProtocol`, `ArtifactVersionResolverProtocol`.

## Key Design Decisions

### Why Three Separate Categories?

**Output**
- Long-term storage
- Product/feature organization
- Version tracking important

**Intermediate**
- Temporary/debug data
- Timestamp-based to track progress
- Can be cleaned up periodically

**Knowledge**
- Reference/static data
- No versioning needed
- Simple access pattern

### Why Version/Feature/Product Hierarchy?

**Benefits:**
1. **Organization** - Clear structure
2. **Comparison** - Easy to compare products (LLMs) for same feature
3. **Evolution** - Track versions over time
4. **Scalability** - Handles many features/products

### Why Coordinator + Specialized Providers?

**Original Problem:**
Single provider tried to handle all 3 categories with complex conditional logic.

**Solution:**
- Extract each category to dedicated provider
- Coordinator delegates based on category
- Each provider focuses on its specific logic

**Result:**
- 50% less code per provider
- Easier to test
- Simpler to extend

## Implementation Details

### Display Name Generation

```python
def _generate_display_name(filename: str, feature: str) -> str:
    """
    Generate user-friendly display name.
    
    Example:
        filename: "scientific_article_Gpt_4.json"
        feature: "content-generation"
        → "Scientific Article Gpt 4.json"
    """
    # Remove feature prefix
    name = filename.removeprefix(f"{feature}_")
    # Title case
    name = name.replace("_", " ").title()
    return name
```

### Version Extraction

```python
def extract_version(filename: str) -> Optional[str]:
    """
    Extract version suffix.
    
    Examples:
        "article_v1.json" → "v1"
        "article_gpt4_v2.json" → "v2"
        "article.json" → None
    """
    match = re.search(r'_v(\d+)', filename)
    return f"v{match.group(1)}" if match else None
```

## Configuration

### Storage Config Persistence

File: `.Pravaha/config/storage_config.json`

```json
{
  "output_path": "/absolute/path/to/output",
  "intermediate_path": "/absolute/path/to/intermediate",
  "knowledge_path": "/absolute/path/to/knowledge"
}
```

Auto-created on first use with defaults.

### LLM Config Integration

Storage providers use LLM config to determine "product" names dynamically:
- Product = LLM model ID from config
- Enables automatic organization by LLM variant

## Testing

### Unit Tests

Test each provider independently:
```python
def test_output_provider_browse():
    provider = OutputStorageProvider(manager, llm_config)
    tree = await provider.browse(feature="test", product="gpt-4")
    assert tree["type"] == "folder"
```

### Integration Tests

Test complete flow through `StorageAPIProvider`:
```python
def test_storage_api_browse(client):
    response = client.get("/api/storage/output/browse?feature=test")
    assert response.status_code == 200
```

## Performance Considerations

1. **Lazy Loading** - Only scans requested paths
2. **No Caching** - Always fresh data (important for real-time updates)
3. **JSON Parsing** - Only parses .json files on read, not browse
4. **Path Validation** - Prevents directory traversal attacks

## Future Enhancements

- [ ] Search across all artifacts
- [ ] Metadata indexing for faster queries
- [ ] File upload endpoints
- [ ] Versioned cleanup/archival
- [ ] S3/cloud storage backends
