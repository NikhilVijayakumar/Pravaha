# Workflow Module - E2E Test Scenarios

**Status**: Planning
**Client Docs**: `docs/client/workflow-module.md`

## 1. Workflow Lifecycle

### Scenario: Create and Run Simple Workflow
1.  **Create**: POST `/api/workflow/create` with 2 nodes (APP, UTIL) and 1 edge.
2.  **Verify**: Response contains created ID.
3.  **Run**: POST `/api/workflow/run?workflow_id={id}`.
4.  **Check Status**: GET `/api/workflow/run/{run_id}` -> Status should eventually be COMPLETED.
5.  **Verify Execution**: Check mock bot manager received calls.

## 2. Dependency Execution

### Scenario: Ordered Execution
1.  **Setup**: Workflow A -> B.
2.  **Run**: Trigger execution.
3.  **Verify**: Log/Mock check confirms A executed before B.

## 3. Configuration Injection

### Scenario: LLM Config Flow
1.  **Setup**: Node LLM (Top-tier model) executed first. Node APP (Generator) executed second.
2.  **Action**: Run workflow.
3.  **Verify**: APP execution received the LLM config from the LLM node.

## 4. Failure Handling

### Scenario: Execution Failure
1.  **Setup**: Workflow with Node A that is mocked to fail.
2.  **Run**: Trigger execution.
3.  **Verify**: Run Status becomes FAILED. Node A State is FAILED. Dependent nodes are skipped/PENDING.
