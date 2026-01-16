# Authentication Module - Unit Test Scenarios

**Status**: Planning  
**Source Code**: `src/nikhil/pravaha/domain/auth/`  
**Docs**: `docs/modules/authentication.md`

## 1. AccessKey Model (`model/access_key.py`)

### Happy Path
- [ ] **Creation**: Create key with valid UUID, hash, name, permissions.
- [ ] **Permission Check (Single)**: `has_permission` returns True for assigned module.
- [ ] **Permission Check (All)**: `has_all_permissions` returns True when all match.

### Failure Scenarios
- [ ] **Permission Check (Fail)**: `has_permission` returns False for unassigned module.
- [ ] **Permission Check (All Fail)**: `has_all_permissions` returns False if one is missing.

### Corner Cases
- [ ] **Empty Permissions**: Key created with empty list permissions (valid, but useless).
- [ ] **Case Sensitivity**: Verify if module checks are strict on Enum types.

## 2. JSON Repository (`repository/json_access_key_repository.py`)

### Happy Path
- [ ] **Create Key**: Successfully writes new key to JSON file.
- [ ] **Retrieve Key**: `get_key_by_value` finds key by raw string.
- [ ] **List Keys**: Returns all active keys.
- [ ] **Update Last Used**: Updates timestamp on usage.
- [ ] **Revoke Key**: Sets `is_active=False`.

### Failure Scenarios
- [ ] **Invalid Key**: `get_key_by_value` returns None for unknown string.
- [ ] **Revoked Key Access**: `get_key_by_value` returns Key object (active status checked by service).
- [ ] **File Not Found**: Repository handles missing JSON file (creates new?).

### Corner Cases
- [ ] **Concurrent Writes**: (If supported) what happens if two creating at once? (Local/JSON might not support).
- [ ] **Corrupted JSON**: Handled gracefully or raises error?

## 3. API Middleware (`middleware/api_key_middleware.py`)

### Happy Path
- [ ] **Valid Auth**: Request with valid header & permission -> 200 OK.
- [ ] **Exempt Path**: Request to `/health` with NO header -> 200 OK.

### Failure Scenarios
- [ ] **Missing Header**: Request to protected Path -> 401 Unauthorized.
- [ ] **Invalid Key**: Header present but unknown/revoked -> 403 Forbidden.
- [ ] **Wrong Permission**: Valid key but wrong module -> 403 Forbidden with details.

### Corner Cases
- [ ] **Malformed Header**: Empty string or weird characters.
- [ ] **Root Path**: Auth behavior on `/`.
- [ ] **Case Sensitivity**: Header Name (`x-api-key` vs `X-API-Key`).
