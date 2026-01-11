# 🔄 Client-Driven Workflow Execution Protocol

## 1. Overview

This document defines the protocol for the **Client-Driven Workflow Execution** model. In this model, the Backend manages the **state and order** of the workflow, while the **Client (UI)** is responsible for the actual **execution** of nodes (Applications and Utilities).

This shift allows for:
- Richer client-side interactivity during execution.
- Leveraging client-side data freshness checks ("Data Loading" step).
- Sequential, controlled execution flow managed by the client but orchestrated by the server.

---

## 2. High-Level Flow

1.  **Initiation**: Client requests a new Run. Server initializes state.
2.  **Orchestration Loop**:
    *   Client **Polls** for Run Status.
    *   Server identifies the **Next Pending Node** based on topological order.
    *   Client receives Pending Node ID.
    *   **Data Check**: Client refreshes data dependencies for the node to ensure version consistency.
    *   **Execution**: Client executes the node's logic (API call).
    *   **Completion**: Client reports success/failure to Server.
    *   Server updates state and prepares the next node.

---

## 3. Execution State Machine

### Node States
- **NEW**: Node is waiting in the queue. Not yet ready.
- **PENDING**: Node is the *current* executable step. Waiting for Client pickup.
- **IN_PROGRESS**: Client has acknowledged the node and is executing it.
- **COMPLETED**: Execution finished successfully.
- **FAILED**: Execution failed (after retries).

---

## 4. API Interaction Detail

### 4.1. Start Workflow Run

**UI Request**:
```http
POST /api/execution/run
Content-Type: application/json

{
  "workflow_id": "uuid"
}
```

**Backend Response**:
```json
{
  "workflow_run_id": "run-uuid-1234",
  "status": "RUNNING"
}
```

### 4.2. Get Run Status (Polling)

**UI Request**:
```http
GET /api/execution/run/{workflow_run_id}/status
```

**Backend Response**:
```json
{
  "run_id": "run-uuid-1234",
  "status": "RUNNING",
  "current_node": {
    "node_id": "node-A",
    "status": "PENDING",    // <--- Key Signal for Client
    "retry_count": 0
  },
  "nodes_status": {
    "node-A": "PENDING",
    "node-B": "NEW",
    "node-C": "NEW"
  }
}
```

### 4.3. Client Execution Logic (The "Loop")

When the Client receives a response with `current_node.status == "PENDING"`, it performs the following steps **strictly in order**:

#### Step 1: Identify Node Type
Check if the Node Type is **APPLICATION** or **UTILITY**.
*(Note: Only these two types are executable in this protocol. Others are pass-through or config).*

#### Step 2: Data Freshness Check (CRITICAL)
Before executing, the Client **MUST** reload the latest data for the node's inputs.
> "The UI loads the latest data version... as it let you load the data from previous connected node... check for latest data version before finishing the api payload."

1.  Identify input dependencies (edges connected to this node).
2.  Fetch/Refresh the output data from the preceding nodes.
3.  Construct the **Final API Payload** using this fresh data.

#### Step 3: Mark In-Progress
Notify the server that execution is starting.

**UI Request**:
```http
POST /api/execution/run/{workflow_run_id}/node/{node_id}/status
{
  "status": "IN_PROGRESS"
}
```

#### Step 4: Execute Node API
Call the independent API endpoint for the Application or Utility. These APIs are stateless with respect to the Workflow Run ID.

*   **Application**: `POST /api/run/application/stream`
*   **Utility**: `POST /api/run/utility`

**Note**: These endpoints do NOT accept a `workflow_run_id`. They execute the logic based solely on the provided inputs. State tracking is handled separately in Step 5.

#### Step 5: Handle Result & Update Server

**Scenario A: Success**
1.  Client receives inputs/outputs from the API.
2.  Client updates Server with `COMPLETED` status.

**UI Request**:
```http
POST /api/execution/run/{workflow_run_id}/node/{node_id}/status
{
  "status": "COMPLETED",
  "output_data": { ... } // Optional, if server needs to persist output references
}
```

**Scenario B: Failure**
1.  Client catches error.
2.  Check **Max Retry Threshold** (Client-side logic or Server-side config).
    *   **If Retries Remaining**:
        *   Update status to `PENDING` (to trigger a re-try loop).
    *   **If Max Retries Exceeded**:
        *   Update status to `FAILED`.

**UI Request (Retry)**:
```http
POST /api/execution/run/{workflow_run_id}/node/{node_id}/status
{
  "status": "PENDING",
  "error": "Timeout",
  "retry_attempt": 1
}
```

---

## 5. Backend Logic (Server Side)

1.  **State Management**: The server must maintain the DAG state.
2.  **Next Node Selection**:
    *   When a node is marked `COMPLETED`:
        *   Find all children of the completed node.
        *   Check if *all* parents of a child are `COMPLETED`.
        *   If yes, mark that child as `PENDING`.
3.  **Concurrency**:
    *   For now, **Sequential Execution** is enforced. The server should only expose **one** `PENDING` node at a time.
    *   If multiple branches technically could run, pick one based on deterministic ordering (e.g., Node ID or Creation time) to keep it sequential as requested.

## 6. Summary of Responsibilities

| Responsibility | Actor | Description |
| :--- | :--- | :--- |
| **Workflow State** | Backend | Tracks what is New, Pending, running, Completed. |
| **Next Step Logic** | Backend | Decides *which* node runs next based on graph topology. |
| **Data Orchestration**| Client | Fetches latest data from inputs, ensures version consistency. |
| **Execution** | Client | Calls the actual App/Util REST APIs. |
| **Retry Policy** | Client/Server | Client detects fail, Server tracks retry status/counts. |
