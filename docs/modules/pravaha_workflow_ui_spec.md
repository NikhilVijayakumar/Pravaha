# Pravaha Workflow System - UI Specification

## Overview
The UI will be an Electron application implementing **MVVM Clean Architecture**. It uses **Material UI (MUI)** for components, supports **Dark/Light themes**, and implements **Localization (i18n)**.

## Architecture: MVVM

### 1. Model Layer (Domain & Data)
- **Domain Models**: TypeScript interfaces mirroring the backend domain entities (`Workflow`, `WorkflowNode`, `RunState`, etc.).
- **Repositories**: 
    - `WorkflowRepository`: Handles API communication (`GET /api/workflow`, `POST /api/workflow`).
    - `RunRepository`: Handles execution control and status polling (`POST /api/run?workflow_id={id}`, `GET /api/run/{id}`).

### 2. ViewModel Layer (State & Logic)
- **WorkflowListViewModel**: Manages the list of workflows, loading states, and navigation to details.
- **WorkflowDesignerViewModel**: 
    - Manages the graph state (nodes, edges) using a library like React Flow.
    - Handles drag-and-drop logic for adding "Application" or "Utility" nodes.
    - Validation logic (e.g., detecting cycles).
    - Commands: `saveWorkflow`, `addNode`, `removeNode`.
- **RunMonitorViewModel**:
    - Polling logic or WebSocket subscription for real-time status.
    - Computed properties for overall progress (e.g., "3/5 Steps Completed").

### 3. View Layer (MUI + React)
- **Components**:
    - `WorkflowCanvas`: Wrapper around React Flow, styled with MUI `Box` and `Paper`.
    - `NodePalette`: Drawer or Sidebar listing available tasks.
    - `InputConfigurationPanel`: Dynamic form generated based on `InputItem` schemas (Direct vs File).
- **Theming**:
    - Use MUI's `ThemeProvider` and `useTheme` hook.
    - Colors defined in the theme palette (e.g., `primary.main` for active nodes, `error.main` for failed).
- **Localization**:
    - All text must use `t('key')` hooks.
    - Keys: `workflow.designer.addNode`, `workflow.status.pending`, etc.

## Functional Requirements

### Workflow Designer
- **Visualization**: Nodes are visualized as Cards with icons (App vs Util).
- **Configuration**: Clicking a node opens a `Drawer` (right side) to configure inputs.
    - **Schema-Driven Forms**: The inputs are rendered dynamically.
        - `DirectInputItem`: TextField.
        - `JsonInputItem`/`TextInputItem`: FileSelector (utilizing Electron's native dialog via IPC).
- **Validation**: Visual warning if required inputs (Source/Path) are missing.

### Execution Dashboard
- **Live Status**: Nodes change color/border based on `RunState` (PENDING, RUNNING, COMPLETED, FAILED, SKIPPED).
- **Resume/Retry Capability**:
    - If a run is `FAILED`, show a "Resume" or "Retry" button.
    - Action: Call `POST /api/run` (or specific resume endpoint if we added one, currently re-triggering existing run via backend logic usually requires re-submission or re-execution command. *Note: Backend implementation allows re-triggering the same run ID internally, but API exposes `POST /run` which creates NEW runs. To support Resume of specific run, UI should likely re-submit and backend handles logic, OR we need to expose `POST /run/{id}/resume`. Current backend limits: `POST /run` creates new. We need to clarify if UI creates new run or resumes. Backend `SimpleWorkflowEngine` supports resuming if called with same Run object. The API `trigger_run` creates a NEW run. To support true resume, we should add an endpoint `POST /run/{id}/execute` or similar. For now, UI assumes "Retry" = "Start New Run from Scratch" or we update API.* 
    - *Correction based on Implementation*: The implemented `WorkflowService` has `execute_run(run_id)`. The API `trigger_run` creates a new run. To resume, we strictly need a way to call `execute_run` on an existing ID. **Recommendation**: UI should treat "Retry" as "Create New Run" for now, unless we add a specific resume endpoint.
- **Logs Console**: A collapsable bottom panel showing logs for the selected node.

## Technology Stack
- **Framework**: Electron + React
- **UI Library**: Material UI (MUI) v5+
- **Graph Library**: React Flow (recommended)
- **State Management**: Zustand or React Context (managed by ViewModels)
- **Localization**: i18next
