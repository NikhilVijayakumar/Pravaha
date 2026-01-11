# Sangama - Bot/Application Module Guide

**Application**: Sangama UI  
**Module**: Bot Manager / Application Execution  
**Last Updated**: 2026-01-12

---

## Current Implementation

### ✅ What Works Well

**File**: `src/renderer/src/features/bot-manager/presentation/viewmodels/useApplicationViewModel.ts`

```typescript
export const useApplicationViewModel = (baseUrl: string, selectedTask: string | null) => {
  const { literal } = useLanguage()
  
  // Schema loading
  const [inputSchemaState, fetchInputSchema] = useDataState<any>()
  const [outputSchemaState, fetchOutputSchema] = useDataState<any>()
  
  // Execution with streaming
  const [executionState, runExecution] = useDataState<any>()
  const [streamLogs, setStreamLogs] = useState<string[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  
  const handleRun = async (inputs: Record<string, InputItem>, llmConfig?: LLMConfigOverride) => {
    // Transform inputs to array format
    const inputsArray = Object.entries(inputs).map(([key, item]) => ({
        [item.key_name || key]: item
    }))
    
    const payload = {
        task_name: selectedTask,
        inputs: inputsArray,
        llm_config_override: llmConfig
    }
    
    // Stream execution
    const res = await ApplicationRepo.runApplicationStream(
      baseUrl,
      payload,
      (chunk) => {
        const lines = chunk.split('\n').filter(Boolean)
        setStreamLogs((prev) => [...prev, ...lines])
      }
    )
  }
}
```

**Strengths**:
- ✅ Streaming execution with SSE
- ✅ Input transformation (Record→Array)
- ✅ LLM config override handling
- ✅ Schema loading for inputs/outputs
- ✅ Real-time log streaming

---

## Integration with Workflow Execution

### How It Fits

The **workflow execution loop** should **reuse** this existing `handleRun` function!

```typescript
// In useWorkflowExecutionLoop.ts
const executeNode = async (node: WorkflowNode) => {
  const { handleRun } = useApplicationViewModel(baseUrl, node.task_name)
  
  // Mark node in progress
  await repo.updateNodeStatus(runId, node.id, { status: 'IN_PROGRESS' })
  
  try {
    // REUSE existing application execution!
    const result = await handleRun(node.inputs, node.llm_config)
    
    // Mark completed
    await repo.updateNodeStatus(runId, node.id, {
      status: 'COMPLETED',
      output_data: result
    })
  } catch (error) {
    await repo.updateNodeStatus(runId, node.id, {
      status: 'FAILED',
      error: error.message,
      retry_attempt: 1
    })
  }
}
```

**Key Point**: Don't duplicate logic - workflow execution = polling + existing `handleRun`

---

## Improvements

### 1. Extract Execution Logic

**Current**: Logic mixed in ViewModel  
**Better**: Separate service layer

```typescript
// NEW: src/renderer/src/features/bot-manager/domain/ApplicationExecutor.ts
export class ApplicationExecutor {
  constructor(private baseUrl: string) {}
  
  async execute(
    taskName: string, 
    inputs: Record<string, InputItem>,
    llmConfig?: LLMConfigOverride,
    onStream?: (chunk: string) => void
  ): Promise<any> {
    const inputsArray = this.transformInputs(inputs)
    const payload = { task_name: taskName, inputs: inputsArray, llm_config_override: llmConfig }
    
    return ApplicationRepo.runApplicationStream(this.baseUrl, payload, onStream)
  }
  
  private transformInputs(inputs: Record<string, InputItem>) {
    return Object.entries(inputs).map(([key, item]) => ({
      [item.key_name || key]: item
    }))
  }
}
```

**Benefits**:
- Reusable across ViewModels
- Testable in isolation
- Clearer separation of concerns

---

### 2. Error Handling Enhancement

**Current**: Basic try-catch  
**Better**: Structured error types

```typescript
// NEW: src/renderer/src/features/bot-manager/domain/errors.ts
export enum ApplicationErrorType {
  NETWORK_ERROR = 'NETWORK_ERROR',
  EXECUTION_ERROR = 'EXECUTION_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR'
}

export class ApplicationExecutionError extends Error {
  constructor(
    public type: ApplicationErrorType,
    public taskName: string,
    public originalError?: Error,
    public details?: any
  ) {
    super(`Application ${taskName} failed: ${originalError?.message}`)
  }
}

// Usage in ViewModel:
try {
  await handleRun(...)
} catch (error) {
  throw new ApplicationExecutionError(
    ApplicationErrorType.EXECUTION_ERROR,
    selectedTask,
    error,
    { inputs, llmConfig }
  )
}
```

---

### 3. Progress Tracking

**Current**: Only logs streaming  
**Better**: Structured progress events

```typescript
export interface ExecutionProgress {
  stage: 'INITIALIZING' | 'RUNNING' | 'STREAMING' | 'FINALIZING'
  percentage?: number
  message?: string
}

const [progress, setProgress] = useState<ExecutionProgress>({ stage: 'INITIALIZING' })

const handleRun = async (...) => {
  setProgress({ stage: 'INITIALIZING', message: 'Preparing execution...' })
  
  const payload = { ... }
  
  setProgress({ stage: 'RUNNING', message: 'Executing application...' })
  
  await ApplicationRepo.runApplicationStream(baseUrl, payload, (chunk) => {
    setProgress({ stage: 'STREAMING', message: 'Receiving results...' })
    setStreamLogs((prev) => [...prev, ...lines])
  })
  
  setProgress({ stage: 'FINALIZING', message: 'Complete!' })
}

// In UI:
<ProgressBar stage={progress.stage} message={progress.message} />
```

---

### 4. Timeout Handling

**Current**: No timeout  
**Better**: Configurable timeout

```typescript
const EXECUTION_TIMEOUT = 5 * 60 * 1000 // 5 minutes

const handleRunWithTimeout = async (...) => {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), EXECUTION_TIMEOUT)
  
  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal
    })
    return res
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new ApplicationExecutionError(
        ApplicationErrorType.TIMEOUT_ERROR,
        selectedTask
      )
    }
    throw error
  } finally {
    clearTimeout(timeoutId)
  }
}
```

---

## API Endpoints Covered

### POST `/api/run/application/stream`

**Purpose**: Execute application with streaming output

**Request**:
```json
{
  "task_name": "generate_content",
  "inputs": [
    {
      "topic": {
        "source": "direct",
        "value": "AI Ethics"
      }
    }
  ],
  "llm_config_override": {
    "model_config": {
      "model": "gpt-4",
      "api_key": "..."
    },
    "llm_parameters": {
      "temperature": 0.7
    }
  }
}
```

**Response**: Server-Sent Events (SSE) stream

**Current Implementation**: ✅ Working well

---

## Testing Recommendations

### Unit Tests Needed

```typescript
// test/features/bot-manager/domain/ApplicationExecutor.test.ts
describe('ApplicationExecutor', () => {
  it('should transform inputs correctly', () => {
    const executor = new ApplicationExecutor('http://localhost:8000')
    const inputs = {
      topic: { key_name: 'topic', source: 'direct', value: 'AI' }
    }
    const result = executor['transformInputs'](inputs)
    expect(result).toEqual([{ topic: { source: 'direct', value: 'AI' } }])
  })
  
  it('should handle execution errors', async () => {
    // Mock failed execution
    await expect(executor.execute('invalid_task', {})).rejects.toThrow()
  })
  
  it('should call onStream callback during execution', async () => {
    const onStream = jest.fn()
    await executor.execute('test_task', {}, undefined, onStream)
    expect(onStream).toHaveBeenCalled()
  })
})
```

---

## Best Practices

1. **Reuse in Workflows**: Don't duplicate - call `handleRun` from workflow loop
2. **Schema Validation**: Use input/output schemas for validation
3. **Stream Management**: Clean up streams on component unmount
4. **Error Feedback**: Show user-friendly error messages
5. **Loading States**: Show progress during execution

---

## Integration Checklist

When integrating with workflow execution:

- [ ] Extract execution logic to `ApplicationExecutor` service
- [ ] Use `handleRun` in workflow execution loop
- [ ] Add error handling with structured types
- [ ] Implement progress tracking
- [ ] Add timeout handling
- [ ] Test end-to-end execution flow

---

## Summary

**Status**: ✅ **Excellent** - Well-implemented, just needs minor refactoring

**Key Strengths**:
- Streaming execution works perfectly
- Input transformation correct
- LLM config override functional

**Minor Improvements**:
- Extract to service layer
- Better error handling
- Progress tracking

**Integration**: Ready to use in workflow execution!
