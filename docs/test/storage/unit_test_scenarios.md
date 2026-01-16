# Storage Module - Unit Test Scenarios

**Status**: Planning
**Source Code**: `src/nikhil/pravaha/domain/storage/`
**Docs**: `docs/modules/storage.md`

## 1. LocalStorageManager (`manager/local_storage_manager.py`)

### Happy Path
- [ ] **Init Defaults**: Initialize with defaults -> Check default paths exist.
- [ ] **Init Custom**: Initialize with custom paths -> Check config saved.
- [ ] **Repository Integration**: Mock config repo -> Verify loads/saves config.
- [ ] **Cache Config**: Verify `CachePathConfig` is respected for config storage.

### Failure Scenarios
- [ ] **Permission Error**: Directory creation fails -> Raise StorageError.

## 2. OutputStorageProvider (`provider/output_storage_provider.py`)

### Happy Path
- [ ] **Structure Logic**: Verify `v{X}/{feature}/{product}` path generation.
- [ ] **Browse Tree**: Browse root -> Returns correct version/feature structure.
- [ ] **File Metadata**: `_generate_file_metadata` extracts version/feature/product correctly from path.
- [ ] **Save Output**: Saves file to correct absolute path.

### Corner Cases
- [ ] **Suffix Versioning**: File `data_v2.json` -> extracts version `v2`.
- [ ] **Missing Metadata**: File `data.json` in root -> handles gracefully (defaults).

## 3. IntermediateStorageProvider (`provider/intermediate_storage_provider.py`)

### Happy Path
- [ ] **Structure Logic**: Verify `intermediate/{feature}/{product}`.
- [ ] **Browse**: Lists timestamped folders if applicable (or flat lists).
- [ ] **Timestamping**: Verify automatic timestamp/UUID generation on save.

## 4. KnowledgeStorageProvider (`provider/knowledge_storage_provider.py`)

### Happy Path
- [ ] **Browse Flat**: List files in root knowledge dir.
- [ ] **Browse Nested**: List files in `docs/guides/`.
- [ ] **Read File**: Read `.md` file content successfully.

## 5. StorageAPIProvider (`provider/storage_api_provider.py`)

### Happy Path
- [ ] **Delegation**: `browse("output")` calls `OutputProvider.browse`.
- [ ] **Delegation**: `browse("knowledge")` calls `KnowledgeProvider.browse`.
- [ ] **Config**: `get_config` returns current manager config.

### Failure Scenarios
- [ ] **Invalid Category**: `browse("invalid")` -> 400 Bad Request / 404.

## 6. Logic Layers (`logic/`)

### Path Resolver (`logic/path_resolver.py`)
- [ ] **Resolve Absolute**: Valid relative path -> Absolute path.
- [ ] **Security**: `../` traversal attempts -> Raise SecurityError.
- [ ] **Category Check**: Path outside category root -> Raise Error.

### Version Resolver (`logic/version_resolver.py`)
- [ ] **Extract Suffix**: `file_v12.json` -> `v12`.
- [ ] **No Suffix**: `file.json` -> `None`.
