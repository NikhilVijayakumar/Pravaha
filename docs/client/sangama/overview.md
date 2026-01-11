# Sangama (UI) - Code Review & Improvements

**Repository**: `E:\Python\Pravaha\NikhilVijayakumar-sangama-ce1c8cc60171`

**Purpose**: Electron-based desktop UI for Pravaha applications (Akashavani backend)

**Review Date**: 2026-01-12

---

## Current Architecture

### ✅ Strengths

1. **Clean Separation of Concerns**
   - Data layer: `WorkflowRepositoryImpl.ts`
   - Domain: `WorkflowRepository.ts` (interfaces)
   - Presentation: ViewModels + Components
   - Follows hexagonal/clean architecture principles

2. **Existing Application Execution**
   - `useApplicationViewModel.ts` already implements streaming execution
   - Input transformation (Record→Array) works correctly
   - LLM config override handling functional
   
3. **React Flow Integration**
   - Visual workflow designer using React Flow
   - Drag-drop node creation
   - Edge connections

4. **Type Safety**
   - Comprehensive TypeScript types in `types.ts`
   - Good enum usage (TaskType, RunStatus)

### ⚠️ Areas for Improvement

---

## 🔴 CRITICAL: Workflow Execution Not Implemented

### Current State
- `useWorkflowRunViewModel.ts` only has CRUD operations (list, trigger)
- `triggerRun` calls backend and does nothing else
- No polling for status
- No node execution loop

### Required Implementation

**Create New Hook**: `useWorkflowExecutionLoop.ts`

```typescript
export const useWorkflowExecutionLoop = (runId: string) => {
  const [currentNode, setCurrentNode] = useState<WorkflowNode | null>(null)
  const [runStatus, setRunStatus] = useState<string>('RUNNING')
  const { handleRun } = useApplicationViewModel(baseUrl, currentNode?.task_name)

  useEffect(() => {
    const interval = setInterval(async () => {
      const status = await repo.getExecutionStatus(runId)
      setRunStatus(status.status)
      
      if (status.current_node?.status === 'PENDING') {
        await executeNode(status.current_node)
      }
      
      if (status.status === 'COMPLETED' || status.status === 'FAILED') {
        clearInterval(interval)
      }
    }, 2000) // Poll every 2s
    
    return () => clearInterval(interval)
  }, [runId])

  const executeNode = async (node: any) => {
    await repo.updateNodeStatus(runId, node.node_id, { status: 'IN_PROGRESS' })
    
    try {
      // REUSE existing handleRun from ApplicationViewModel!
      const result = await handleRun(node.inputs, node.llm_config)
      
      await repo.updateNodeStatus(runId, node.node_id, {
        status: 'COMPLETED',
        output_data: result
      })
    } catch (error) {
      await repo.updateNodeStatus(runId, node.node_id, {
        status: 'FAILED',
        error: error.message,
        retry_attempt: 1
      })
    }
  }

  return { currentNode, runStatus }
}
```

**Priority**: 🔴 **CRITICAL** - Without this, workflows cannot execute!

---

## 🟡 Medium Priority Improvements

### 1. Repository Implementation Missing Methods

**File**: `src/renderer/src/features/workflow/data/WorkflowRepositoryImpl.ts`

**Missing Methods** (needed for new API):
```typescript
async getExecutionStatus(runId: string): Promise<ServerResponse<any>> {
  return this.api.get<any>(`api/execution/run/${runId}/status`)
}

async updateNodeStatus(runId: string, nodeId: string, request: any): Promise<ServerResponse<any>> {
  return this.api.post<any>(`api/execution/run/${runId}/node/${nodeId}/status`, request)
}

async getNodeOutput(runId: string, nodeId: string): Promise<ServerResponse<any>> {
  return this.api.get<any>(`api/execution/run/${runId}/node/${nodeId}/output`)
}
```

**Priority**: 🟡 **HIGH** - Required for execution loop

---

### 2. Type Definitions Need Updates

**File**: `src/renderer/src/features/workflow/domain/types.ts`

**Current**:
```typescript
export type TaskType = 'APP' | 'UTIL' | 'LLM' | 'ENVIRONMENT' | 'GLOBAL_LLM' | 'NOTE' | 'GROUP'
export type RunStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'SKIPPED'
```

**Should Add**:
```typescript
export type RunStatus = 'NEW' | 'PENDING' | 'IN_PROGRESS' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'SKIPPED'

// Match backend NodeType enum
export type NodeType = 'APP' | 'UTIL' | 'LLM' | 'GLOBAL_LLM' | 'ENVIRONMENT' | 'NOTE' | 'GROUP'

// Execution status response
export interface ExecutionStatus {
  run_id: string
  status: RunStatus
  current_node: {
    node_id: string
    node_type: NodeType
    task_name: string
    status: RunStatus
    retry_count: number
  } | null
  nodes_status: Record<string, RunStatus>
}
```

**Priority**: 🟡 **MEDIUM**

---

### 3. WorkflowNode Uses `task_type` but Backend Now Uses `node_type`

**File**: `src/renderer/src/features/workflow/domain/types.ts`

**Current**:
```typescript
export interface WorkflowNode {
  id: string
  task_type: TaskType  // ← Mismatched!
  task_name: string
  inputs: Record<string, InputItem>
  ...
}
```

**Backend Expects**:
```typescript
{
  node_type: NodeType  // ← Different field name
}
```

**Solution**: 
- Either: Update UI to use `node_type` (breaking change for UI)
- Or: Add backend serialization to accept both `task_type` and `node_type`

**Recommendation**: Update UI to match backend (clearer semantics)

**Priority**: 🟡 **MEDIUM**

---

## 🟢 Low Priority / Nice-to-Have

### 4. Error Handling Enhancement

**Current**: Simple error messages  
**Improvement**: Structured error types, user-friendly messages

```typescript
export class WorkflowExecutionError extends Error {
  constructor(
    public nodeId: string,
    public nodeName: string,
    public originalError: Error
  ) {
    super(`Node ${nodeName} failed: ${originalError.message}`)
  }
}
```

---

### 5. Execution Progress UI

**Current**: No visual feedback during execution  
**Improvement**: Real-time node status visualization

**Suggested Component**:
```typescript
<WorkflowExecutionProgress
  run={currentRun}
  nodeStates={nodeStates}
  currentNodeId={currentNode?.id}
/>
```

Shows:
- ✅ Completed nodes (green)
- 🔄 In-progress node (blue, spinner)
- ⏳ Pending nodes (gray)
- ❌ Failed nodes (red)

---

### 6. Retry UI Controls

Allow user to manually retry failed nodes:

```typescript
<Button onClick={() => retryNode(failedNodeId)}>
  Retry Node
</Button>
```

---

### 7. Execution Logs Panel

Show real-time logs during execution:

```typescript
<ExecutionLogsPanel
  logs={executionLogs}
  isStreaming={isStreaming}
/>
```

Reuse existing `streamLogs` from `useApplicationViewModel`

---

## 🛠️ Suggested File Structure Changes

### Current Structure
```
features/workflow/
├── data/
│   └── WorkflowRepositoryImpl.ts
├── domain/
│   ├── WorkflowRepository.ts
│   └── types.ts
└── presentation/
    ├── viewmodels/
    │   ├── useWorkflowDesignerViewModel.ts
    │   ├── useWorkflowListViewModel.ts
    │   └── useWorkflowRunViewModel.ts
    └── components/
        └── ...
```

### Recommended Addition
```
features/workflow/
├── data/
│   └── WorkflowRepositoryImpl.ts  [ADD NEW METHODS]
├── domain/
│   ├── WorkflowRepository.ts
│   └── types.ts  [UPDATE TYPES]
└── presentation/
    ├── viewmodels/
    │   ├── useWorkflowDesignerViewModel.ts
    │   ├── useWorkflowListViewModel.ts
    │   ├── useWorkflowRunViewModel.ts
    │   └── useWorkflowExecutionLoop.ts  [NEW]
    └── components/
        ├── WorkflowExecutionProgress.tsx  [NEW]
        └── ExecutionLogsPanel.tsx  [NEW]
```

---

## Implementation Priority

### Phase 1 (Critical - Do First)
1. ✅ Create `useWorkflowExecutionLoop` hook
2. ✅ Add new repository methods (`getExecutionStatus`, etc.)
3. ✅ Update types (`ExecutionStatus`, add `NEW`/`IN_PROGRESS` states)

**Estimated Effort**: 2-3 hours

### Phase 2 (High Priority)
4. ✅ Align `task_type` → `node_type` naming
5. ✅ Add execution progress UI component
6. ✅ Wire up execution loop in WorkflowDashboard

**Estimated Effort**: 1 day

### Phase 3 (Nice-to-Have)
7. ✅ Enhanced error handling
8. ✅ Retry UI controls
9. ✅ Execution logs panel

**Estimated Effort**: 1-2 days

---

## Testing Checklist

### Manual Tests
- [ ] Create simple 3-node workflow (A→B→C)
- [ ] Trigger execution
- [ ] Verify polling starts
- [ ] Verify nodes execute sequentially
- [ ] Test failure scenario (force node to fail)
- [ ] Test retry logic
- [ ] Verify workflow completes

### Edge Cases
- [ ] Network disconnection mid-execution
- [ ] Server restart during execution
- [ ] Multiple concurrent workflow runs
- [ ] Workflow with parallel branches (if supported)

---

## Code Quality Notes

### ✅ Good Practices Already Present
- TypeScript strict mode
- ESLint configured
- Separation of concerns
- React hooks best practices
- Clean component architecture

### Suggestions
- Add unit tests for ViewModels (currently none found)
- Add integration tests for workflow execution
- Document complex state management logic
- Add JSDoc comments for public APIs

---

## Summary

**Overall Code Quality**: 🟢 **Good** (7/10)

**Strengths**:
- Clean architecture
- Type safety
- Good separation of concerns

**Critical Gap**: Workflow execution loop not implemented

**Recommended Next Steps**:
1. Implement `useWorkflowExecutionLoop` (Critical)
2. Add new repository methods (Critical)
3. Test end-to-end workflow execution
4. Add execution progress UI (High priority)
