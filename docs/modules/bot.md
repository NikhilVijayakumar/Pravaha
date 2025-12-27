# Bot Module Documentation

The `bot` module is the core of Pravaha's execution engine. It defines the protocols for executing synchronous and asynchronous tasks and provides the API provider to expose these capabilities via FastAPI.

## Components

### 1. Protocols
Located in `src/nikhil/pravaha/domain/bot/protocol/`

#### `BotManagerProtocol`
The contract that your bot manager must implement.

```python
class BotManagerProtocol(Protocol[UT, AT]):
    def run(self, utility_task: UT, inputs: Optional[List[Dict[str, Any]]] = None) -> Any:
        # Execute synchronous utility task
        pass

    def stream_run(self, application_task: AT, inputs: Optional[List[Dict[str, Any]]] = None) -> Union[Iterable[str], AsyncIterable[str]]:
        # Execute streaming application task
        pass
```

- **`UT`**: Generic type for Utility Task Enum.
- **`AT`**: Generic type for Application Task Enum.

### 2. Models
Located in `src/nikhil/pravaha/domain/bot/model/`

#### `UtilityRequest`
Structure for utility task requests.
```json
{
  "task_name": "enum_value",
  "inputs": [{"key": "value"}]
}
```

#### `ApplicationRequest`
Structure for streaming application requests.
```json
{
  "task_name": "enum_value",
  "inputs": [{"key": "value"}]
}
```

### 3. API Provider
Located in `src/nikhil/pravaha/domain/bot/provider/bot_api_provider.py`

The `BotAPIProvider` class creates a FastAPI router with the following endpoints:

- **POST `/run/utility`**: Executes `bot_manager.run()`. Returns JSON.
- **POST `/run/application/stream`**: Executes `bot_manager.stream_run()`. Returns Server-Sent Events (SSE).
- **GET `/enums/*`**: Exposes available task types.

## Usage

```python
from pravaha.domain.bot.provider.bot_api_provider import BotAPIProvider

# Initialize
provider = BotAPIProvider(my_bot_manager, my_task_config)

# Mount Router
app.include_router(provider.router)
```
