# Authentication Module - Technical Documentation

> **Audience:** Pravaha contributors and maintainers  
> **Client Documentation:** [docs/client/authentication-module.md](../client/authentication-module.md)

## Module Objective

The Authentication module provides **API access control with module-based permissions**:

1. **Access Keys** - Application-level authentication (not user login)
2. **Module Permissions** - Fine-grained access to Bot, LLM, Storage, Workflow, Nibandha
3. **Protocol-Based Storage** - Pluggable backends (JSON default, PostgreSQL/MongoDB support)
4. **Feature Discovery** - API to query available capabilities per key

## Architecture

### Middleware + Repository Pattern

```
┌─────────────────────────────────────────┐
│        FastAPI Application              │
│  ┌───────────────────────────────────┐  │
│  │  APIKeyMiddleware                 │  │
│  │  - Validates X-API-Key header     │  │
│  │  - Checks module permissions      │  │
│  └────────────┬──────────────────────┘  │
│               ↓                          │
│  ┌────────────────────────────────────┐ │
│  │  AccessKeyRepository               │ │
│  │  - Protocol-based                  │ │
│  │  - JSON default                    │ │
│  │  - PostgreSQL/MongoDB support      │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Why Module Permissions?**
- **Least Privilege** - Keys only access what they need
- **Security** - Limit blast radius of compromised keys
- **Multi-App Support** - Different apps get different permissions

### Components

#### 1. Model Layer (`src/nikhil/pravaha/domain/auth/model/`)

**PravahaModule (Enum)**
```python
class PravahaModule(str, Enum):
    BOT = "bot"           # Bot execution and task management
    LLM = "llm"           # LLM configuration management
    STORAGE = "storage"   # Artifact storage and retrieval
    WORKFLOW = "workflow" # Workflow definition and execution
    NIBANDHA = "nibandha" # Logging and observability
```

**AccessKey (Model)**
```python
@dataclass
class AccessKey:
    id: str                              # UUID
    key: str                             # Hashed (SHA-256)
    name: str                            # Human-readable
    permissions: List[PravahaModule]     # Module access list
    created_at: datetime
    last_used: Optional[datetime]
    is_active: bool
    description: Optional[str]
    
    def has_permission(self, module: PravahaModule) -> bool:
        """Check if key has access to a module."""
        return module in self.permissions
```

#### 2. Protocol Layer (`src/nikhil/pravaha/domain/auth/protocol/`)

**AccessKeyRepositoryProtocol**
```python
class AccessKeyRepositoryProtocol(Protocol):
    def validate_key(self, key: str) -> bool: ...
    def get_key_by_value(self, key: str) -> Optional[AccessKey]: ...
    def create_key(
        self, 
        name: str,
        permissions: List[PravahaModule]
    ) -> AccessKey: ...
    def revoke_key(self, key_id: str) -> None: ...
    def list_keys(self) -> List[AccessKey]: ...
```

#### 3. Repository Layer (`src/nikhil/pravaha/domain/auth/repository/`)

**JsonAccessKeyRepository**
- Stores keys in `.Pravaha/auth/access_keys.json`
- SHA-256 hashing for secure storage
- Random key generation (`secrets.token_urlsafe(32)`)
- Permission-aware CRUD operations

#### 4. Middleware Layer (`src/nikhil/pravaha/domain/auth/middleware/`)

**APIKeyMiddleware**
- Validates `X-API-Key` header
- Maps request paths to required modules
- Checks permissions
- Attaches `access_key` to `request.state`
- Returns descriptive 403 errors

#### 5. Config Layer (`src/nikhil/pravaha/domain/auth/config/`)

**AuthConfig**
```python
@dataclass
class AuthConfig:
    enabled: bool = True
    exempt_paths: List[str] = ["/health", "/docs", "/openapi.json"]
```

## Data Flow

### Authentication Request Flow

```
Client Request with X-API-Key header
    ↓
APIKeyMiddleware.dispatch()
    ↓
1. Check if path is exempt (e.g., /health)
    ├─ Yes → Allow (skip auth)
    └─ No → Continue
    ↓
2. Extract X-API-Key header
    ├─ Missing → 401 Unauthorized
    └─ Present → Continue
    ↓
3. Validate key via repository
    repository.get_key_by_value(api_key)
    ├─ Invalid/Inactive → 403 Forbidden
    └─ Valid → Continue
    ↓
4. Determine required module
    _get_required_module(request.url.path)
    # /api/storage/browse → STORAGE
    # /api/workflow/run → WORKFLOW
    ↓
5. Check permission
    access_key.has_permission(required_module)
    ├─ No → 403 with details
    └─ Yes → Continue
    ↓
6. Update last_used timestamp
    repository.update_last_used(access_key.id)
    ↓
7. Attach to request state
    request.state.access_key = access_key
    ↓
Proceed to endpoint handler
```

### Key Creation Flow

```
Create Key Request
    ↓
repository.create_key(name, permissions)
    ↓
1. Generate random key
    raw_key = secrets.token_urlsafe(32)
    ↓
2. Hash for storage
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
    ↓
3. Create AccessKey object
    AccessKey(
        id=uuid4(),
        key=hashed_key,  # Store hash
        permissions=permissions
    )
    ↓
4. Save to storage
   _save_keys(keys)  # JSON file
    ↓
5. Return with raw key (ONLY TIME SHOWN)
    AccessKey(..., key=raw_key)
```

## Module-to-Path Mapping

The middleware maps API paths to required permissions:

| Path Prefix | Required Module | Example Endpoints |
|------------|----------------|-------------------|
| `/api/bot` | `BOT` | `/api/bot/run/utility`, `/api/bot/run/crew` |
| `/api/llm` | `LLM` | `/api/llm/config` |
| `/api/storage` | `STORAGE` | `/api/storage/browse/output`, `/api/storage/read` |
| `/api/workflow` | `WORKFLOW` | `/api/workflow/list`, `/api/workflow/run` |
| `/api/nibandha` | `NIBANDHA` | `/api/nibandha/logs` |

**Exempt Paths (No Auth):**
- `/health` - Health check
- `/docs` - API documentation
- `/openapi.json` - OpenAPI schema
- `/redoc` - ReDoc documentation

## Permission Denied Error Response

```json
{
  "detail": "Access denied. Key does not have 'llm' permission",
  "required_permission": "llm",
  "available_permissions": ["storage", "workflow"]
}
```

**Benefits:**
- Clear error message
- Shows what's needed
- Shows what's available
- Helps debugging

## Design Patterns

### 1. Protocol-Based Design
All storage backends implement `AccessKeyRepositoryProtocol`:
- JSON (default)
- PostgreSQL (client-implemented)
- MongoDB (client-implemented)
- Redis (client-implemented)

### 2. Secure by Default
- Keys never stored in plain text (SHA-256 hash)
- Raw key shown only once during creation
- Last-used timestamp tracking for auditing

### 3. Middleware Pattern
Authentication logic separated from business logic:
- Single point of authentication
- Consistent across all endpoints
- Easy to enable/disable

### 4. Dependency Injection
Middleware receives repository via constructor:
```python
APIKeyMiddleware(
    app=app,
    repository=access_key_repository,
    exempt_paths=["/health"]
)
```

## Key Design Decisions

### Why Application-Level Keys (not User Auth)?

**Use Case:**
- Service-to-service communication
- CI/CD pipelines
- Multiple client applications
- API integrations

**Benefits:**
- Simpler than OAuth2/JWT
- No user management needed
- Easy key rotation
- Application-scoped permissions

### Why Module-Based Permissions?

**Problem:**
Single "admin" key has too much access. All-or-nothing permissions.

**Solution:**
Granular module permissions. Same API behaves differently per key.

**Example:**
```python
# CI/CD key - only storage and workflow
ci_key = create_key(
    name="CI/CD Pipeline",
    permissions=[PravahaModule.STORAGE, PravahaModule.WORKFLOW]
)

# Admin key - full access
admin_key = create_key(
    name="Admin",
    permissions=PravahaModule.all_modules()
)
```

### Why Protocol-Based Repository?

**Flexibility:**
- Dev: JSON files
- Production: PostgreSQL
- High-performance: Redis
- Multi-region: DynamoDB

**Interface remains same:**
```python
# Client implements protocol
class PostgreSQLAccessKeyRepository(AccessKeyRepositoryProtocol):
    def validate_key(self, key: str) -> bool:
        # Query PostgreSQL
        ...

# Use in app
app = create_fastapi_app(
    access_key_repository=PostgreSQLAccessKeyRepository(conn_string)
)
```

## Implementation Details

### SHA-256 Hashing

```python
def _hash_key(self, key: str) -> str:
    """Hash API key for secure storage."""
    return hashlib.sha256(key.encode()).hexdigest()
```

**Why SHA-256?**
- One-way (cannot reverse)
- Fast verification
- Industry standard
- No salt needed (keys are random)

### Secure Key Generation

```python
def _generate_key(self) -> str:
    """Generate secure random API key."""
    return secrets.token_urlsafe(32)  # 256 bits of entropy
```

**Why `secrets` module?**
- Cryptographically secure (not `random`)
- URL-safe encoding
- 32 bytes = 43 characters

### Permission Checking

```python
def has_permission(self, module: PravahaModule) -> bool:
    """Check if key has permission for a module."""
    return module in self.permissions

def has_all_permissions(self, modules: List[PravahaModule]) -> bool:
    """Check if key has all specified permissions."""
    return all(m in self.permissions for m in modules)
```

## Configuration

### Storage Location

File: `.Pravaha/auth/access_keys.json`

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "key": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
    "name": "Production App",
    "permissions": ["storage", "workflow"],
    "created_at": "2026-01-16T10:00:00",
    "last_used": "2026-01-16T10:30:00",
    "is_active": true,
    "description": "Main production deployment"
  }
]
```

### Custom Cache Location

```python
from pravaha.domain.config.cache_config import CachePathConfig

# Custom cache directory
cache_config = CachePathConfig.from_custom_root("/var/lib/pravaha")

# Keys stored in: /var/lib/pravaha/auth/access_keys.json
repo = JsonAccessKeyRepository(cache_config=cache_config)
```

## Bootstrap & Setup

### Initial Key Creation

```bash
.venv/bin/python3 scripts/create_initial_api_key.py
```

Output:
```
============================================================
  PRAVAHA API KEY BOOTSTRAP
============================================================

Creating admin API key with all module permissions...

✅ API Key Created Successfully!

============================================================
Key ID: 123e4567-e89b-12d3-a456-426614174000
Key Name: Initial Admin Key
Permissions: bot, llm, storage, workflow, nibandha
============================================================

🔑 API Key: xvK3jP7mN9qR2tY5wZ8aB1cD4eF6gH0iJ

============================================================
⚠️  IMPORTANT: SAVE THIS KEY - IT WON'T BE SHOWN AGAIN!
============================================================
```

### Environment Setup

```bash
# Add to .bashrc or .env
export PRAVAHA_API_KEY='xvK3jP7mN9qR2tY5wZ8aB1cD4eF6gH0iJ'
```

## Testing

### Unit Tests

```python
def test_access_key_permission():
    key = AccessKey(
        id="test-id",
        key="hashed",
        name="Test",
        permissions=[PravahaModule.STORAGE]
    )
    
    assert key.has_permission(PravahaModule.STORAGE)
    assert not key.has_permission(PravahaModule.BOT)

def test_json_repository_create():
    repo = JsonAccessKeyRepository()
    key = repo.create_key(
        name="Test Key",
        permissions=[PravahaModule.LLM, PravahaModule.STORAGE]
    )
    
    assert len(key.key) > 0  # Raw key returned
    assert len(key.permissions) == 2
```

### Integration Tests

```python
def test_middleware_authentication(client):
    # Valid key
    response = client.get(
        "/api/storage/browse/output",
        headers={"X-API-Key": "valid_key"}
    )
    assert response.status_code == 200
    
    # Invalid key
    response = client.get(
        "/api/storage/browse/output",
        headers={"X-API-Key": "invalid"}
    )
    assert response.status_code == 403
    
    # Missing key
    response = client.get("/api/storage/browse/output")
    assert response.status_code == 401
```

### Permission Tests

```python
def test_permission_denied(client):
    # Key with only STORAGE permission
    response = client.get(
        "/api/llm/config",
        headers={"X-API-Key": "storage_only_key"}
    )
    
    assert response.status_code == 403
    assert "llm" in response.json()["required_permission"]
    assert "storage" in response.json()["available_permissions"]
```

## Performance Considerations

1. **Fast Validation** - O(1) hash comparison
2. **Minimal Overhead** - Single DB lookup per request
3. **No Encryption** - Hashing is fast (SHA-256 is optimized)
4. **Cached Repository** - Can add in-memory cache for hot keys

## Security Best Practices

1. **Never log API keys** - Log only key IDs
2. **Rotate keys regularly** - Revoke old, create new
3. **Limit permissions** - Only grant what's needed
4. **Monitor usage** - Track `last_used` timestamps
5. **Revoke compromised keys immediately**

```python
# Good - Log key ID
logger.info(f"Request from key {access_key.id}")

# Bad - Never log key value
logger.info(f"Request with key {api_key}")  # ❌
```

## Future Enhancements

- [ ] Key expiration (TTL)
- [x] Last-used tracking
- [ ] Rate limiting per key
- [ ] Key usage analytics
- [ ] Automatic key rotation
- [ ] Multi-factor authentication for key creation
- [ ] IP whitelisting per key
- [ ] Webhook notifications for key events
