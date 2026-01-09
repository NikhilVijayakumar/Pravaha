# Workflow Module - Client Documentation

> **💡 Quick Start:** Use **[API Factory](api-factory.md)** to auto-configure workflows! This guide shows workflow design details.

The Workflow module enables building and executing complex multi-step workflows with visual design support.

## Overview

Features:
- **Visual Workflow Design**: Node-based workflow editor
- **Multiple Node Types**: Application, Utility, LLM, Environment
- **Execution Management**: Track workflow runs and status
- **Restartability**: Resume from failed nodes
- **Persistence**: JSON-based workflow storage

## Workflow Structure

### Workflow Definition

```json
{
  "id": "workflow-uuid",
  "name": "My Workflow",
  "nodes": [
    {
      "id": "node-1",
      "task_type": "APP",
      "task_name": "generate_content",
      "inputs": {
        "topic": {
          "key_name": "topic",
          "source": "direct",
          "value": "AI"
        }
      },
      "position": {"x": 100, "y": 100}
    },
    {
      "id": "node-2",
      "task_type": "LLM",
      "task_name": "llm_config",
      "llm_config": {
        "ui_mode": "creative",
        "ui_model_id": "gpt-4",
        "model_config": {
          "model": "gpt-4",
          "api_key": "sk-..."
        },
        "llm_parameters": {
          "temperature": 0.7
        }
      },
      "position": {"x": 300, "y": 100}
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-2",
      "target": "node-1"
    }
  ]
}
```

### Node Types

1. **APP**: Application tasks (streaming LLM apps)
2. **UTIL**: Utility tasks (calculators, validators)
3. **LLM**: LLM configuration nodes
4. **ENVIRONMENT**: Environment variable nodes

## API Endpoints

### POST `/api/workflow/create`
Create a new workflow.

**Request:**
```json
{
  "name": "My Workflow", 
  "nodes": [...],
  "edges": [...]
}
```

**Response:**
```json
{
  "id": "generated-uuid",
  "name": "My Workflow",
  "nodes": [...],
  "edges": [...],
  "created_at": "2026-01-09T...",
  "updated_at": "2026-01-09T..."
}
```

### GET `/api/workflow/list`
List all workflows.

**Response:**
```json
[
  {
    "id": "workflow-1",
    "name": "Workflow 1",
    "created_at": "...",
    "updated_at": "..."
  }
]
```

### GET `/api/workflow/{workflow_id}`
Get workflow by ID.

### POST `/api/workflow/update`
Update existing workflow.

**Request:**
```json
{
  "id": "workflow-uuid",
  "name": "Updated Name",
  "nodes": [...],
  "edges": [...]
}
```

### POST `/api/workflow/rename`
Rename a workflow.

**Request:**
```json
{
  "id": "workflow-uuid",
  "new_name": "New Workflow Name"
}
```

**Response:** Updated workflow object

### DELETE `/api/workflow/{workflow_id}`
Delete a workflow.

### POST `/api/workflow/run?workflow_id={id}`
Execute a workflow.

**Response:**
```json
{
  "id": "run-uuid",
  "workflow_id": "workflow-uuid",
  "status": "RUNNING",
  "started_at": "2026-01-09T..."
}
```

### GET `/api/workflow/run/{run_id}`
Get workflow run status.

**Response:**
```json
{
  "id": "run-uuid",
  "workflow_id": "workflow-uuid",
  "status": "COMPLETED",
  "started_at": "...",
  "completed_at": "...",
  "node_states": {
    "node-1": "COMPLETED",
    "node-2": "COMPLETED"
  }
}
```

### GET `/api/workflow/runs?workflow_id={id}`
List runs for a workflow.

**Response:**
```json
[
  {
    "id": "run-1",
    "workflow_id": "workflow-1",
    "status": "COMPLETED",
    "started_at": "...",
    "completed_at": "..."
  }
]
```

## Setup

### Register Workflow Provider

```python
from pravaha.domain.api.factory.api_factory import create_fastapi_app

app = create_fastapi_app(
    bot_manager=bot_manager,
    task_config=task_config,
    storage_manager=storage_manager,
    workflow_data_dir="./data"  # Workflow storage directory
)
```

## Workflow Execution

### How Workflows Run

1. **Topological Sort**: Nodes executed in dependency order
2. **LLM Config Injection**: LLM nodes configure connected APP nodes
3. **State Tracking**: Each node's status tracked (PENDING, RUNNING, COMPLETED, FAILED)
4. **Failure Handling**: Execution stops at first failure
5. **Restartability**: Resume from last successful node

### Example Flow

```
[LLM Config Node] ──→ [APP Node: Generate] ──→ [UTIL Node: Validate]
                ↓
[Environment Node]
```

**Execution:**
1. LLM Config runs first (no dependencies)
2. Environment runs (no dependencies)
3. APP Node runs with LLM config from step 1
4. UTIL Node runs with output from step 3

## Integration Example

```python
from pravaha.domain.workflow.service.workflow_service import WorkflowService
from pravaha.domain.workflow.infrastructure.json_workflow_repository import JsonWorkflowRepository
from pravaha.domain.workflow.infrastructure.json_run_repository import JsonRunRepository
from pravaha.domain.workflow.service.simple_workflow_engine import SimpleWorkflowEngine

# Setup repositories
workflow_repo = JsonWorkflowRepository("data/workflows.json")
run_repo = JsonRunRepository("data/runs.json")

# Setup engine with your task executor
from your_app import TaskExecutor
executor = TaskExecutor(bot_manager)
engine = SimpleWorkflowEngine(executor, run_repo)

# Create service
workflow_service = WorkflowService(workflow_repo, run_repo, engine)

# Create workflow via API or directly
from pravaha.domain.workflow.entity.workflow import Workflow, WorkflowNode, WorkflowEdge

workflow = Workflow(
    name="My Workflow",
    nodes=[...],
    edges=[...]
)

created = workflow_service.create_workflow(workflow)

# Execute
run = await workflow_service.trigger_run(created.id)
await workflow_service.execute_run(run.id)

# Check status
run_status = workflow_service.get_run(run.id)
print(run_status.status)  # COMPLETED, FAILED, RUNNING
```

## Input Sources

Workflow nodes support multiple input sources:

### Direct Input
```json
{
  "key_name": "topic",
  "source": "direct",
  "value": "Quantum Physics"
}
```

### File Input (JSON)
```json
{
  "key_name": "data",
  "source": "file",
  "path": "knowledge/input.json",
  "format": "json"
}
```

### File Input (Text)
```json
{
  "key_name": "prompt",
  "source": "file",
  "path": "knowledge/prompt.txt",
  "format": "text"
}
```

## Best Practices

1. **Name Workflows Clearly**: Use descriptive names
2. **Use LLM Nodes**: Centralize LLM config in dedicated nodes
3. **Environment Variables**: Use ENV nodes for API keys
4. **Test Incrementally**: Test each node before building complex workflows
5. **Handle Failures**: Implement error handling in task executors
6. **Version Workflows**: Save different versions as you iterate
7. **Monitor Runs**: Check run status and logs

## UI Integration

Pravaha provides a React-based workflow designer (not included in core library). To integrate:

1. Set up workflow API endpoints (automatic with `create_fastapi_app`)
2. Use the separate `sangama` UI package
3. Or build your own using the workflow API endpoints

## Example: Complete Workflow

```json
{
  "name": "Content Generation Pipeline",
  "nodes": [
    {
      "id": "llm-1",
      "task_type": "LLM",
      "task_name": "creative_llm",
      "llm_config": {
        "model_config": {"model": "gpt-4"},
        "llm_parameters": {"temperature": 0.8}
      }
    },
    {
      "id": "app-1",
      "task_type": "APP",
      "task_name": "generate_content",
      "inputs": {
        "topic": {"source": "direct", "value": "AI"}
      }
    },
    {
      "id": "util-1",
      "task_type": "UTIL",
      "task_name": "validate_output"
    }
  ],
  "edges": [
    {"source": "llm-1", "target": "app-1"},
    {"source": "app-1", "target": "util-1"}
  ]
}
```
