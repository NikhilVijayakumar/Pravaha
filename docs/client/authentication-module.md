# Authentication Module - Client Documentation

> **💡 Quick Start:** Secure your Pravaha API with access keys and module-based permissions!

The Authentication module provides API access control using application-level access keys with fine-grained module permissions.

## Overview

Features:
- **API Access Keys**: Application-level authentication (not user login)
- **Module Permissions**: Control access to Bot, LLM, Storage, Workflow, Nibandha modules
- **Secure Storage**: SHA-256 hashed keys, shown only once during creation
- **Feature Discovery**: Query available capabilities per key
- **Pluggable Backends**: JSON default, PostgreSQL/MongoDB support

## Quick Start

### 1. Create Your First API Key

```bash
# Run bootstrap script
.venv/bin/python3 scripts/create_initial_api_key.py
```

Output:
```
✅ API Key Created Successfully!

🔑 API Key: xvK3jP7mN9qR2tY5wZ8aB1cD4eF6gH0iJ

⚠️  IMPORTANT: SAVE THIS KEY - IT WON'T BE SHOWN AGAIN!
```

### 2. Set Environment Variable

```bash
export PRAVAHA_API_KEY='xvK3jP7mN9qR2tY5wZ8aB1cD4eF6gH0iJ'
```

### 3. Use in API Requests

```bash
curl http://localhost:8000/api/storage/browse/output \
  -H 'X-API-Key: xvK3jP7mN9qR2tY5wZ8aB1cD4eF6gH0iJ'
```

## Module Permissions

Each access key grants permissions to specific modules:

| Module | Description | Example Endpoints |
|--------|-------------|-------------------|
| `bot` | Bot execution and task management | `/api/bot/run/utility`, `/api/bot/run/crew` |
| `llm` | LLM configuration management | `/api/llm/config` |
| `storage` | Artifact storage and retrieval | `/api/storage/browse`, `/api/storage/read` |
| `workflow` | Workflow definition and execution | `/api/workflow/list`, `/api/workflow/run` |

## Setup

### Enable Authentication (Default)

```python
from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.auth.config.auth_config import AuthConfig

# Auth enabled by default
app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager
)

# Keys stored in: .Pravaha/auth/access_keys.json
```

### Disable Authentication (Development)

```python
# Disable for local development
app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager,
    auth_config=AuthConfig.disabled()
)
```

### Custom Storage Backend

```python
from pravaha.domain.auth.protocol.access_key_repository_protocol import AccessKeyRepositoryProtocol

# Implement your own repository
class PostgreSQLAccessKeyRepository(AccessKeyRepositoryProtocol):
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
    
    def validate_key(self, key: str) -> bool:
        # Query PostgreSQL
        ...

# Use in app
postgres_repo = PostgreSQLAccessKeyRepository("postgresql://...")
app = create_fastapi_app(
    ...,
    access_key_repository=postgres_repo
)
```

## Creating Access Keys

### Programmatic Creation

```python
from pravaha.domain.auth.repository.json_access_key_repository import JsonAccessKeyRepository
from pravaha.domain.auth.model.module import PravahaModule

repo = JsonAccessKeyRepository()

# Create key with specific permissions
key = repo.create_key(
    name="CI/CD Pipeline",
    description="Automated deployment key",
    permissions=[PravahaModule.STORAGE, PravahaModule.WORKFLOW]
)

print(f"API Key: {key.key}")  # Save this!
print(f"Permissions: {[p.value for p in key.permissions]}")
```

### Full Access Key

```python
# Admin key with all permissions
admin_key = repo.create_key(
    name="Admin Key",
    description="Full access for administration",
    permissions=PravahaModule.all_modules()
)
```

### Limited Access Key

```python
# Read-only storage key
readonly_key = repo.create_key(
    name="Frontend App",
    description="Can only read storage",
    permissions=[PravahaModule.STORAGE]
)
```

## Managing Keys

### List All Keys

```python
# List active keys (key values are masked)
keys = repo.list_keys()

for key in keys:
    print(f"ID: {key.id}")
    print(f"Name: {key.name}")
    print(f"Permissions: {[p.value for p in key.permissions]}")
    print(f"Created: {key.created_at}")
    print(f"Last Used: {key.last_used}")
```

### Revoke a Key

```python
# Revoke compromised or unused key
repo.revoke_key(key_id="123e4567-e89b-12d3-a456-426614174000")
```

### Check Key Permissions

```python
# Get key details
key = repo.get_key_by_id("123e4567-...")

# Check specific permission
if key.has_permission(PravahaModule.STORAGE):
    print("✅ Can access storage")

# Check multiple permissions
if key.has_all_permissions([PravahaModule.STORAGE, PravahaModule.WORKFLOW]):
    print("✅ Can access storage and workflow")
```

## Using Access Keys

### In API Requests

```bash
# Include X-API-Key header
curl http://localhost:8000/api/storage/browse/output \
  -H 'X-API-Key: YOUR_API_KEY_HERE'
```

### In Python Requests

```python
import requests

headers = {
    "X-API-Key": "xvK3jP7mN9qR2tY5wZ8aB1cD4eF6gH0iJ"
}

response = requests.get(
    "http://localhost:8000/api/storage/browse/output",
    headers=headers
)

print(response.json())
```

### In JavaScript fetch

```javascript
const headers = {
    'X-API-Key': 'xvK3jP7mN9qR2tY5wZ8aB1cD4eF6gH0iJ'
};

fetch('http://localhost:8000/api/storage/browse/output', { headers })
    .then(res => res.json())
    .then(data => console.log(data));
```

## Feature Discovery & Frontend Integration

### Discovering Available Features

Frontend applications should use the **capabilities endpoint** to discover what features to show based on the current API key's permissions.

**How it works:**
1. Every API request includes `X-API-Key` header
2. Middleware validates key and checks module permissions automatically
3. Frontend calls `/api/auth/capabilities` on startup to know what features to display
4. Frontend conditionally renders UI based on available modules

### Capabilities Endpoint

```bash
# Get current key's capabilities
curl http://localhost:8000/api/auth/capabilities \
  -H 'X-API-Key: YOUR_API_KEY_HERE'
```

**Response:**
```json
{
  "key_id": "abc-123-def",
  "key_name": "Frontend App",
  "available_modules": ["storage", "workflow"],
  "endpoints": {
    "storage": [
      "/api/storage/browse/output",
      "/api/storage/browse/intermediate",
      "/api/storage/browse/knowledge",
      "/api/storage/read/output",
      "/api/storage/read/intermediate",
      "/api/storage/read/knowledge",
      "/api/storage/config"
    ],
    "workflow": [
      "/api/workflow/list",
      "/api/workflow/create",
      "/api/workflow/run",
      "/api/workflow/rename",
      "/api/workflow/delete"
    ]
  }
}
```

### Frontend Integration (Sangama - Electron/React)

**For the Sangama Electron UI:**

```javascript
// Initialize client with API key
class PravahaClient {
  constructor(apiKey, baseURL = 'http://localhost:8000') {
    this.apiKey = apiKey;
    this.baseURL = baseURL;
    this.capabilities = null;
  }
  
  // Discover capabilities on startup
  async init() {
    this.capabilities = await this.getCapabilities();
    return this.capabilities;
  }
  
  // Get current key's capabilities
  async getCapabilities() {
    const response = await fetch(`${this.baseURL}/api/auth/capabilities`, {
      headers: { 'X-API-Key': this.apiKey }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch capabilities');
    }
    
    return await response.json();
  }
  
  // Check if feature is available
  hasFeature(module) {
    return this.capabilities?.available_modules.includes(module);
  }
  
  // Make authenticated request
  async request(endpoint, options = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }
    
    return await response.json();
  }
}

// Usage in React components
const App = () => {
  const [client, setClient] = useState(null);
  const [capabilities, setCapabilities] = useState(null);
  
  useEffect(() => {
    const initClient = async () => {
      const apiKey = process.env.PRAVAHA_API_KEY;
      const pravahaClient = new PravahaClient(apiKey);
      const caps = await pravahaClient.init();
      
      setClient(pravahaClient);
      setCapabilities(caps);
    };
    
    initClient();
  }, []);
  
  if (!capabilities) return <LoadingSpinner />;
  
  return (
    <div>
      {capabilities.available_modules.includes('storage') && (
        <StorageFeature client={client} />
      )}
      
      {capabilities.available_modules.includes('workflow') && (
        <WorkflowFeature client={client} />
      )}
      
      {capabilities.available_modules.includes('bot') && (
        <BotFeature client={client} />
      )}
      
      {capabilities.available_modules.includes('llm') && (
        <LLMConfigFeature client={client} />
      )}
      
      {!capabilities.available_modules.includes('workflow') && (
        <div className="feature-disabled">
          Workflow features not available with current API key
        </div>
      )}
    </div>
  );
};
```

### Python Client Integration (Akashavani)

**For the Akashavani Python client:**

```python
import os
import requests
from typing import List, Dict, Any

class PravahaClient:
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:8000"):
        self.api_key = api_key or os.getenv("PRAVAHA_API_KEY")
        self.base_url = base_url
        self.capabilities = None
        
        if not self.api_key:
            raise ValueError("API key required. Set PRAVAHA_API_KEY environment variable.")
    
    def init(self) -> Dict[str, Any]:
        """Initialize and discover capabilities."""
        self.capabilities = self.get_capabilities()
        return self.capabilities
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get current key's capabilities."""
        response = self._request("GET", "/api/auth/capabilities")
        return response
    
    def has_feature(self, module: str) -> bool:
        """Check if feature is available."""
        if not self.capabilities:
            self.init()
        return module in self.capabilities.get("available_modules", [])
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make authenticated request."""
        headers = kwargs.pop("headers", {})
        headers["X-API-Key"] = self.api_key
        
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 401:
            raise PermissionError("API key required or invalid")
        elif response.status_code == 403:
            error = response.json()
            required = error.get("required_permission")
            available = error.get("available_permissions", [])
            raise PermissionError(
                f"Access denied. Required: {required}, Available: {available}"
            )
        
        response.raise_for_status()
        return response.json()
    
    # Feature-specific methods
    def get_storage_files(self, category: str):
        """Get storage files (requires 'storage' permission)."""
        if not self.has_feature("storage"):
            raise PermissionError("Storage feature not available with current key")
        return self._request("GET", f"/api/storage/browse/{category}")
    
    def list_workflows(self):
        """List workflows (requires 'workflow' permission)."""
        if not self.has_feature("workflow"):
            raise PermissionError("Workflow feature not available with current key")
        return self._request("GET", "/api/workflow/list")

# Usage
client = PravahaClient()
client.init()

# Check features before using
if client.has_feature("storage"):
    files = client.get_storage_files("output")
    print(f"Found {len(files)} files")
else:
    print("Storage feature not available")

if client.has_feature("workflow"):
    workflows = client.list_workflows()
    print(f"Found {len(workflows)} workflows")
```

### Public Features Endpoint

Get a list of ALL available features (no authentication required):

```bash
curl http://localhost:8000/api/auth/features
```

**Response:**
```json
{
  "bot": {
    "description": "Bot execution and task management",
    "endpoints": ["/api/bot/run/utility", "/api/bot/run/crew"]
  },
  "llm": {
    "description": "LLM configuration management",
    "endpoints": ["/api/llm/config"]
  },
  "storage": {
    "description": "Artifact storage and retrieval",
    "endpoints": [
      "/api/storage/browse/output",
      "/api/storage/read/knowledge",
      "..."
    ]
  },
  "workflow": {
    "description": "Workflow definition and execution",
    "endpoints": [
      "/api/workflow/list",
      "/api/workflow/create",
      "..."
    ]
  }
}
```

**Use case:** Display a feature comparison or "what you could access" page before API key creation.

## Permission Errors

### Access Denied Response

When a key lacks required permissions:

```json
{
  "detail": "Access denied. Key does not have 'llm' permission",
  "required_permission": "llm",
  "available_permissions": ["storage", "workflow"]
}
```

**What this means:**
- The endpoint requires `llm` permission
- Your key only has `storage` and `workflow`
- Create a new key with `llm` permission or use a different key

### Unauthorized Response

When API key is missing:

```json
{
  "detail": "API key required. Include X-API-Key header."
}
```

**Fix:** Add `X-API-Key` header to your request

### Forbidden Response

When API key is invalid or inactive:

```json
{
  "detail": "Invalid or inactive API key"
}
```

**Fix:** Check your key, it may be:
- Misspelled
- Revoked
- From a different environment

## Exempt Paths

These paths don't require authentication:

- `/health` - Health check endpoint
- `/docs` - API documentation
- `/openapi.json` - OpenAPI schema
- `/redoc` - ReDoc documentation

## Use Cases

### CI/CD Pipeline

```python
# Create deployment key
deploy_key = repo.create_key(
    name="GitHub Actions",
    description="Automated deployment from CI/CD",
    permissions=[
        PravahaModule.STORAGE,   # Upload artifacts
        PravahaModule.WORKFLOW   # Trigger workflows
    ]
)

# Use in GitHub Actions
# PRAVAHA_API_KEY secret = deploy_key.key
```

### Frontend Application

```python
# Create read-only key for frontend
frontend_key = repo.create_key(
    name="React App",
    description="Frontend application",
    permissions=[
        PravahaModule.STORAGE,   # Browse/read artifacts
        PravahaModule.WORKFLOW   # View workflow status
    ]
)
```

### Admin Dashboard

```python
# Create full-access key
admin_key = repo.create_key(
    name="Admin Dashboard",
    description="Full administrative access",
    permissions=PravahaModule.all_modules()
)
```

### Third-Party Integration

```python
# Limited integration key
integration_key = repo.create_key(
    name="Partner API",
    description="Integration with partner system",
    permissions=[PravahaModule.STORAGE]  # Only storage access
)
```

## Configuration Storage

### Default Location

Keys are stored in: `.Pravaha/auth/access_keys.json`

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "key": "5e884898da28047151d0e56f8dc...",  
    "name": "Production App",
    "permissions": ["storage", "workflow"],
    "created_at": "2026-01-16T10:00:00",
    "last_used": "2026-01-16T10:30:00",
    "is_active": true,
    "description": "Main production deployment"
  }
]
```

**Note:** Keys are hashed with SHA-256 for security.

### Custom Cache Location

```python
from pravaha.domain.config.cache_config import CachePathConfig

# Custom cache directory
cache_config = CachePathConfig.from_custom_root("/var/lib/pravaha")

repo = JsonAccessKeyRepository(cache_config=cache_config)
# Keys stored in: /var/lib/pravaha/auth/access_keys.json
```

## Best Practices

1. **Never commit keys to version control** - Use environment variables
2. **Create purpose-specific keys** - One key per application/service
3. **Limit permissions** - Only grant what's needed (principle of least privilege)
4. **Rotate keys regularly** - Create new, revoke old
5. **Monitor key usage** - Check `last_used` timestamps
6. **Revoke immediately** - If a key is compromised, revoke it ASAP
7. **Use descriptive names** - Name keys after their purpose

### Example: Environment Setup

```bash
# .env file (never commit this!)
PRAVAHA_API_KEY=xvK3jP7mN9qR2tY5wZ8aB1cD4eF6gH0iJ

# Load in application
import os
api_key = os.getenv("PRAVAHA_API_KEY")
```

### Example: Key Rotation

```python
# Create new key
new_key = repo.create_key(
    name="Production App v2",  
    permissions=old_key.permissions  # Same permissions
)

# Update deployment with new key
# ... deploy new_key.key ...

# After verification, revoke old key
repo.revoke_key(old_key.id)
```

## Troubleshooting

### "API key required" Error

**Problem:** Missing `X-API-Key` header

**Solution:**
```bash
curl http://localhost:8000/api/storage/browse/output \
  -H 'X-API-Key: YOUR_KEY_HERE'  # Add this header
```

### "Access denied" Error

**Problem:** Key lacks required permission

**Solution:**
1. Check error response for `required_permission`
2. Check `available_permissions`
3. Create new key with correct permissions OR use different key

### "Invalid or inactive" Error

**Problem:** Key is revoked or doesn't exist

**Solution:**
1. Verify key is correct (no typos)
2. Check if key was revoked: `repo.get_key_by_id(key_id)`
3. Create new key if needed

## Security Notes

- **Keys are hashed**: Stored as SHA-256 hashes, cannot be recovered
- **One-time view**: Raw key shown only during creation
- **Audit trail**: `last_used` timestamp tracks key activity
- **Revocation**: Instantly disable compromised keys
- **No rate limiting** (yet): Monitor usage manually

## Next Steps

- 📖 **API Factory Documentation**: [docs/client/api-factory.md](api-factory.md)
- 🔧 **Module Documentation**: [docs/modules/authentication.md](../modules/authentication.md)
- 🚀 **Deploy with Auth**: Update production config with authentication enabled
