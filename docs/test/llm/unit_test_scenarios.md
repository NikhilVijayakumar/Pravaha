# LLM Module - Unit Test Scenarios

## 1. Domain Entities
(Entities are currently simple Pydantic models or Dicts, minimal testing needed unless complex logic added)

## 2. Infrastructure (Repositories)
Target: `tests/unit/domain/llm/infrastructure/test_json_llm_repository.py`

### 2.1 JSON Config Repository
- **[UT-LLM-REP-001] Save and Load Config**: Verify saving a dictionary config and retrieving it via `get_config`.
- **[UT-LLM-REP-002] Persistence**: Verify changes persist to the underlying JSON file using `update_config`.
- **[UT-LLM-REP-003] Missing File Handling**: Verify behavior when config file is missing (should return valid default or empty dict).
- **[UT-LLM-REP-004] Resolve Output Config**: Verify `resolve_output_config` method correctly extracts model-specific settings (e.g., predicted output paths).

## 3. Domain Services / Managers
Target: `tests/unit/domain/llm/manager/test_llm_config_manager.py`
(Refactoring `tests/unit/domain/storage/manager/test_llm_config_json.py`)

### 3.1 Config Loading & Caching
- **[UT-LLM-MGR-001] YAML to JSON Cache**: Verify that initializing with a YAML path creates a JSON cache (migration logic).
- **[UT-LLM-MGR-002] Load from Cache**: Verify that if JSON cache exists, it is preferred/loaded.
- **[UT-LLM-MGR-003] Config Update**: Verify `update_config` delegates to repository and updates cache.

## 4. API Providers
Target: `tests/unit/domain/llm/provider/test_llm_api.py`

### 4.1 Config Endpoints
- **[UT-LLM-API-001] Get Config Success**: Verify `GET /api/llm/config` returns full configuration from manager.
- **[UT-LLM-API-002] Get Config Error**: Verify 500 handling if manager errors out.
