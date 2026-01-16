# Bot Module - E2E Test Scenarios

## 1. Execution Lifecycle
Target: `tests/e2e/domain/bot/scenarios/test_bot_execution.py`

### 1.1 Utility Task Execution
- **[E2E-BOT-001] Sync Task Flow**:
  - POST `/run/utility` with valid inputs.
  - Verify 200 OK and expected JSON result.
  - Mock manager ensures inputs are passed correctly.

### 1.2 Application Streaming Execution
- **[E2E-BOT-002] Async Stream Flow**:
  - POST `/run/application/stream` with valid inputs.
  - Verify response is `text/event-stream`.
  - Verify chunks are received in order.
  - Verify proper termination.

### 1.3 LLM Config Override
- **[E2E-BOT-003] Runtime Config Override**:
  - POST `/run/application/stream` with `llm_config_override`.
  - Verify manager receives the override object.
  - Validate that execution behavior changes (mocked) based on override.

### 1.4 Protocol Introspection
- **[E2E-BOT-004] Schema & Config Discovery**:
  - GET `/enums/util-types` and verify list.
  - GET `/protocol/schema/input/{task_name}` and validate schema structure.
  - GET `/protocol/config/{task_name}` and validate config return.
