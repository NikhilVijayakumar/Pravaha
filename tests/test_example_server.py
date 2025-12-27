from fastapi.testclient import TestClient
from pravaha_example.service.server import app
from pravaha_example.config.settings import ApplicationType, UtilsType

client = TestClient(app)

def test_run_calculator_utility():
    # Test valid addition
    payload = {
        "task_name": UtilsType.CALCULATOR.value,
        "inputs": [{"operation": "add", "a": 5, "b": 3}]
    }
    response = client.post("/run/utility", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "result": 8}

    # Test valid multiplication
    payload["inputs"] = [{"operation": "multiply", "a": 5, "b": 3}]
    response = client.post("/run/utility", json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == 15

def test_run_calculator_invalid_operation():
    payload = {
        "task_name": UtilsType.CALCULATOR.value,
        "inputs": [{"operation": "divide", "a": 5, "b": 3}]
    }
    response = client.post("/run/utility", json=payload)
    assert response.status_code == 200
    assert "Unknown operation" in response.json()["result"]

def test_run_app_math_bot_stream():
    payload = {
        "task_name": ApplicationType.MATH_ASSISTANT.value,
        "inputs": [{"question": "1+1"}]
    }
    response = client.post("/run/application/stream", json=payload)
    assert response.status_code == 200
    
    # Check headers (Starlette SSE sets these)
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    # Check content
    content = response.text
    assert "Hello! I am the Math Assistant." in content
    assert "Processing: {'question': '1+1'}" in content
    assert "[DONE]" in content

def test_storage_list_output_folders():
    # Since we use LocalStorageManager with default paths, and mocked nothing,
    # it might try to create/read from .Amsha/output...
    # We should ensure the test doesn't fail if directory is empty.
    response = client.get("/storage/output/folders")
    assert response.status_code == 200
    assert "folders" in response.json()
