# 📦 Pravaha Workflow System

## Backend Architecture Specification (Revised)

---

## 1. Purpose & Scope

The **Pravaha Workflow System Backend** is a **workflow orchestration service** that allows users to:

* Define **directed acyclic workflows (DAGs)** composed of executable tasks
* Persist workflows and execution runs
* Execute workflows deterministically using an external execution engine
* Track execution state at workflow and node level

> ⚠️ **Non-Goal**
> This system does **not** execute LLMs or tools directly.
> Execution is delegated to an external execution layer (e.g., Pravaha).

---

## 2. Architectural Principles

* **Domain-Driven Design (DDD)**
* **Clean Architecture**
* **Protocol-first design**
* **Framework-agnostic core**
* **Explicit execution boundaries**
* **Replaceable infrastructure**

---

## 3. High-Level Architecture

```
┌───────────────────────────┐
│       Presentation        │  FastAPI (Thin)
│   (Routers / DTOs only)   │
└────────────┬──────────────┘
             │
┌────────────▼──────────────┐
│       Application         │  Use Cases
│   (Workflow / Execution)  │
└────────────┬──────────────┘
             │
┌────────────▼──────────────┐
│          Domain           │  Entities + Protocols
│   (Workflow, Engine API)  │
└────────────┬──────────────┘
             │
┌────────────▼──────────────┐
│      Infrastructure       │  JSON Repos, Executors
│  (Persistence, Adapters)  │
└───────────────────────────┘
```

---

## 4. Domain Layer (Core)

> **No external dependencies**

### 4.1 Entities (Aggregates)

#### `Workflow`

* Aggregate root
* Contains:

  * `nodes: List[WorkflowNode]`
  * `edges: List[WorkflowEdge]`
* Invariants:

  * Must be a DAG
  * All nodes must be connected

#### `WorkflowNode`

Represents a single executable step.

| Field       | Description                     |
| ----------- | ------------------------------- |
| `id`        | Unique identifier               |
| `task_type` | `APPLICATION` | `UTILITY`       |
| `task_name` | Logical task identifier         |
| `inputs`    | List of `InputItem` definitions |

#### `WorkflowRun`

Execution instance of a workflow.

| Field          | Description             |
| -------------- | ----------------------- |
| `id`           | Run identifier          |
| `workflow_id`  | Associated workflow     |
| `node_states`  | Map[node_id → RunState] |
| `started_at`   | Timestamp               |
| `completed_at` | Timestamp               |

---

### 4.2 Value Objects

#### `RunState`

```
PENDING → RUNNING → COMPLETED
                  → FAILED
                  → SKIPPED
```

---

## 5. Core Protocols (Interfaces)

### 5.1 Repository Protocols

```python
class WorkflowRepositoryProtocol(Protocol):
    def save(self, workflow: Workflow) -> None
    def get(self, workflow_id: str) -> Workflow
```

```python
class RunRepositoryProtocol(Protocol):
    def create(self, run: WorkflowRun) -> None
    def update_node_state(self, run_id: str, node_id: str, state: RunState) -> None
    def get(self, run_id: str) -> WorkflowRun
```

---

### 5.2 Execution Protocol (New)

#### `TaskExecutorProtocol`

This is the **explicit integration seam** between workflow orchestration and execution engines.

```python
class TaskExecutorProtocol(Protocol):
    def execute(
        self,
        task_type: TaskType,
        task_name: str,
        inputs: list[dict] | None,
        stream: bool = False
    ) -> Any | AsyncIterable[str]:
        ...
```

> ✅ The workflow engine depends **only** on this protocol.

---

### 5.3 Workflow Engine Protocol

```python
class WorkflowEngineProtocol(Protocol):
    def execute(workflow: Workflow, run: WorkflowRun) -> None
```

---

## 6. Application Layer (Use Cases)

### 6.1 WorkflowUseCase

| Method                 | Responsibility         |
| ---------------------- | ---------------------- |
| `create_workflow(dto)` | Validate DAG & persist |
| `get_workflow(id)`     | Retrieve workflow      |

---

### 6.2 ExecutionUseCase

| Method                     | Responsibility             |
| -------------------------- | -------------------------- |
| `trigger_run(workflow_id)` | Create run + invoke engine |
| `get_run_status(run_id)`   | Retrieve execution state   |

---

## 7. Infrastructure Layer

### 7.1 Persistence (JSON)

* `JsonWorkflowRepository`
* `JsonRunRepository`
* Atomic file writes
* Simple locking for concurrent updates

---

### 7.2 Execution Adapter

#### `PravahaTaskExecutor`

Implements `TaskExecutorProtocol` using `BotManagerProtocol`.

```text
WorkflowEngine
   ↓
TaskExecutorProtocol
   ↓
Pravaha BotManager
```

This ensures:

* Workflow system does not depend on FastAPI
* Pravaha remains reusable and standalone

---

## 8. Presentation Layer (API)

### Responsibilities

* Map HTTP → Use Cases
* Perform DTO validation
* Zero business logic

### Routers

| Router           | Purpose                |
| ---------------- | ---------------------- |
| `WorkflowRouter` | CRUD workflows         |
| `RunRouter`      | Trigger & monitor runs |

---

## 9. Explicit Non-Goals

❌ No scheduling
❌ No retries (future concern)
❌ No execution logic
❌ No LLM/tool awareness

---

# 🖥️ Pravaha Workflow System

## Frontend Architecture Specification (Revised)

---

## 1. Overview

The frontend is a **desktop Electron application** that provides:

* Visual workflow authoring
* Input configuration
* Execution monitoring
* Log inspection

It follows **MVVM + Clean Architecture**.

---

## 2. High-Level Architecture

```
┌──────────────────────────┐
│           View           │  React + MUI
│     (Stateless UI)       │
└───────────┬──────────────┘
            │
┌───────────▼──────────────┐
│        ViewModel          │  State + Commands
│     (Zustand / Hooks)     │
└───────────┬──────────────┘
            │
┌───────────▼──────────────┐
│          Model           │  Domain + Repos
│     (API / DTOs)         │
└──────────────────────────┘
```

---

## 3. Model Layer

### 3.1 Domain Models (TypeScript)

Mirrors backend entities:

* `Workflow`
* `WorkflowNode`
* `WorkflowEdge`
* `WorkflowRun`
* `RunState`

---

### 3.2 Repositories

| Repository           | Responsibility            |
| -------------------- | ------------------------- |
| `WorkflowRepository` | Workflow CRUD             |
| `RunRepository`      | Trigger runs, poll status |

---

## 4. ViewModel Layer

### 4.1 WorkflowDesignerViewModel

**Responsibilities**

* Manage React Flow state
* Enforce DAG constraints
* Node creation & deletion
* Validation feedback

**Commands**

* `addNode()`
* `removeNode()`
* `saveWorkflow()`

---

### 4.2 RunMonitorViewModel

**Responsibilities**

* Poll run state
* Derive UI-only states:

  * `BLOCKED`
  * `RETRYING`
* Compute progress

---

## 5. View Layer

### 5.1 Core Components

| Component                 | Description         |
| ------------------------- | ------------------- |
| `WorkflowCanvas`          | React Flow wrapper  |
| `NodePalette`             | Available tasks     |
| `InputConfigurationPanel` | Schema-driven forms |
| `ExecutionConsole`        | Node logs           |

---

### 5.2 Visual State Mapping

| RunState  | UI Representation |
| --------- | ----------------- |
| PENDING   | Grey              |
| RUNNING   | Blue (animated)   |
| COMPLETED | Green             |
| FAILED    | Red               |
| SKIPPED   | Muted             |

---

## 6. Input Configuration

Inputs are rendered dynamically based on `InputItem` type:

| Type   | UI          |
| ------ | ----------- |
| Direct | TextField   |
| JSON   | File Picker |
| Text   | File Picker |

Electron IPC is used for native file dialogs.

---

## 7. Theming & Localization

* MUI `ThemeProvider`
* Dark / Light mode
* All strings via `i18next`

---

## 8. Explicit Non-Goals (Frontend)

❌ No execution logic
❌ No workflow validation beyond DAG rules
❌ No backend assumptions

---

## 9. Resulting System Boundaries (Final)

```
Electron UI
   ↓ HTTP
Workflow API
   ↓ Use Case
Workflow Engine
   ↓ Protocol
TaskExecutor
   ↓ Adapter
Pravaha
```

---


