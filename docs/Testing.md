# Testing Guide

This document outlines the testing strategy for the Pravaha project.

## Test Structure

- **`tests/unit/`**: Unit tests for individual modules.
    - **`domain/bot`**: Tests for Bot Manager logic and models.
    - **`domain/storage`**: Tests for Storage Manager and API.
- **`tests/test_example_server.py`**: Integration tests for the example package.

## Running Tests

We use `pytest` as the test runner.

### Run All Tests
```bash
pytest
```

### Run Unit Tests Only
```bash
pytest tests/unit
```

### Run Specific Test File
```bash
pytest tests/test_example_server.py
```

### Troubleshooting
If you encounter environment issues regarding `TestClient` or `asyncio`, try running with verbose output:
```bash
pytest -vv
```
