# Bot Module - Unit Test Scenarios

## 1. Protocol Layer
Target: `src/nikhil/pravaha/domain/bot/protocol/`

### 1.1 Type Safety & Protocol Compliance
- **[UT-BOT-001] Protocol Adherence**: Verify that a compliant manager implements all required methods (`run`, `stream_run`, `get_input_model`, `get_output_model`, `get_config`).
- **[UT-BOT-002] Generic Typing**: Verify that the protocol correctly handles generic `UT` (Utility Task) and `AT` (Application Task) Enums.

## 2. API Provider
Target: `src/nikhil/pravaha/domain/bot/provider/bot_api_provider.py`
Test File: `tests/unit/domain/bot/provider/test_bot_api.py`

### 2.1 Route Registration
- **[UT-BOT-003] Route Setup**: Verify all expected routes (`/run/utility`, `/run/application/stream`, enums, schemas) are registered upon initialization.

### 2.2 Task Resolution
- **[UT-BOT-004] Enum Resolution**: Verify `_get_task_enum` correctly resolves string task names to their corresponding Enum members (checking UtilsType first, then ApplicationType).
- **[UT-BOT-005] Invalid Task Name**: Verify `_get_task_enum` returns `None` or raises acceptable error for non-existent task names.

### 2.3 Execution Endpoints
- **[UT-BOT-006] Utility Execution**: Verify `POST /run/utility` correctly calls `manager.run` and returns result.
- **[UT-BOT-007] Utility Error Handling**: Verify proper HTTP 500 mapping when manager raises exception during utility run.
- **[UT-BOT-008] Stream Execution**: Verify `POST /run/application/stream` correctly calls `manager.stream_run` and returns streaming response.

### 2.4 Schema & Config Endpoints
- **[UT-BOT-009] Input Schema**: Verify `GET /protocol/schema/input/{task}` returns JSON schema derived from Pydantic model.
- **[UT-BOT-010] Config Introspection**: Verify `GET /protocol/config/{task}` delegates to `manager.get_config` and returns valid JSON.

## 3. Streaming Utilities
Target: `src/nikhil/pravaha/domain/bot/streaming/`

### 3.1 Async Conversion
- **[UT-BOT-011] Sync to Async Stream**: Verify utility maps synchronous iterable to async generator without blocking.
