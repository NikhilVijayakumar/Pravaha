# Workflow Module - Unit Test Scenarios

**Status**: Planning
**Source Code**: `src/nikhil/pravaha/domain/workflow/`
**Docs**: `docs/modules/workflow.md`

## 1. Entities (`entity/`, `model/`)

### Happy Path
- [ ] **Workflow Model**: Create valid `Workflow`, serialize to JSON, deserialize back.
- [ ] **Node Types**: Verify `WorkflowNode` validation for APP, UTIL, LLM, ENVIRONMENT types.
- [ ] **Edge Validation**: Create valid `WorkflowEdge`.

### Failure Scenarios
- [ ] **Invalid Node**: Create node with missing required fields.
- [ ] **Invalid Edge**: Edge referencing non-existent nodes (might be validated in Service).

## 2. Repositories (`infrastructure/`, `repository/`)

### Happy Path
- [ ] **Workflow Repo Save/Load**: Save workflow -> Load by ID -> Verify equality.
- [ ] **Workflow Repo List**: Save multiple -> List all.
- [ ] **Run Repo Save/Load**: Save run -> Load by ID.
- [ ] **Run Repo Update**: Update node state -> Verify persistence.

### Failure Scenarios
- [ ] **Not Found**: Load non-existent ID -> Return None or raise Error.
- [ ] **Duplicate Save**: Save existing ID -> Update or Error (depending on logic).

## 3. Engine & Service (`service/`)

### Happy Path
- [ ] **Topological Sort**: A->B->C graph -> Returns [A, B, C].
- [ ] **Independent Nodes**: A, B (no edges) -> Returns [A, B] (or B, A).
- [ ] **Complex Graph**: Diamond dependency (A->B, A->C, B->D, C->D) -> Correct order.
- [ ] **Execution Logic**: `execute()` iterates nodes and calls executor.

### Failure Scenarios
- [ ] **Cycle Detection**: A->B->A graph -> Raise `CycleDetectedError`.
- [ ] **Missing Dependency**: Edge refers to missing node -> Raise Validation Error.

## 4. Task Executor (`infrastructure/`)

### Happy Path
- [ ] **Route APP**: Node Type APP -> Calls `bot_manager.stream_run`.
- [ ] **Route UTIL**: Node Type UTIL -> Calls `bot_manager.run`.
- [ ] **LLM Context**: Node Type LLM -> Stores config in context.
- [ ] **Env Context**: Node Type ENVIRONMENT -> Stores env vars.
