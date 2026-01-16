# LLM Module - E2E Test Scenarios

## 1. Configuration Lifecycle
Target: `tests/e2e/domain/llm/scenarios/test_llm_config_lifecycle.py`

### 1.1 Config Persistence
- **Scenario**:
    1.  Start API with clean state (no config or default config).
    2.  `GET /api/llm/config` to verify initial state.
    3.  `POST /api/llm/config` (if update endpoint exists) OR verify through file modification + reload (if API only supports read for now, check `implementation_plan`).
    *   *Note*: Current `LLMAPIProvider` only exposes `GET`. If `update` is planned, test it here.
    *   *Alternative*: Test that User modifying YAML file is reflected in API (simulating startup).

### 1.2 Model Resolution (Future/Planned)
- **Scenario**:
    1.  Define a test model in config with specific `output_config`.
    2.  Call a "Resolve" endpoint (if added) or verify `GET /api/llm/config` structure contains parsed/resolved paths.

## 2. Integration with Applications
- **Scenario**:
    1.  Configure specific parameters (e.g., `temperature`) for a generic model key.
    2.  Verify that downstream components (like CrewAI orchestrator, tested via mock) receive this consolidated configuration.
