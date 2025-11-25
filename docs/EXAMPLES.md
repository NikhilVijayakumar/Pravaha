# Pravaha Usage Examples

This document provides comprehensive examples of how to use Pravaha to create FastAPI applications for bot/agent systems with streaming support.

---

## Table of Contents

1. [Basic Example](#basic-example)
2. [Full Working Example](#full-working-example)
3. [Integration with CrewAI](#integration-with-crewai)
4. [Integration with LangChain](#integration-with-langchain)
5. [Custom Streaming Implementation](#custom-streaming-implementation)
6. [Error Handling](#error-handling)
7. [Testing Your API](#testing-your-api)

---

## Basic Example

### Step 1: Define Enums

```python
# config.py
from enum import Enum

class UtilsType(Enum):
    """Utility task types - synchronous operations"""
    VALIDATE = "validate"
    PARSE = "parse"
    TRANSFORM = "transform"

class ApplicationType(Enum):
    """Application task types - streaming operations"""
    CHAT = "chat"
    SUMMARIZE = "summarize"
    GENERATE = "generate"

class ExecutionTarget(Enum):
    """Execution targets"""
    LOCAL = "local"
    CLOUD = "cloud"
```

### Step 2: Implement Bot Manager

```python
# bot_manager.py
from typing import Any, Iterator
from config import UtilsType, ApplicationType

class SimpleBotManager:
    """Simple bot manager implementation"""
    
    def run(self, utility_task: UtilsType) -> Any:
        """Handle synchronous utility tasks"""
        if utility_task == UtilsType.VALIDATE:
            return {"status": "valid", "message": "Input validated successfully"}
        elif utility_task == UtilsType.PARSE:
            return {"parsed_data": {"key": "value"}}
        elif utility_task == UtilsType.TRANSFORM:
            return {"transformed": True}
        return {"error": "Unknown task"}
    
    def stream_run(self, application_task: ApplicationType) -> Iterator[str]:
        """Handle streaming tasks"""
        if application_task == ApplicationType.CHAT:
            # Simulate streaming chat response
            response = "Hello! How can I assist you today?"
            for word in response.split():
                yield word + " "
        elif application_task == ApplicationType.SUMMARIZE:
            yield "Summary: "
            yield "This is a concise summary "
            yield "of the input text."
```

### Step 3: Create Task Config

```python
# task_config.py
from config import UtilsType, ApplicationType, ExecutionTarget

class TaskConfig:
    """Task configuration"""
    UtilsType = UtilsType
    ApplicationType = ApplicationType
    ExecutionTarget = ExecutionTarget
```

### Step 4: Create and Run API

```python
# main.py
from nikhil.pravaha.domain.api.factory.api_factory import create_fastapi_app
from bot_manager import SimpleBotManager
from task_config import TaskConfig
import uvicorn

# Create instances
bot_manager = SimpleBotManager()
task_config = TaskConfig()

# Create FastAPI app
app = create_fastapi_app(bot_manager, task_config, prefix="api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 5: Test the API

```bash
# Run the server
python main.py

# In another terminal, test endpoints:

# Utility endpoint (synchronous)
curl -X POST http://localhost:8000/api/run/utility \\
  -H "Content-Type: application/json" \\
  -d '{"task_name": "validate"}'

# Streaming endpoint (SSE)
curl -N http://localhost:8000/api/run/application/stream \\
  -H "Content-Type: application/json" \\
  -d '{"task_name": "chat"}'

# Get enums
curl http://localhost:8000/api/enums/util-types
curl http://localhost:8000/api/enums/application-types
```

---

## Full Working Example

Here's a complete, production-ready example with a more sophisticated bot manager:

```python
# full_example/config.py
from enum import Enum

class UtilsType(Enum):
    HEALTH_CHECK = "health_check"
    VALIDATE_INPUT = "validate_input"
    GET_STATS = "get_stats"

class ApplicationType(Enum):
    CHAT = "chat"
    CODE_GENERATION = "code_generation"
    DOCUMENT_ANALYSIS = "document_analysis"

class ExecutionTarget(Enum):
    LOCAL = "local"
    REMOTE = "remote"
```

```python
# full_example/bot_manager.py
import time
from typing import Any, Iterator, Dict
from config import UtilsType, ApplicationType

class ProductionBotManager:
    def __init__(self):
        self.stats = {
            "requests_processed": 0,
            "streams_completed": 0
        }
    
    def run(self, utility_task: UtilsType) -> Any:
        """Execute utility tasks"""
        self.stats["requests_processed"] += 1
        
        if utility_task == UtilsType.HEALTH_CHECK:
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "service": "ProductionBot"
            }
        
        elif utility_task == UtilsType.VALIDATE_INPUT:
            return {
                "valid": True,
                "schema_version": "1.0",
                "validated_at": time.time()
            }
        
        elif utility_task == UtilsType.GET_STATS:
            return self.stats
        
        return {"error": f"Unknown task: {utility_task}"}
    
    def stream_run(self, application_task: ApplicationType) -> Iterator[str]:
        """Execute streaming tasks"""
        
        if application_task == ApplicationType.CHAT:
            # Simulate LLM streaming response
            response = [
                "I understand you'd like to chat.",
                " I'm here to help with any questions",
                " or tasks you may have.",
                " How can I assist you today?"
            ]
            for chunk in response:
                time.sleep(0.1)  # Simulate processing delay
                yield chunk
            
            self.stats["streams_completed"] += 1
        
        elif application_task == ApplicationType.CODE_GENERATION:
            # Simulate code generation
            code_chunks = [
                "def hello_world():\\n",
                "    print('Hello, World!')\\n",
                "    return True\\n"
            ]
            for chunk in code_chunks:
                time.sleep(0.05)
                yield chunk
            
            self.stats["streams_completed"] += 1
        
        elif application_task == ApplicationType.DOCUMENT_ANALYSIS:
            # Simulate document analysis
            analysis_steps = [
                "[1/4] Loading document...\\n",
                "[2/4] Extracting text...\\n",
                "[3/4] Analyzing content...\\n",
                "[4/4] Complete! Summary: Document contains 1000 words."
            ]
            for step in analysis_steps:
                time.sleep(0.2)
                yield step
            
            self.stats["streams_completed"] += 1
```

```python
# full_example/task_config.py
from config import UtilsType, ApplicationType, ExecutionTarget

class TaskConfig:
    UtilsType = UtilsType
    ApplicationType = ApplicationType
    ExecutionTarget = ExecutionTarget
```

```python
# full_example/main.py
from nikhil.pravaha.domain.api.factory.api_factory import create_fastapi_app
from bot_manager import ProductionBotManager
from task_config import TaskConfig
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create bot manager and config
bot_manager = ProductionBotManager()
task_config = TaskConfig()

# Create FastAPI app
app = create_fastapi_app(bot_manager, task_config, prefix="api/v1")

# Add startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Pravaha API server starting...")
    logger.info(f"📍 API available at: http://localhost:8000/api/v1")
    logger.info(f"📊 Health check: http://localhost:8000/health")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True  # Enable auto-reload during development
    )
```

---

## Integration with CrewAI

Example of integrating Pravaha with CrewAI:

```python
# crewai_example/bot_manager.py
from crewai import Agent, Task, Crew
from typing import Iterator
from config import UtilsType, ApplicationType

class CrewAIBotManager:
    def __init__(self):
        # Initialize CrewAI agents
        self.researcher = Agent(
            role='Researcher',
            goal='Research and gather information',
            backstory='Expert researcher with attention to detail',
            verbose=True
        )
        
        self.writer = Agent(
            role='Writer',
            goal='Write engaging content',
            backstory='Creative writer with excellent communication skills',
            verbose=True
        )
    
    def run(self, utility_task: UtilsType):
        """Execute utility tasks"""
        if utility_task == UtilsType.HEALTH_CHECK:
            return {
                "status": "healthy",
                "agents": ["researcher", "writer"]
            }
        return {"result": "processed"}
    
    def stream_run(self, application_task: ApplicationType) -> Iterator[str]:
        """Execute CrewAI tasks with streaming"""
        
        if application_task == ApplicationType.CHAT:
            # Create task
            task = Task(
                description="Answer user's question",
                agent=self.researcher
            )
            
            # Create crew
            crew = Crew(
                agents=[self.researcher],
                tasks=[task],
                verbose=True
            )
            
            # Execute and stream results
            # Note: This is a simplified example
            # Real implementation would need CrewAI streaming support
            result = crew.kickoff()
            
            # Stream the result in chunks
            for chunk in str(result).split(". "):
                yield chunk + ". "
        
        elif application_task == ApplicationType.DOCUMENT_ANALYSIS:
            # Create research and writing tasks
            research_task = Task(
                description="Analyze the document",
                agent=self.researcher
            )
            
            writing_task = Task(
                description="Summarize findings",
                agent=self.writer
            )
            
            crew = Crew(
                agents=[self.researcher, self.writer],
                tasks=[research_task, writing_task],
                verbose=True
            )
            
            yield "[Agent: Researcher] Starting analysis...\\n"
            result = crew.kickoff()
            yield f"[Agent: Writer] Summary: {result}"
```

---

## Integration with LangChain

Example of integrating Pravaha with LangChain:

```python
# langchain_example/bot_manager.py
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Iterator
from config import UtilsType, ApplicationType
import os

class LangChainBotManager:
    def __init__(self):
        # Initialize LangChain LLM
        self.llm = OpenAI(
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create prompt template
        self.chat_prompt = PromptTemplate(
            input_variables=["query"],
            template="You are a helpful assistant. {query}"
        )
        
        self.chat_chain = LLMChain(llm=self.llm, prompt=self.chat_prompt)
    
    def run(self, utility_task: UtilsType):
        """Execute utility tasks"""
        if utility_task == UtilsType.VALIDATE_INPUT:
            return {"status": "valid", "llm": "OpenAI"}
        return {}
    
    def stream_run(self, application_task: ApplicationType) -> Iterator[str]:
        """Execute LangChain tasks with streaming"""
        
        if application_task == ApplicationType.CHAT:
            # Note: For real streaming, use LangChain's streaming callbacks
            # This is a simplified example
            query = "Hello, how are you?"
            response = self.chat_chain.run(query)
            
            # Stream response word by word
            for word in response.split():
                yield word + " "
        
        elif application_task == ApplicationType.SUMMARIZE:
            # Summarization chain
            summary_prompt = PromptTemplate(
                input_variables=["text"],
                template="Summarize the following text: {text}"
            )
            summary_chain = LLMChain(llm=self.llm, prompt=summary_prompt)
            
            text = "Long text to summarize..."
            summary = summary_chain.run(text)
            
            yield "Summary: "
            for sentence in summary.split(". "):
                yield sentence + ". "
```

---

## Custom Streaming Implementation

### Async Streaming

If your bot logic is async, you can return async generators:

```python
# async_bot_manager.py
import asyncio
from typing import AsyncIterator
from config import ApplicationType

class AsyncBotManager:
    async def run(self, utility_task):
        # Async utility execution
        await asyncio.sleep(0.1)
        return {"status": "success"}
    
    async def stream_run(self, application_task: ApplicationType) -> AsyncIterator[str]:
        """Async streaming"""
        if application_task == ApplicationType.CHAT:
            words = ["Hello", "from", "async", "stream"]
            for word in words:
                await asyncio.sleep(0.1)  # Simulate async work
                yield word + " "
```

Pravaha automatically detects and handles async generators!

### Custom SSE Format

```python
# custom_sse_bot.py
from typing import Iterator
import json

class CustomSSEBot:
    def stream_run(self, application_task) -> Iterator[str]:
        """Stream with custom data format"""
        # Yield JSON objects
        yield json.dumps({"type": "start", "timestamp": 1234567890})
        yield json.dumps({"type": "chunk", "data": "Hello"})
        yield json.dumps({"type": "chunk", "data": "World"})
        yield json.dumps({"type": "end", "timestamp": 1234567900})
```

---

## Error Handling

### Exception Handling in Bot Manager

```python
# error_handling_bot.py
class ErrorHandlingBot:
    def run(self, utility_task: UtilsType):
        """Utility with error handling"""
        if utility_task == UtilsType.VALIDATE:
            # Raise custom exception - Pravaha will catch and return HTTP 500
            raise ValueError("Invalid input format")
        return {"status": "ok"}
    
    def stream_run(self, application_task: ApplicationType) -> Iterator[str]:
        """Streaming with error handling"""
        try:
            yield "Starting process...\\n"
            
            # Simulate an error condition
            if application_task == ApplicationType.CHAT:
                yield "Processing...\\n"
                # Work happens here
                yield "Complete!"
        
        except Exception as e:
            # Yield error in stream
            yield f"\\nError: {str(e)}"
```

### Client-Side Error Handling

```python
# client_example.py
import requests

# Utility endpoint
try:
    response = requests.post(
        "http://localhost:8000/api/run/utility",
        json={"task_name": "validate"}
    )
    response.raise_for_status()
    print(response.json())
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.json()}")

# Streaming endpoint
try:
    response = requests.post(
        "http://localhost:8000/api/run/application/stream",
        json={"task_name": "chat"},
        stream=True
    )
    response.raise_for_status()
    
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith('data: '):
                data = decoded[6:]  # Remove 'data: ' prefix
                print(data)
                
except requests.exceptions.HTTPError as e:
    print(f"Streaming Error: {e}")
```

---

## Testing Your API

### Unit Testing

```python
# test_bot_manager.py
import pytest
from bot_manager import SimpleBotManager
from config import UtilsType, ApplicationType

def test_utility_run():
    bot = SimpleBotManager()
    result = bot.run(UtilsType.VALIDATE)
    assert result["status"] == "valid"

def test_stream_run():
    bot = SimpleBotManager()
    stream = bot.stream_run(ApplicationType.CHAT)
    chunks = list(stream)
    assert len(chunks) > 0
    assert isinstance(chunks[0], str)
```

### Integration Testing

```python
# test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_utility_endpoint():
    response = client.post(
        "/api/run/utility",
        json={"task_name": "validate"}
    )
    assert response.status_code == 200
    assert "result" in response.json()

def test_streaming_endpoint():
    response = client.post(
        "/api/run/application/stream",
        json={"task_name": "chat"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

def test_enum_endpoint():
    response = client.get("/api/enums/util-types")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

---

## Summary

Pravaha makes it easy to:

1. ✅ Define task types with Enums
2. ✅ Implement bot logic with protocols (no inheritance)
3. ✅ Create FastAPI apps with one function call
4. ✅ Support both sync and async streaming
5. ✅ Integrate with any bot framework (CrewAI, LangChain, custom)
6. ✅ Handle errors gracefully
7. ✅ Test with standard testing tools

For more examples, see the [GitHub repository](#) or [documentation](README.md).
