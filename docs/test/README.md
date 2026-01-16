# Testing Strategy & Guidelines

This document outlines the testing strategy for the Pravaha project. We follow a documentation-driven testing approach where test requirements are derived from module and client documentation to ensure the implementation fulfills its contracts.

## 📂 Test Structure

Tests are organized relative to the source structure, with a clear separation between Unit and End-to-End (E2E) tests.

```
tests/
├── unit/               # Isolated unit tests (mocked dependencies)
│   ├── domain/
│   │   ├── auth/
│   │   ├── bot/
│   │   ├── llm/
│   │   ├── storage/
│   │   └── workflow/
├── e2e/                # Integration/E2E tests (real dependencies/API calls)
│   ├── domain/
│   │   ├── auth/
│   │   ├── ...
├── conftest.py         # Global fixtures
└── ...
```

## 🧪 Testing Categories

### 1. Unit Tests (`tests/unit/`)
*   **Goal**: Verify logic of individual components (classes, functions) in isolation.
*   **Dependencies**: All external dependencies (File I/O, Network, DB, downstream classes) should be **MOCKED**.
*   **Coverage**:
    *   Happy path (expected behavior)
    *   Edge cases (boundaries, empty inputs)
    *   Error handling (specific exceptions raised)

### 2. End-to-End / Integration Tests (`tests/e2e/`)
*   **Goal**: Verify modules work together and APIs function as expected from a client perspective.
*   **Dependencies**: use real implementations where possible (e.g., real file system for Storage, real FastAPI app request for Auth).
*   **Coverage**:
    *   Workflow verification (A -> B -> C)
    *   Configuration loading (Real files)
    *   API Contract validation (Request/Response schemas)

## 📝 The Documentation-Driven Process

For each module (`Auth`, `Bot`, `Storage`, `Workflow`, `LLM`), we follow this cycle:

1.  **Analyze Documentation**:
    *   Review `docs/modules/<module>.md` (Technical Contract)
    *   Review `docs/client/<module>.md` (Usage Contract)
2.  **Define Test Requirements**:
    *   List "Must Haves" based on the docs.
    *   Identify corner cases implied by the docs.
3.  **Gap Analysis**:
    *   Check existing `tests/unit` and `tests/e2e`.
    *   Identify missing coverage.
4.  **Implement**:
    *   Write missing tests.
    *   Refactor existing tests if they don't match the structure.

## 🚀 Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit

# Run only e2e tests
pytest tests/e2e

# Run for specific module
pytest tests/unit/domain/auth
```
