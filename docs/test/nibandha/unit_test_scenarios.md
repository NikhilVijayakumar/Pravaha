# Nibandha Integration - Unit Test Scenarios

## 1. Logging Manager
Target: `src/nikhil/pravaha/domain/logging/manager/logging_manager.py`
Test File: `tests/unit/domain/logging/test_logging_manager.py`

### 1.1 Singleton Behavior
- **[UT-NIB-001] Singleton Instance**: Verify that `PravphaLoggingManager.get_instance()` returns the same instance on multiple calls.
- **[UT-NIB-002] Auto-Initialization**: Verify that `get_logger()` initializes the manager if it hasn't been initialized yet.

### 1.2 Logger Retrieval
- **[UT-NIB-003] Logger Binding**: Verify `get_logger()` returns a valid logger instance (mocked/stubbed Nibandha).

## 2. Rotation Utils
Target: `src/nikhil/pravaha/domain/logging/utils/rotation_utils.py`
Test File: `tests/unit/domain/logging/test_rotation_utils.py`

### 2.1 Configuration Setup
- **[UT-NIB-004] Setup Rotation**: Verify `setup_rotation` writes correct YAML configuration to the expected path (mocked file system).
- **[UT-NIB-005] Default Configuration**: Verify default values are used if not provided.

### 2.2 Rotation Logic
- **[UT-NIB-006] Check & Rotate**: Verify `check_and_rotate` calls `should_rotate` and `rotate_logs` on the Nibandha instance (mocked).
- **[UT-NIB-007] Cleanup**: Verify `cleanup_old_logs` delegates to `cleanup_old_archives`.
