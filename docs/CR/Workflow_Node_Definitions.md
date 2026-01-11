# 🧩 Workflow Node Definitions

## 1. Node Categories

Nodes in the Workflow system are categorized by their role in the execution lifecycle.

### A. Executable Nodes (Active)
These nodes represent actual units of work. They are the **ONLY** nodes that are executed during the workflow run.

| Node Type | Code | Description | Executable? |
| :--- | :--- | :--- | :--- |
| **Application** | `APP` | Represents a full domain application (e.g., "Knowledge Generator"). Runs complex logic via the Application API. | ✅ YES |
| **Utility** | `UTIL` | Represents a helper function or utility (e.g., "File Converter", "Data Transform"). Runs fast, functional logic via the Utility API. | ✅ YES |

### B. Configuration Nodes (Passive)
These nodes provide configuration or context to the Executable Nodes but are not "run" themselves in the execution loop. Their data is resolved *before* the Executable Node runs.

| Node Type | Code | Description | Executable? |
| :--- | :--- | :--- | :--- |
| **LLM Config** | `LLM` | Defines Local LLM settings (Model, Context Window). Connects to APP/UTIL nodes to configure their AI backend. | ❌ NO |
| **Global LLM** | `GLOBAL_LLM`| Defines default LLM settings for the entire workflow. | ❌ NO |
| **Environment** | `ENVIRONMENT`| Defines environment variables and global constants. | ❌ NO |

### C. UI/Organization Nodes (Virtual)
These nodes exist purely for the user interface and organization. They are ignored by the backend execution engine.

| Node Type | Code | Description | Executable? |
| :--- | :--- | :--- | :--- |
| **Note** | `NOTE` | A sticky note for comments/documentation on canvas. | ❌ NO |
| **Group** | `GROUP` | A container to visually group multiple nodes. | ❌ NO |

---

## 2. Executable Node Details

### 🟢 Application Node (`APP`)
*   **Purpose**: Encapsulates a major business capability.
*   **Execution**:
    *   Triggered when status is `PENDING`.
    *   **Input**: Takes dynamic inputs from previous nodes + static configuration.
    *   **Process**: UI calls `POST /api/application/{id}/run`.
    *   **Output**: Returns structured data (JSON/Files) that can be used by subsequent nodes.

### 🔵 Utility Node (`UTIL`)
*   **Purpose**: Performs data transformation, formatting, or lightweight processing.
*   **Execution**:
    *   Triggered when status is `PENDING`.
    *   **Input**: Takes specific data inputs (e.g., a string to formatting, a file to convert).
    *   **Process**: UI calls `POST /api/utility/{id}/run`.
    *   **Output**: Returns transformed data.

---

## 3. Data Flow & Dependencies

*   **Executable Nodes** (`APP`, `UTIL`) rely on **Upstream Data**.
*   When a Client prepares to execute a node, it must **Refresh Data**:
    1.  Look at incoming edges.
    2.  If edge comes from `APP` or `UTIL`, fetch the *latest output version* of that parent node.
    3.  If edge comes from `LLM` or `ENVIRONMENT`, resolve the configuration values.
    4.  Combine all inputs into the API Payload.
