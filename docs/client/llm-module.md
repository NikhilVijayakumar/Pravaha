# LLM Module - Client Documentation

> **💡 Quick Start:** Use **[API Factory](api-factory.md)** to auto-configure LLM module! This guide shows configuration details.

The LLM module manages LLM configurations and provides centralized config management for your AI applications.

## Overview

Features:
- **Config Management**: Store and retrieve LLM configurations
- **Provider Agnostic**: Works with OpenAI, Anthropic, local models (LM Studio, Ollama)
- **Runtime Override**: Override configs at request time
- **API Access**: Get registered LLM configs via REST API

## Configuration Structure

### LLM Config Format

```yaml
# llm_config.yaml
creative_llm:
  ui_mode: "creative"
  ui_model_id: "gpt-4"
  model_config:
    base_url: "https://api.openai.com/v1"
    model: "gpt-4-turbo-preview"
    api_key: "${OPENAI_API_KEY}"  # Environment variable
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
    top_p: 0.9
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
    max_completion_tokens: 8192
```

## Integration

### Setup LLM Config Manager

```python
from pravaha.domain.storage.manager.llm_config_manager import LLMConfigManager

# Initialize with config file
llm_config_manager = LLMConfigManager(config_path="llm_config.yaml")

# Or use default location: .Pravaha/config/llm_config.json
llm_config_manager = LLMConfigManager()
```

### Using with create_fastapi_app

```python
from pravaha.domain.api.factory.api_factory import create_fastapi_app

app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager,
    llm_config_path="llm_config.yaml"  # Specify config path
)
```

## API Endpoints

### GET `/api/llm/configs`
Get all registered LLM configurations.

**Response:**
```json
[
  {
    "ui_mode": "creative",
    "ui_model_id": "gpt-4",
    "model_config": {
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4-turbo-preview",
      "api_key": "sk-..."
    },
    "llm_parameters": {
      "temperature": 0.8,
      "top_p": 0.95,
      "max_completion_tokens": 4096
    }
  }
]
```

### GET `/api/llm/config/{mode}`
Get LLM config by mode (creative/evaluation).

**Example:** `GET /api/llm/config/creative`

## Using LLM Config in Applications

### In Your Bot Manager

```python
class MyBotManager:
    def stream_run(self, application_task, inputs=None, llm_config=None):
        # llm_config can come from:
        # 1. Request (llm_config_override)
        # 2. Workflow node
        # 3. Default config
        
        model = llm_config["model_config"]["model"]
        temperature = llm_config["llm_parameters"]["temperature"]
        
        # Use with your LLM library
        response = call_llm(
            model=model,
            temperature=temperature,
            prompt=inputs[0]["message"]
        )
        
        for chunk in response:
            yield chunk
```

### Runtime Override

Clients can override LLM config at runtime:

```json
{
  "task_name": "chat_bot",
  "inputs": [{"message": "Hello"}],
  "llm_config_override": {
    "model_config": {
      "base_url": "http://localhost:1234/v1",
      "model": "lm_studio/gemma-3-12b-it",
      "api_key": "lm_studio"
    },
    "llm_parameters": {
      "temperature": 0.9,
      "max_completion_tokens": 2048
    }
  }
}
```

## Environment Variables

Use environment variables for API keys:

```yaml
model_config:
  api_key: "${OPENAI_API_KEY}"
```

## Best Practices

1. **Separate Configs**: Use different configs for creative vs evaluation tasks
2. **Environment Variables**: Never commit API keys, use env vars
3. **Local Testing**: Set up local LLM (LM Studio/Ollama) for development
4. **Override Support**: Always accept `llm_config` parameter in `stream_run()`
5. **Default Fallback**: Provide sensible defaults if no config specified
