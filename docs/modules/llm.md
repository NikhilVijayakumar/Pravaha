# LLM Module - Technical Documentation

> **Audience:** Pravaha contributors and maintainers  
> **Client Documentation:** [docs/client/llm-module.md](../client/llm-module.md)

## Module Objective

The LLM module provides **centralized LLM configuration management** for AI applications, supporting:
1. Multiple LLM providers (OpenAI, Anthropic, local models)
2. Mode-based configuration (creative vs evaluation)
3. Runtime configuration override
4. Environment variable expansion for security

## Architecture

```
┌─────────────────────┐
│  LLMAPIProvider     │  (Presentation - FastAPI)
└──────────┬──────────┘
           │ depends on
           ↓
┌─────────────────────┐
│ LLMConfigManager    │  (Domain - Config Management)
└──────────┬──────────┘
           │ loads from
           ↓
       llm_config.yaml
```

### Components

#### 1. Manager (`src/nikhil/pravaha/domain/storage/manager/llm_config_manager.py`)

**LLMConfigManager**

**Responsibilities:**
1. Load YAML config file
2. Parse LLM configurations
3. Provide lookup by mode
4. Expand environment variables

```python
class LLMConfigManager:
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            # Default: .Pravaha/config/llm_config.json
            config_path = Path.cwd() / ".Pravaha" / "config" / "llm_config.json"
        
        self.config_path = config_path
        self.configs = self._load_configs()
    
    def _load_configs(self) -> List[Dict]:
        """Load and parse YAML configs."""
        if not self.config_path.exists():
            return []
        
        with open(self.config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Expand environment variables
        return self._expand_env_vars(data)
    
    def get_config_by_mode(self, mode: str) -> Optional[Dict]:
        """Get LLM config by ui_mode (creative/evaluation)."""
        for config in self.configs:
            if config.get("ui_mode") == mode:
                return config
        return None
    
    def get_all_configs(self) -> List[Dict]:
        """Get all registered LLM configs."""
        return self.configs
```

#### 2. API Provider (`src/nikhil/pravaha/domain/llm/provider/llm_api_provider.py`)

**LLMAPIProvider**

**Responsibilities:**
1. Expose LLM configs via HTTP
2. Create FastAPI routes
3. Handle queries by mode

```python
class LLMAPIProvider:
    def __init__(self, llm_config_manager: LLMConfigManagerProtocol):
        self.llm_config_manager = llm_config_manager
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        self.router.get("/configs")(self.get_all_configs)
        self.router.get("/config/{mode}")(self.get_config_by_mode)
    
    async def get_all_configs(self):
        """GET /api/llm/configs"""
        return self.llm_config_manager.get_all_configs()
    
    async def get_config_by_mode(self, mode: str):
        """GET /api/llm/config/{mode}"""
        config = self.llm_config_manager.get_config_by_mode(mode)
        if not config:
            raise HTTPException(status_code=404, detail=f"Config for mode {mode} not found")
        return config
```

## Configuration Structure

### YAML Format

```yaml
# llm_config.yaml
creative_llm:
  ui_mode: "creative"           # Mode identifier
  ui_model_id: "gpt-4"         # Display name
  model_config:
    base_url: "https://api.openai.com/v1"
    model: "gpt-4-turbo-preview"
    api_key: "${OPENAI_API_KEY}"  # Env var expansion
  llm_parameters:
    temperature: 0.8
    top_p: 0.95
    max_completion_tokens: 4096

evaluation_llm:
  ui_mode: "evaluation"
  ui_model_id: "claude-3"
  model_config:
    base_url: "https://api.anthropic.com/v1"
    model: "claude-3-opus-20240229"
    api_key: "${ANTHROPIC_API_KEY}"
  llm_parameters:
    temperature: 0.1
    max_completion_tokens: 2048

local_llm:
  ui_mode: "creative"
  ui_model_id: "gemma-3-12b"
  model_config:
    base_url: "http://localhost:1234/v1"
    model: "lm_studio/gemma-3-12b-it"
    api_key: "lm_studio"
  llm_parameters:
    temperature: 0.7
```

### Fields Explained

| Field | Purpose | Required |
|-------|---------|----------|
| `ui_mode` | Category (creative/evaluation) | Yes |
| `ui_model_id` | Display name for UI | Yes |
| `model_config.base_url` | API endpoint | Yes |
| `model_config.model` | Model identifier | Yes |
| `model_config.api_key` | Authentication | Yes |
| `llm_parameters.temperature` | Creativity (0-1) | No |
| `llm_parameters.top_p` | Nucleus sampling | No |
| `llm_parameters.max_completion_tokens` | Max output length | No |

## Data Flow

### Get All Configs

```
GET /api/llm/configs
    ↓
LLMAPIProvider.get_all_configs()
    ↓
llm_config_manager.get_all_configs()
    ↓
Returns List[Dict] of all configs
    ↓
HTTP Response (JSON array)
```

### Get Config by Mode

```
GET /api/llm/config/creative
    ↓
LLMAPIProvider.get_config_by_mode("creative")
    ↓
llm_config_manager.get_config_by_mode("creative")
    ↓
Search configs for ui_mode == "creative"
    ↓
Return first match (or 404)
    ↓
HTTP Response (JSON object)
```

### Runtime Override Flow

```
User Request with llm_config_override
    ↓
Bot Manager receives override
    ↓
If override present: Use override
Else: Use default from LLM config
    ↓
Pass to LLM library (OpenAI, Anthropic, etc.)
```

## Environment Variable Expansion

### Implementation

```python
def _expand_env_vars(self, config: Dict) -> Dict:
    """
    Recursively expand ${VAR} patterns.
    
    Example:
        "${OPENAI_API_KEY}" → os.getenv("OPENAI_API_KEY")
    """
    if isinstance(config, dict):
        return {k: self._expand_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [self._expand_env_vars(item) for item in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        var_name = config[2:-1]  # Remove ${ and }
        return os.getenv(var_name, config)  # Fallback to original if not set
    else:
        return config
```

### Security Benefits

1. **No Hardcoded Keys** - API keys not in version control
2. **Environment-Specific** - Different keys per environment (dev/staging/prod)
3. **Secret Management** - Integrate with secret managers

## Design Patterns

### 1. Singleton-like Configuration
LLMConfigManager loaded once, reused across requests.

### 2. Strategy Pattern
Different LLM providers (OpenAI, Anthropic, local) use same config structure.

### 3. Protocol-Based
`LLMConfigManagerProtocol` allows alternative implementations.

## Key Design Decisions

### Why YAML Instead of JSON?

**Chose:** YAML  
**Instead of:** JSON

**Reasons:**
1. **Comments** - Can document configs inline
2. **Readability** - More human-friendly
3. **Multiline Strings** - Easier for prompts
4. **Less Verbose** - No quotes everywhere

### Why Mode-Based Config?

**Modes:** creative (high temperature) vs evaluation (low temperature)

**Reasons:**
1. **Use Case Clarity** - Different tasks need different configs
2. **Quick Switching** - UI can toggle between modes
3. **Consistency** - Same mode = same behavior

### Why Separate from Bot Manager?

**Reasons:**
1. **Separation of Concerns** - Config ≠ Execution
2. **Reusability** - Multiple bot managers can share configs
3. **Centralization** - Single source of truth

## Integration with Other Modules

### With Bot Manager
Bot manager reads LLM config via `llm_config_manager` or receives override in `stream_run()`.

### With Storage Provider
Storage providers use LLM config to organize outputs by model (`ui_model_id`).

### With Workflow
Workflow LLM nodes reference configs by mode.

## Testing

### Unit Tests

```python
def test_load_configs():
    manager = LLMConfigManager(Path("test_config.yaml"))
    configs = manager.get_all_configs()
    assert len(configs) > 0

def test_get_config_by_mode():
    config = manager.get_config_by_mode("creative")
    assert config["ui_mode"] == "creative"

def test_env_var_expansion():
    os.environ["TEST_KEY"] = "secret"
    config = manager._expand_env_vars({"api_key": "${TEST_KEY}"})
    assert config["api_key"] == "secret"
```

### Integration Tests

```python
def test_llm_api_get_configs(client):
    response = client.get("/api/llm/configs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## Future Enhancements

- [ ] Config validation (Pydantic schemas)
- [ ] Dynamic config reloading without restart
- [ ] Config versioning/migration
- [ ] Provider-specific parameter validation
- [ ] Cost tracking per config
