# Pravaha Workflow System - Backend Specification

## Overview
The backend follows **Domain-Driven Design (DDD)** and **Clean Architecture**. It relies on **Protocols** to define interfaces, minimizing dependency on frameworks like FastAPI (which serves only as the delivery mechanism). State is persisted via a JSON-based repository implementation.

## Architecture Layers

### 1. Domain Layer (Core)
*No external dependencies.*

**Entities (Models)**
- `Workflow`: Aggregate root containing `nodes` and `edges`.
- `WorkflowNode`: Represents a step (Task). Properties: `id`, `task_type` (APP/UTIL), `task_name`, `inputs` (List[`InputItem`]).
- `WorkflowRun`: Represents an execution instance.
- `RunState`: Status of a run/node (PENDING, RUNNING, COMPLETED, FAILED).

**Protocols (Interfaces)**
- `WorkflowRepositoryProtocol`: CRUD operations for `Workflow`.
- `RunRepositoryProtocol`: CRUD operations for `WorkflowRun` and State updates.
- `WorkflowEngineProtocol`: Logic to execute a graph (topological sort, dependency handling).
- `WorkflowManagerProtocol`: Facade for external consumers (API routers).

### 2. Infrastructure Layer (Implementation)
*Implements Protocols.*

**Repositories (JSON Persistence)**
- `JsonWorkflowRepository`: 
    - Reads/Writes `data/workflows.json` (relative to app cwd).
    - Serializes `Workflow` objects.
- `JsonRunRepository`: 
    - Reads/Writes `data/runs.json` (relative to app cwd).
    - Handles concurrency (simple lock or atomic write) for state updates.

**Engine**
- `SimpleWorkflowEngine`:
    - Implements `WorkflowEngineProtocol`.
    - **Logic**:
        1. **Load State**: Fetch existing `WorkflowRun` from `JsonRunRepository`.
        2. **Graph Validation**: Validates graph (removes disconnected components, checks cycles).
        3. **Topological Sort**: Sorts nodes execution order.
        4. **Execution Loop**: Iterates through sorted nodes.
            - **Resume Check**: If node state is `COMPLETED` in `RunRepository`, it is **skipped**.
            - **Execute**: Delegates to `PravahaTaskExecutor` -> `BotManagerProtocol`.
            - **State Updates**: Updates `RunRepository` at start (`RUNNING`) and end (`COMPLETED`) of each node.
            - **Failure Handling**: Catches exceptions, marks node/run as `FAILED`, and **stops execution**. This allows the run to be re-triggered later to resume from this point.

### 3. Application Layer (Use Cases)
*Orchestrates Domain and Infrastructure.*

- `WorkflowUseCase`: 
    - `create_workflow(dto)`: Validates and saves.
    - `get_workflow(id)`: Retrieves.
- `ExecutionUseCase`:
    - `trigger_run(workflow_id)`: Creates `WorkflowRun`, initializes Engine.
    - `get_run_status(run_id)`: Retrieves state.

### 4. Presentation Layer (API)
*FastAPI Routers (Minimal Logic).*

- `WorkflowRouter`: Maps HTTP requests to `WorkflowUseCase`.
- `RunRouter`: Maps HTTP requests to `ExecutionUseCase`.
- **Response Models**: Pydantic DTOs separate from Domain Entities (or reused if clean).

## Key Implementation Details

### Input Handling
The `WorkflowNode` inputs will be stored as the `InputItem` definitions (Source/Path/Value). 
- When the `WorkflowEngine` executes a node, it passes these inputs to the `BotManager`. 
- Since `BotManager` and `ApplicationManager` now handle `InputItem` -> `List[Dict]` conversion logic (implemented in previous task), the Engine simply passes the Pydantic models (or dict representation) through.

### Dependency Injection
Use a container or factory pattern to inject `JsonWorkflowRepository` and `SimpleWorkflowEngine` into `WorkflowManagerProtocol` at startup. This ensures the domain logic remains testable and decoupled from the JSON file system.
