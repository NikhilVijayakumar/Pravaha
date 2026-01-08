# Workflow API Backend Issues

## Summary
The frontend is correctly calling workflow API endpoints at `http://127.0.0.1:8000/api/workflow/*`, but the backend is returning a **422 Unprocessable Entity** error for workflow creation requests. This indicates a data validation or schema mismatch between the frontend request payload and the backend's expected schema.

## Current Status
- ✅ Frontend URLs are correctly formed with `/api` prefix
- ✅ Backend endpoints are reachable (no 404 errors)
- ❌ Backend returns 422 error - validation/schema issue

---

## API Endpoints & Test Commands

### 1. Create Workflow
**Endpoint:** `POST /api/workflow/create`

**Current Issue:** Returns 422 (Unprocessable Entity)

**Test Command (bash):**
```bash
curl -X POST http://127.0.0.1:8000/api/workflow/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Workflow",
    "nodes": [
      {
        "id": "node_1",
        "task_type": "APP",
        "task_name": "generate_scientific_knowledge_application",
        "inputs": {},
        "position": {
          "x": 500,
          "y": 400
        }
      }
    ],
    "edges": [],
    "created_at": "2026-01-08T03:15:25.000Z",
    "updated_at": "2026-01-08T03:15:25.000Z"
  }'
```

**Test Command (PowerShell):**
```powershell
$body = @'
{
  "name": "Test Workflow",
  "nodes": [
    {
      "id": "node_1",
      "task_type": "APP",
      "task_name": "generate_scientific_knowledge_application",
      "inputs": {},
      "position": {"x": 500, "y": 400}
    }
  ],
  "edges": [],
  "created_at": "2026-01-08T03:15:25.000Z",
  "updated_at": "2026-01-08T03:15:25.000Z"
}
'@

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/workflow/create" -Method POST -ContentType "application/json" -Body $body
```

**Expected Response:**
```json
{
  "id": "uuid-generated-by-backend",
  "name": "Test Workflow",
  "nodes": [...],
  "edges": [...],
  "created_at": "2026-01-08T03:15:25.000Z",
  "updated_at": "2026-01-08T03:15:25.000Z"
}
```

---

### 2. List Workflows
**Endpoint:** `GET /api/workflow/list`

**Test Command:**
```bash
curl -X GET http://127.0.0.1:8000/api/workflow/list
```

**Expected Response:**
```json
[
  {
    "id": "workflow-id-1",
    "name": "Workflow 1",
    "nodes": [...],
    "edges": [...],
    "created_at": "...",
    "updated_at": "..."
  }
]
```

---

### 3. Get Workflow by ID
**Endpoint:** `GET /api/workflow/{id}`

**Test Command:**
```bash
curl -X GET http://127.0.0.1:8000/api/workflow/550e8400-e29b-41d4-a716-446655440000
```

**Expected Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Workflow",
  "nodes": [...],
  "edges": [...],
  "created_at": "...",
  "updated_at": "..."
}
```

---

### 4. Update Workflow
**Endpoint:** `POST /api/workflow/update`

**Test Command:**
```bash
curl -X POST http://127.0.0.1:8000/api/workflow/update \
  -H "Content-Type: application/json" \
  -d '{
    "id": "existing-workflow-id",
    "name": "Updated Workflow Name",
    "nodes": [...],
    "edges": [...],
    "created_at": "2026-01-08T03:15:25.000Z",
    "updated_at": "2026-01-08T03:20:00.000Z"
  }'
```

---

### 5. Delete Workflow
**Endpoint:** `DELETE /api/workflow/{id}`

**Test Command:**
```bash
curl -X DELETE http://127.0.0.1:8000/api/workflow/550e8400-e29b-41d4-a716-446655440000
```

**Expected Response:**
```json
true
```

---

### 6. Trigger Workflow Run
**Endpoint:** `POST /api/workflow/run?workflow_id={id}`

**Test Command:**
```bash
curl -X POST "http://127.0.0.1:8000/api/workflow/run?workflow_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response:**
```json
{
  "id": "run-uuid",
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "RUNNING",
  "started_at": "2026-01-08T03:15:25.000Z"
}
```

---

### 7. Get Workflow Run
**Endpoint:** `GET /api/workflow/run/{run_id}`

**Test Command:**
```bash
curl -X GET http://127.0.0.1:8000/api/workflow/run/run-uuid-here
```

---

### 8. List Workflow Runs (All)
**Endpoint:** `GET /api/workflow/runs`

**Test Command:**
```bash
curl -X GET http://127.0.0.1:8000/api/workflow/runs
```

**Expected Response:**
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

---

### 9. List Workflow Runs (Filtered by Workflow)
**Endpoint:** `GET /api/workflow/runs?workflow_id={id}`

**Test Command:**
```bash
curl -X GET "http://127.0.0.1:8000/api/workflow/runs?workflow_id=550e8400-e29b-41d4-a716-446655440000"
```

---

## Request Payload Schema

### Workflow Object
```typescript
{
  id?: string                    // Only for update, not for create
  name: string                   // Required
  nodes: WorkflowNode[]          // Required
  edges: WorkflowEdge[]          // Required
  created_at?: string            // ISO 8601 timestamp
  updated_at?: string            // ISO 8601 timestamp
}
```

### WorkflowNode Object
```typescript
{
  id: string                             // Required - unique node identifier
  task_type: "APP" | "UTIL" | "LLM" | "ENVIRONMENT"  // Required
  task_name: string                      // Required - e.g., "generate_scientific_knowledge_application"
  inputs: Record<string, InputItem>      // Required - can be empty {}
  position: {                            // Required
    x: number,
    y: number
  },
  llm_config?: {                         // Optional
    ui_mode: "creative" | "evaluation",
    ui_model_id: string,
    model_config: {
      base_url?: string,
      model: string,
      api_key: string
    },
    llm_parameters: {
      temperature?: number,
      top_p?: number,
      max_completion_tokens?: number,
      stop?: string[]
    }
  },
  environment_config?: {                 // Optional
    variables: Array<{
      key: string,
      value: string,
      description?: string
    }>
  }
}
```

### InputItem Object (Union Type)
```typescript
// Direct input (hardcoded value)
{
  key_name: string,
  source: "direct",
  value: any
}

// JSON file input
{
  key_name: string,
  source: "file",
  path: string,
  format: "json"
}

// Text file input
{
  key_name: string,
  source: "file",
  path: string,
  format: "text"
}
```

### WorkflowEdge Object
```typescript
{
  id: string,              // Required - unique edge identifier
  source: string,          // Required - source node id
  target: string,          // Required - target node id
  sourceHandle?: string,   // Optional
  targetHandle?: string    // Optional
}
```

---

## Backend Issues to Fix

### Issue 1: 422 Validation Error on Workflow Creation
**Severity:** HIGH  
**Status:** ❌ Not Working

**Description:**  
The backend is rejecting valid workflow creation requests with a 422 status code.

**Steps to Reproduce:**
1. Send POST request to `/api/workflow/create` with the minimal payload shown above
2. Backend returns 422 error

**Possible Causes:**
- Backend Pydantic model field names don't match frontend payload
- Backend expects different data types (e.g., expecting snake_case vs camelCase)
- Missing required fields in backend schema that frontend isn't sending
- Extra validation rules on backend that frontend payload doesn't satisfy

**Debug Steps:**
1. Check backend logs for specific validation error messages
2. Compare backend Pydantic model with the WorkflowNode/WorkflowEdge schemas above
3. Verify field name conventions (snake_case vs camelCase)
4. Check if backend expects additional required fields

**Recommended Fix:**
- Update backend Pydantic models to match the exact schema shown above
- Ensure field names match (prefer snake_case as per Python convention)
- Make `created_at` and `updated_at` optional or auto-generate them on backend
- Return detailed validation errors in 422 response body

---

## Frontend Implementation Details

**Source Files:**
- Workflow Types: `src/renderer/src/features/workflow/domain/types.ts`
- API Client: `src/renderer/src/features/workflow/data/WorkflowRepositoryImpl.ts`
- Save Logic: `src/renderer/src/features/workflow/presentation/components/WorkflowDesigner.tsx`

**Current Frontend Behavior:**
1. User creates workflow in visual designer
2. Clicks "Save" button
3. Frontend constructs payload matching schema above
4. Calls `POST /api/workflow/create`
5. Backend returns 422
6. Frontend shows error alert to user

---

## Testing Checklist

- [ ] Create workflow endpoint returns 201 with valid ID
- [ ] List workflows endpoint returns array
- [ ] Get workflow by ID returns correct workflow
- [ ] Update workflow endpoint accepts updates
- [ ] Delete workflow endpoint removes workflow
- [ ] Trigger run endpoint initiates execution
- [ ] Get run endpoint returns run status
- [ ] List runs endpoints return correct data

---

## Contact

For questions about this issue, contact the frontend team or refer to:
- Frontend codebase: `e:\Python\sangama`
- This documentation: `docs/issues/workflow-api-backend-issues.md`
