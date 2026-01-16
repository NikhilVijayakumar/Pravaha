# Repository Config - Unit Test Scenarios

## 1. CachePathConfig
Target: `tests/unit/domain/config/test_cache_config.py`

### 1.1 Initialization Strategies
- **[UT-CFG-001] Default Initialization**: Verify `CachePathConfig.default()` uses `.Pravaha` root and derived subdirectories.
- **[UT-CFG-002] Custom Root**: Verify `CachePathConfig.from_custom_root("/tmp/custom")` sets root and correctly derives storage/llm/workflow paths under that root.
- **[UT-CFG-003] Explicit Overrides**: Verify constructor allows overriding specific component paths (e.g., specific `storage_cache_dir`) while keeping others derived from root.

### 1.2 Path Resolution Logic
- **[UT-CFG-004] Storage Path**: Verify `get_storage_cache_dir()` returns `{root}/config` if not overridden, or the override path.
- **[UT-CFG-005] LLM Path**: Verify `get_llm_cache_dir()` returns `{root}/config` if not overridden, or the override path.
- **[UT-CFG-006] Workflow Path**: Verify `get_workflow_cache_dir()` returns `{root}/config` if not overridden, or the override path.
