# API Factory - E2E Test Scenarios

## 1. Integration Wiring
Target: `tests/e2e/domain/api/factory/scenarios/test_factory_integration.py`

### 1.1 Full Stack Wiring
- **[E2E-FAC-001] App Startup**: Start app via factory and verify it handles requests to all modules without 500 errors (using Mock managers).
- **[E2E-FAC-002] Cross-Module Config**: Verify LLM config works across modules (e.g. Storage uses LLM config for paths).

### 1.2 Configuration Overrides
- **[E2E-FAC-003] Custom LLM Config**: Start app with custom `llm_config.yaml` and verify endpoint reflects loaded config.
