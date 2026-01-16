# Pravaha - Enterprise FastAPI Framework for LLM Applications

**Version:** 2.0.0  
**Python:** 3.8+

Pravaha is a production-ready FastAPI framework providing modular architecture for building LLM and agent applications with built-in authentication, storage management, workflow orchestration, and comprehensive configuration capabilities.

---

## ✨ Key Features

### 🔐 **Authentication & Security**
- API key-based authentication with SHA-256 hashing
- Module-based permissions (Bot, LLM, Storage, Workflow)
- Feature discovery and capability management
- Pluggable storage backends (JSON, PostgreSQL, MongoDB)

### 📦 **Storage Management**
- Organized artifact storage (Output, Intermediate, Knowledge)
- Version resolution and LLM-aware metadata
- Recursive browsing and file reading APIs
- Configurable storage backends

### 🔄 **Workflow Engine**
- Visual multi-step workflow execution
- Topological dependency resolution
- State persistence and restartability
- LLM configuration injection

### 🤖 **Bot Integration**
- Protocol-based design for any bot/agent framework
- Dual execution modes (sync utilities + async streaming)
- Server-Sent Events (SSE) for real-time responses
- CrewAI and custom agent support

### ⚙️ **Configuration & Extensibility**
- Protocol-based repository pattern for all config
- Centralized cache management with `CachePathConfig`
- Custom backend implementations supported
- Environment-specific configuration

### 📊 **Logging & Observability**
- Production-ready logging with Nibandha integration
- Automatic log rotation and archival
- Centralized timestamped logs
- Zero-configuration setup

---

## 📚 Documentation

### For Users (Implementing Pravaha)

**Start Here:** [Client Documentation Index](docs/client/README.md)

| Module | Description | Documentation |
|--------|-------------|---------------|
| **API Factory** | One-line FastAPI app creation | [docs/client/api-factory.md](docs/client/api-factory.md) |
| **Authentication** | API keys & permissions | [docs/client/authentication-module.md](docs/client/authentication-module.md) |
| **Bot Module** | Task execution & streaming | [docs/client/bot-module.md](docs/client/bot-module.md) |
| **Storage** | File organization & retrieval | [docs/client/storage-module.md](docs/client/storage-module.md) |
| **Workflow** | Multi-step orchestration | [docs/client/workflow-module.md](docs/client/workflow-module.md) |
| **LLM Config** | Model configuration management | [docs/client/llm-module.md](docs/client/llm-module.md) |

**Client SDKs:**
- [Sangama (Electron UI)](docs/client/sangama/) - Frontend integration guide
- [Akashavani (Python Client)](docs/client/akashavani/) - Library usage guide

### For Contributors (Developing Pravaha)

**Technical Documentation:** [Module Documentation](docs/modules/)

| Module | Purpose | Documentation |
|--------|---------|---------------|
| **Authentication** | Security architecture | [docs/modules/authentication.md](docs/modules/authentication.md) |
| **Repository Pattern** | Configuration storage | [docs/modules/repository-config.md](docs/modules/repository-config.md) |
| **Bot Module** | Execution engine | [docs/modules/bot.md](docs/modules/bot.md) |
| **Storage** | Artifact management | [docs/modules/storage.md](docs/modules/storage.md) |
| **Workflow** | Orchestration engine | [docs/modules/workflow.md](docs/modules/workflow.md) |
| **LLM** | Config management | [docs/modules/llm.md](docs/modules/llm.md) |
| **Nibandha** | Logging integration | [docs/modules/nibandha-integration.md](docs/modules/nibandha-integration.md) |

**Architecture:**
- [Architecture.md](docs/Architecture.md) - Design principles & standards
- [API Factory](docs/modules/api-factory.md) - Factory pattern details

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd Pravaha

# Create virtual environment
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.\.venv\Scripts\Activate.ps1

# Install in editable mode
pip install -e .
```

### 2. Create API Key

```bash
# Generate initial admin key
.venv/bin/python3 scripts/create_initial_api_key.py

# Save the key - it's shown only once!
export PRAVAHA_API_KEY='your-key-here'
```

### 3. Create Your First App

```python
from pravaha.domain.api.factory.api_factory import create_fastapi_app
from pravaha.domain.bot.manager.simple_bot_manager import SimpleBotManager
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager

# Create managers
bot_manager = SimpleBotManager()
storage_manager = LocalStorageManager()

# Create app with all features
app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=your_task_config,
    storage_manager=storage_manager
    # Authentication enabled by default
)
```

### 4. Run Server

```bash
uvicorn your_module:app --reload
# Server starts at http://localhost:8000
```

### 5. Use the API

```bash
# With authentication
curl http://localhost:8000/api/storage/browse/output \
  -H 'X-API-Key: your-key-here'

# Check capabilities
curl http://localhost:8000/api/auth/capabilities \
  -H 'X-API-Key: your-key-here'

# Browse documentation
open http://localhost:8000/docs
```

---

## 🏗️ Architecture

### Clean Architecture Principles

```
src/nikhil/pravaha/domain/
├── api/                    # API layer
│   ├── factory/            # FastAPI app creation
│   └── streaming/          # SSE streaming utilities
├── auth/                   # Authentication system
│   ├── model/              # AccessKey, PravahaModule
│   ├── protocol/           # Repository contracts
│   ├── repository/         # JSON/custom implementations
│   ├── middleware/         # API key validation
│   └── provider/           # Auth API endpoints
├── bot/                    # Bot execution
│   ├── protocol/           # BotManager contracts
│   ├── manager/            # Bot implementations
│   └── provider/           # Bot API endpoints
├── storage/                # Storage management
│   ├── manager/            # Storage configuration
│   ├── provider/           # Storage API
│   ├── logic/              # Path & version resolution
│   ├── protocol/           # Repository contracts
│   └── repository/         # Storage config repositories
├── workflow/               # Workflow orchestration
│   ├── entity/             # Workflow, WorkflowNode
│   ├── service/            # Orchestration engine
│   ├── infrastructure/     # Repositories
│   └── provider/           # Workflow API
├── llm/                    # LLM configuration
│   ├── protocol/           # Config repository contracts
│   └── repository/         # LLM config repositories
├── config/                 # Centralized configuration
│   └── cache_config.py     # CachePathConfig
└── logging/                # Nibandha integration
    └── manager/            # Logging setup
```

### Protocol-Based Design

All major components use Python Protocols for flexibility:

```python
# Example: Custom PostgreSQL backend
from pravaha.domain.auth.protocol import AccessKeyRepositoryProtocol

class PostgreSQLAccessKeyRepository(AccessKeyRepositoryProtocol):
    def validate_key(self, key: str) -> bool:
        # Your PostgreSQL implementation
        ...

# Use in app
app = create_fastapi_app(
    ...,
    access_key_repository=PostgreSQLAccessKeyRepository(conn_string)
)
```

---

## 🔐 Authentication System

### Module-Based Permissions

Control access to specific features:

```python
from pravaha.domain.auth.repository import JsonAccessKeyRepository
from pravaha.domain.auth.model.module import PravahaModule

repo = JsonAccessKeyRepository()

# Create key with specific permissions
frontend_key = repo.create_key(
    name="React App",
    permissions=[PravahaModule.STORAGE, PravahaModule.WORKFLOW]
)

# Admin key with all permissions
admin_key = repo.create_key(
    name="Admin",
    permissions=PravahaModule.all_modules()  # All 4 modules
)
```

### Available Modules

| Module | Description | Example Endpoints |
|--------|-------------|-------------------|
| `bot` | Bot execution & task management | `/api/bot/run/utility`, `/api/bot/run/crew` |
| `llm` | LLM configuration | `/api/llm/config` |
| `storage` | Artifact storage & retrieval | `/api/storage/browse/*`, `/api/storage/read/*` |
| `workflow` | Workflow orchestration | `/api/workflow/list`, `/api/workflow/run` |

### Feature Discovery

Frontend apps can discover available features:

```javascript
// Get current key's capabilities
const response = await fetch('/api/auth/capabilities', {
  headers: { 'X-API-Key': apiKey }
});

const { available_modules, endpoints } = await response.json();

// Show/hide UI features based on permissions
if (available_modules.includes('storage')) {
  showStorageFeature();
}
```

**📖 Full Guide:** [Authentication Documentation](docs/client/authentication-module.md)

---

## 📦 Storage Management

### Organized Categories

```
project/
├── output/              # Production artifacts
│   └── Model_v1/        # Versioned by model
├── intermediate/        # Processing artifacts  
│   └── 20260116_143022/ # Timestamped
└── knowledge/           # Static resources
    └── docs/            # Nested structure
```

### Storage API

```bash
# Browse files
GET /api/storage/browse/output

# Read file content
GET /api/storage/read/knowledge?path=docs/guide.md

# Update configuration
POST /api/storage/config
```

**📖 Full Guide:** [Storage Module Documentation](docs/client/storage-module.md)

---

## 🔄 Workflow Engine

### Visual Workflow Definition

```python
workflow = {
    "name": "Content Pipeline",
    "nodes": [
        {
            "id": "llm-1",
            "task_type": "LLM",
            "task_name": "gpt-4-creative"
        },
        {
            "id": "app-1",
            "task_type": "APP",
            "task_name": "generate_content",
            "inputs": {...}
        }
    ],
    "edges": [
        {"source": "llm-1", "target": "app-1"}  # LLM config → App
    ]
}
```

### Execute Workflows

```bash
# Create workflow
POST /api/workflow/create

# List all workflows
GET /api/workflow/list

# Execute workflow
POST /api/workflow/run?workflow_id=xxx
```

**📖 Full Guide:** [Workflow Module Documentation](docs/client/workflow-module.md)

---

## ⚙️ Configuration & Extensibility

### Centralized Cache Configuration

```python
from pravaha.domain.config.cache_config import CachePathConfig

# Custom cache location
cache_config = CachePathConfig.from_custom_root("/var/lib/pravaha")

app = create_fastapi_app(
    ...,
    cache_config=cache_config
)
# All components use /var/lib/pravaha/* for storage
```

### Repository Pattern

Implement custom backends for any component:

```python
# Example: MongoDB AccessKey Repository
from pravaha.domain.auth.protocol import AccessKeyRepositoryProtocol

class MongoDBAccessKeyRepository(AccessKeyRepositoryProtocol):
    def __init__(self, mongo_uri: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client.pravaha
        self.collection = self.db.access_keys
    
    def validate_key(self, key: str) -> bool:
        # MongoDB implementation
        ...
```

**📖 Full Guide:** [Repository & Configuration](docs/modules/repository-config.md)

---

## 📊 Logging with Nibandha

### Production-Ready Logging

```python
from pravaha.domain.logging.utils.rotation_utils import LogRotationUtils

# Setup log rotation
LogRotationUtils.setup_rotation(
    max_size_mb=50,              # Rotate at 50MB
    rotation_interval_hours=24,   # Or daily
    archive_retention_days=30     # Keep 30 days
)

# Logging auto-initializes
app = create_fastapi_app(...)
```

### Log Organization

```
.Nibandha/Pravaha/logs/
├── data/
│   ├── 2026-01-16_10-00-00.log  # Current log
│   └── 2026-01-15_10-00-00.log  # Previous
└── archives/
    └── 2026-01-14_10-00-00.log.gz  # Compressed
```

**📖 Full Guide:** [Nibandha Integration](docs/modules/nibandha-integration.md)

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/nikhil/pravaha --cov-report=html

# Specific module
pytest tests/unit/domain/auth/ -v

# Authentication tests (26 tests)
pytest tests/unit/domain/auth/
```

### Test Coverage

- ✅ Authentication: 26 tests (100% passing)
- ✅ Storage: Comprehensive coverage
- ✅ Workflow: Entity and service tests
- ✅ Config: Cache config integration tests

---

## 🎯 Use Cases

### 1. **LLM Chat Applications**
- Real-time streaming responses
- Conversation state management
- Multi-model support

### 2. **Agent Orchestration**
- CrewAI integration
- Multi-step workflows
- Tool chaining

### 3. **Content Generation Pipelines**
- Workflow-based pipelines
- Version management
- Artifact tracking

### 4. **Enterprise Multi-Tenant SaaS**
- Per-tenant API keys
- Module-based feature access
- Custom storage backends

### 5. **CI/CD Integration**
- Programmatic key creation
- Workflow automation
- Artifact deployment

---

## 📦 Dependencies

### Core Dependencies
- **FastAPI** (0.121.3) - Web framework
- **sse-starlette** (3.0.3) - Server-Sent Events
- **PyYAML** (6.0.2) - Configuration parsing
- **Nibandha** - Logging & storage

### Optional
- **PostgreSQL/MongoDB drivers** - For custom repositories
- **Redis** - For distributed caching

See [pyproject.toml](pyproject.toml) for complete list.

---

## 🔄 Migration from 1.x to 2.0

### Breaking Changes

**Authentication (New):**
- API keys now required by default
- Call `/api/auth/features` to discover capabilities
- Include `X-API-Key` header in all requests

**Disable for backward compatibility:**
```python
from pravaha.domain.auth.config import AuthConfig

app = create_fastapi_app(
    ...,
    auth_config=AuthConfig.disabled()  # Disable auth
)
```

**Repository Pattern:**
- Managers now accept `config_repository` parameter
- Defaults to JSON, fully backward compatible

---

## 🤝 Contributing

We welcome contributions! Please:

1. Follow [Architecture.md](docs/Architecture.md) coding standards
2. Use protocol-based design for new features
3. Add comprehensive tests (aim for >80% coverage)
4. Update documentation in `docs/modules/` and `docs/client/`
5. Submit PRs with clear descriptions

---

## 📝 License

[Specify your license here]

---

## 📞 Support

- **Documentation:** [docs/client/README.md](docs/client/README.md)
- **Technical Docs:** [docs/modules/](docs/modules/)
- **Issues:** [GitHub Issues](your-issues-url)

---

## 🎉 What's New in 2.0

### Authentication System
- ✅ API key-based authentication with module permissions
- ✅ Feature discovery API (`/api/auth/capabilities`)
- ✅ Pluggable storage backends (PostgreSQL/MongoDB support)

### Repository Pattern
- ✅ Protocol-based configuration repositories
- ✅ JSON default implementations
- ✅ Unified `CachePathConfig` for all modules

### Manager Refactoring
- ✅ `LocalStorageManager` uses repository pattern
- ✅ `LocalWorkflowManager` uses repository pattern
- ✅ `LLMConfigManager` uses repository pattern

### Enhanced Documentation
- ✅ Complete module documentation (8 guides)
- ✅ Client documentation with SDK examples
- ✅ Sangama & Akashavani integration guides

### Testing
- ✅ 26 authentication tests (100% passing)
- ✅ Integration test suites
- ✅ Comprehensive coverage reports

---

**Built with ❤️ using FastAPI and Python Protocols**
