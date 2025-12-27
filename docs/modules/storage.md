# Storage Module Documentation

The `storage` module provides a standardized way to manage file system paths for output, intermediate results, and knowledge bases.

## Components

### 1. Manager
Located in `src/nikhil/pravaha/domain/storage/manager/local_storage_manager.py`

`LocalStorageManager` handles directory creation and path resolution.

- **Config File**: `storage_config.json` (created automatically).
- **Default Paths**:
    - Output: `.Amsha/output/final/output`
    - Intermediate: `.Amsha/output/intermediate/output`
    - Knowledge: `data/knowledge`

### 2. API Provider
Located in `src/nikhil/pravaha/domain/storage/provider/storage_api_provider.py`

The `StorageAPIProvider` exposes endpoints to inspect reference directories:

- **POST `/storage/config`**: Update storage paths dynamically.
- **GET `/storage/{category}/folders`**: List folders in a category.
- **GET `/storage/{category}/{folder}/files`**: List files in a folder.
- **GET `/storage/{category}/{folder}/{file}`**: Retrieve file content (JSON or Text).

## Usage

```python
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider

manager = LocalStorageManager()
provider = StorageAPIProvider(manager)

app.include_router(provider.router)
```
