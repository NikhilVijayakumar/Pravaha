# Helper Guide: Updating Pravaha for Dynamic LLM Configuration

This document outlines the changes required in the `Pravaha` library to support the dynamic LLM configuration flow implemented in `Akashavani`.

## 1. Update `BotManagerProtocol`

The `BotManagerProtocol` defines the contract for bot managers. It needs to be updated to accept the optional `llm_config` argument in `stream_run`.

**File**: `pravaha/domain/bot/protocol/bot_manager_protocol.py` (Hypothetical path based on imports)

```python
from typing import Optional, TypeVar, Any
# Ensure LLMConfigurationInput is available or use strict typing if Pravaha depends on the domain model
# If LLMConfigurationInput is specific to the application, use Any or a Dict, 
# but ideally Pravaha should define the contract or import it if shared.

class BotManagerProtocol(Generic[T, K]):
    # ... existing methods ...

    def stream_run(self, application_task: K, inputs=None, llm_config: Optional[Any] = None):
        """
        Executes a streaming run for the given application task.
        
        Args:
            application_task: The task/application identifier.
            inputs: Application inputs.
            llm_config: Optional dynamic LLM configuration (e.g., LLMConfigurationInput)
        """
        ...
```

## 2. API Layer (if applicable)

If `Pravaha` exposes a REST API via FastAPI or similar, the endpoint handler for `stream_run` (likely `/bot/stream_run` or similar) needs to be updated to accept `llm_config` in its request body.

**Example Request Body Update:**

```json
{
  "task": "generate_scientific_knowledge_application",
  "inputs": { ... },
  "llm_config": {
    "llm_model_config": {
      "model": "gpt-4-turbo",
      "api_key": "..."
    },
    "llm_parameters": {
      "temperature": 0.7
    }
  }
}
```

## 3. Propagation

Ensure that any internal orchestrators or services within `Pravaha` that call `BotManager.stream_run` are also updated to pass this argument if they are part of the chain.

## 4. `LLMConfigurationInput` Definition

If `LLMConfigurationInput` is intended to be a shared contract, consider moving its definition to `Pravaha` so both `Akashavani` and `Pravaha` can import it, or define an equivalent Pydantic model in `Pravaha` that `Akashavani`'s model matches.
