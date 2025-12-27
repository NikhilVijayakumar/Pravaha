# Example Package Documentation

The `pravaha_example` package demonstrates a complete working implementation of the Pravaha architecture.

## Location
`src/nikhil/pravaha_example`

## Components

### 1. Domain Logic
- **`domain/math_bot.py`**: A `MathBot` class that implements `stream_run`. It simulates a chat interaction where it "thinks" and then responds.
- **`domain/calculator_tool.py`**: A `CalculatorTool` class that implements a simple `run` method for arithmetic.

### 2. Configuration
- **`config/settings.py`**: Defines standard Enums:
    - `ApplicationType.MATH_ASSISTANT`
    - `UtilsType.CALCULATOR`

### 3. Server
- **`service/server.py`**: A FastAPI application.
    - Instantiates `LocalStorageManager`.
    - Instantiates a `SimpleBotManager` (stub) that routes tasks to the MathBot or CalculatorTool.
    - Mounts both `BotAPIProvider` and `StorageAPIProvider`.

## Running the Example

1. Navigate to the project root.
2. Run the server:
   ```bash
   uvicorn pravaha_example.service.server:app --reload
   ```
3. The API is available at `http://127.0.0.1:8000`.

## Testing the Example
We have provided an integration test suite: `tests/test_example_server.py`.

Run it with:
```bash
pytest tests/test_example_server.py
```
