# Nibandha Integration - E2E Test Scenarios

## 1. Integration Lifecycle
Target: `tests/e2e/domain/logging/scenarios/test_logging_lifecycle.py`

### 1.1 Application Bootstrapping
- **[E2E-NIB-001] Auto-Initialization in App**:
  - Initialize `PravphaLoggingManager`.
  - Verify that logging directory structure is created (mocked FS or temp dir).
  - Verify first log message is written.

### 1.2 Rotation Flow
- **[E2E-NIB-002] Rotation Configuration & Execution**:
  - Call `LogRotationUtils.setup_rotation`.
  - Simulate log growth (mock logic or force rotate).
  - Call `LogRotationUtils.check_and_rotate`.
  - Verify rotation occurred (mocked interaction).

### 1.3 Logging Formatting
- **[E2E-NIB-003] Log Format**:
  - Write log messages at different levels.
  - Verify the log file content follows the `<timestamp> | <logger> | <level> | <message>` format (if testable via file read).
