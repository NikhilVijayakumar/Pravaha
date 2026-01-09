# Workflow Module - Technical Documentation

> **Audience:** Pravaha contributors and maintainers  
> **Client Documentation:** [docs/client/workflow-module.md](../client/workflow-module.md)

## Module Objective

The Workflow module enables **visual multi-step workflow execution** with:
1. Node-based workflow design (APP, UTIL, LLM, ENVIRONMENT nodes)
2. Topological execution (dependency-based ordering)
3. State persistence and restartability
4. LLM configuration injection between nodes

## Architecture

### Layered Architecture

```
┌──────────────────────────────┐
│  WorkflowAPIProvider         │  Presentation (FastAPI)
└────────────┬─────────────────┘
             │
┌────────────▼─────────────────┐
│  WorkflowService             │  Application (Business Logic)
└────────────┬─────────────────┘
             │
     ┌───────┴────────┐
     │                │
     ▼                ▼
┌────────────┐  ┌─────────────┐
│ Workflow   │  │   Run       │  Domain (Entities)
│ Repository │  │ Repository  │
└────────────┘  └─────────────┘
     │                │
     ▼                ▼
┌────────────┐  ┌─────────────┐
│   JSON     │  │    JSON     │  Infrastructure (Persistence)
│ Workflow   │  │     Run     │
│ Repository │  │ Repository  │
└────────────┘  └─────────────┘
```

### Components

#### 1. Entities (`src/nikhil/pravaha/domain/workflow/entity/`)

**Workflow** - Definition of workflow
```python
class Workflow:
    id: str
    name: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    created_at: datetime
    updated_at: datetime
```

**WorkflowNode** - Individual task in workflow  
```python
class WorkflowNode:
    id: str
    task_type: str  # APP, UTIL, LLM, ENVIRONMENT
    task_name: str
    inputs: Dict[str, WorkflowInput]  # Key → Input source
    llm_config: Optional[Dict]  # For LLM nodes
    position: Dict[str, float]  # UI positioning
```

**WorkflowEdge** - Dependency between nodes
```python
class WorkflowEdge:
    id: str
    source: str  # Node ID
    target: str  # Node ID
```

**WorkflowRun** - Execution instance
```python
class WorkflowRun:
    id: str
    workflow_id: str
    status: str  # PENDING, RUNNING, COMPLETED, FAILED
    node_states: Dict[str, str]  # node_id → status
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

#### 2. Repositories (`src/nikhil/pravaha/domain/workflow/infrastructure/`)

**JsonWorkflowRepository**
- Persists workflows to `data/workflows.json`
- CRUD operations on workflows
- Efficient rename without full reload

**JsonRunRepository**
- Persists runs to `data/runs.json`
- Track execution history
- Query runs by workflow_id

#### 3. Engine (`src/nikhil/pravaha/domain/workflow/service/`)

**SimpleWorkflowEngine**
- Orchestrates workflow execution
- Topological sort for execution order
- State management (PENDING → RUNNING → COMPLETED/FAILED)
- Injects LLM config from LLM nodes to APP nodes

**Key Algorithm:**
```python
def execute(self, workflow: Workflow, run_id: str):
    # 1. Build dependency graph
    graph = self._build_graph(workflow)
    
    # 2. Topological sort
    execution_order = self._topological_sort(graph)
    
    # 3. Execute in order
    for node in execution_order:
        # Update state: RUNNING
        self._update_node_state(run_id, node.id, "RUNNING")
        
        try:
            # Execute node via task executor
            result = self.task_executor.execute(node)
            
            # Update state: COMPLETED
            self._update_node_state(run_id, node.id, "COMPLETED")
        except Exception as e:
            # Update state: FAILED
            self._update_node_state(run_id, node.id, "FAILED")
            raise
```

#### 4. Task Executor (`src/nikhil/pravaha/domain/workflow/infrastructure/`)

**PravahaTaskExecutor**
- Bridge between workflow and bot manager
- Routes APP nodes → `bot_manager.stream_run()`
- Routes UTIL nodes → `bot_manager.run()`
- Handles LLM and ENVIRONMENT nodes specially

```python
def execute(self, node: WorkflowNode) -> Any:
    if node.task_type == "APP":
        # Resolve task enum
        task = self._resolve_task(node.task_name, ApplicationType)
        # Get LLM config (from node or workflow context)
        llm_config = self._get_llm_config(node)
        # Execute
        return self.bot_manager.stream_run(task, node.inputs, llm_config)
    
    elif node.task_type == "UTIL":
        task = self._resolve_task(node.task_name, UtilsType)
        return self.bot_manager.run(task, node.inputs)
    
    elif node.task_type == "LLM":
        # Store LLM config for downstream nodes
        return self._store_llm_config(node)
    
    elif node.task_type == "ENVIRONMENT":
        # Store environment variables
        return self._store_env_vars(node)
```

## Data Flow

### Workflow Creation

```
POST /api/workflow/create
    ↓
WorkflowAPIProvider.create_workflow()
    ↓
WorkflowService.create_workflow(workflow)
    ↓
Generate UUID, timestamps
    ↓
workflow_repo.save(workflow)
    ↓
Write to data/workflows.json
    ↓
Return created workflow
```

### Workflow Execution

```
POST /api/workflow/run?workflow_id=xxx
    ↓
WorkflowAPIProvider.run_workflow()
    ↓
WorkflowService.trigger_run(workflow_id)
    ↓
1. Load workflow from repository
2. Create WorkflowRun (PENDING)
3. Save run to repository
4. engine.execute(workflow, run)
    ├─→ Topological sort nodes
    ├─→ For each node:
    │   ├─→ Update state: RUNNING
    │   ├─→ task_executor.execute(node)
    │   └─→ Update state: COMPLETED/FAILED
    └─→ Update run.status: COMPLETED/FAILED
    ↓
Return WorkflowRun
```

### LLM Config Injection

```
Workflow with nodes:
    [LLM Config] ──→ [APP: Generate]
    
Execution:
1. Execute LLM node first (no dependencies)
   → Store config in execution context
   
2. Execute APP node
   → Check for connected LLM node
   → Inject LLM config from context
   → Pass to bot_manager.stream_run(..., llm_config)
```

## Design Patterns

### 1. Repository Pattern
Abstracts persistence:
- `WorkflowRepositoryProtocol` - Interface
- `JsonWorkflowRepository` - Concrete implementation
- Easy to swap (e.g., SQLRepository)

### 2. Command Pattern
Each workflow run is a command object (`WorkflowRun`) that can be:
- Executed
- Stored
- Replayed
- Queried

### 3. Strategy Pattern
Different node types (APP, UTIL, LLM, ENV) use different execution strategies.

### 4. Topological Sort Algorithm
DAG (Directed Acyclic Graph) execution ensures dependencies are satisfied.

## Key Design Decisions

### Why JSON Persistence?

**Chose:** JSON files  
**Instead of:** Database

**Reasons:**
1. **Simplicity** - No DB setup required
2. **Portability** - Easy to backup/share
3. **Debugging** - Human-readable
4. **Prototyping** - Fast iteration

**Trade-off:** Not suitable for high-concurrency or large-scale deployments.

### Why Topological Sort?

Ensures nodes execute in dependency order:
- If NodeB depends on NodeA (edge: A → B)
- NodeA executes before NodeB
- Prevents reading uninitialized data

### Why Separate Run from Workflow?

**Workflow** = Template/Blueprint  
**Run** = Execution Instance

**Benefits:**
1. **History** - Keep all execution records
2. **Debugging** - See what failed and when
3. **Restartability** - Resume from last successful node
4. **Analytics** - Track success rates, durations

### Why Four Node Types?

| Type | Purpose | Example |
|------|---------|---------|
| APP | LLM applications | "Generate content" |
| UTIL | Utilities | "Validate output" |
| LLM | Config provider | "GPT-4 creative" |
| ENVIRONMENT | Env vars | "API_KEY=xxx" |

**Separation allows:**
- Clear visual distinction in UI
- Different validation rules
- Context injection (LLM → APP)

## Node Input Sources

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
  "path": "knowledge/dataset.json",
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

**Resolution:** Task executor reads files and injects values before execution.

## State Transitions

```
WorkflowRun States:
    PENDING → RUNNING → COMPLETED
                  ↓
                FAILED

Node States:
    PENDING → RUNNING → COMPLETED
                  ↓
                FAILED
```

**Rules:**
- Run starts in PENDING
- Changes to RUNNING when first node starts
- Changes to COMPLETED when all nodes complete
- Changes to FAILED if any node fails

## Testing

### Unit Tests

```python
def test_topological_sort():
    # A → B → C
    workflow = create_test_workflow()
    order = engine._topological_sort(workflow)
    assert order == [A, B, C]

def test_workflow_execution():
    run = workflow_service.trigger_run(workflow_id)
    assert run.status == "COMPLETED"
    assert run.node_states["node-1"] == "COMPLETED"
```

### Integration Tests

```python
def test_workflow_api_create(client):
    response = client.post("/api/workflow/create", json={...})
    assert response.status_code == 200

def test_workflow_api_run(client):
    response = client.post(f"/api/workflow/run?workflow_id={id}")
    assert response.json()["status"] in ["RUNNING", "COMPLETED"]
```

## Performance Considerations

1. **Sequential Execution** - Nodes execute one at a time (no parallelization yet)
2. **JSON I/O** - Read/write entire file (lock during writes)
3. **In-Memory Sorting** - Topological sort scales O(V + E)

## Future Enhancements

- [ ] Parallel node execution (independent nodes)
- [ ] Conditional branching (if/else nodes)
- [ ] Loop nodes (iterate over lists)
- [ ] Sub-workflows (workflow as node)
- [ ] Database backend for scalability
- [ ] Workflow versioning
- [ ] Scheduled execution (cron-like)
- [ ] Webhooks for workflow events
