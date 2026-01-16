# API Factory - Unit Test Scenarios

## 1. Application Construction
Target: `src/nikhil/pravaha/domain/api/factory/api_factory.py`
Test File: `tests/unit/domain/api/factory/test_api_factory.py`

### 1.1 App Initialization
- **[UT-FAC-001] Basic Initialization**: Verify `create_fastapi_app` returns valid FastAPI instance with correct title.
- **[UT-FAC-002] Health Check**: Verify `/health` endpoint returns 200 OK.
- **[UT-FAC-003] CORS Middleware**: Verify CORS middleware is added (check `app.middleware_stack`).

### 1.2 Router Mounting
- **[UT-FAC-004] Default Prefix**: Verify routers are mounted at `/api`.
- **[UT-FAC-005] Custom Prefix**: Verify routers respect custom prefix (e.g., `/v1`).
- **[UT-FAC-006] Module Routes**:
  - Verify Bot routes (`/bot/run/utility` etc.)
  - Verify Storage routes (`/storage/output/browse` etc.)
  - Verify Workflow routes (`/workflow/list` etc.)
  - Verify LLM routes (`/llm/configs` etc.)

### 1.3 Dependency Injection
- **[UT-FAC-007] LLM Config Path**: Verify `LLMConfigManager` is initialized with provided path.
- **[UT-FAC-008] Manager Propagation**: Verify provided managers (Bot, Storage) are passed to providers.
