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

def test_run_app_math_bot_stream_no_inputs():
    payload = {
        "task_name": ApplicationType.MATH_ASSISTANT.value
        # No inputs provided
    }
    response = client.post("/run/application/stream", json=payload)
    assert response.status_code == 200
    
    content = response.text
    assert "Hello! I am the Math Assistant." in content
    # Should NOT process any inputs implies "Processing:" might not appear or logic handles it?
    # MathBot: if inputs: ...
    assert "Processing:" not in content
    assert "[DONE]" in content

def test_storage_list_output_folders():
    # Since we use LocalStorageManager with default paths, and mocked nothing,
    # it might try to create/read from .Amsha/output...
    # We should ensure the test doesn't fail if directory is empty.
    assert response.status_code == 200
    assert "folders" in response.json()

def test_storage_browse_output():
    # We expect the 'output' folder to exist and contain items we created (nested_folder, root_file.txt)
    # The LocalStorageManager in example server uses the real file system (defaults to root/output)
    
    response = client.get("/storage/output/browse")
    assert response.status_code == 200
    data = response.json()
    items = data["items"]
    
    names = [i["name"] for i in items]
    # We created 'nested_folder' and 'root_file.txt' in previous step
    assert "nested_folder" in names
    assert "root_file.txt" in names
    
    # Check types
    for item in items:
        if item["name"] == "nested_folder":
            assert item["type"] == "folder"
        if item["name"] == "root_file.txt":
            assert item["type"] == "file"
        if item["name"] == "root_file.txt":
            assert item["type"] == "file"

def test_storage_comprehensive_scenarios():
    # 1. Output (JSON content)
    # Root file
    resp = client.get("/storage/output/read?path=root_result.json")
    assert resp.status_code == 200
    assert resp.json()["content"]["status"] == "root"
    
    # Nested file
    resp = client.get("/storage/output/read?path=nested_output/data.json")
    assert resp.status_code == 200
    assert resp.json()["content"]["status"] == "nested"

    # 2. Intermediate (JSON content)
    # Root file
    resp = client.get("/storage/intermediate/read?path=step1.json")
    assert resp.status_code == 200
    assert resp.json()["content"]["step"] == 1
    
    # Nested file
    resp = client.get("/storage/intermediate/read?path=nested_inter/temp.json")
    assert resp.status_code == 200
    assert resp.json()["content"]["step"] == 2

    # 3. Knowledge (Markdown content)
    # Root file
    resp = client.get("/storage/knowledge/read?path=root_info.md")
    assert resp.status_code == 200
    assert "# Root Info" in resp.json()["content"]
    
    # Nested file
    resp = client.get("/storage/knowledge/read?path=nested_wiki/python.md")
    assert resp.status_code == 200
    assert "# Python" in resp.json()["content"]
    
    # 4. Verify Browsing Nested Folders
    resp = client.get("/storage/knowledge/browse?path=nested_wiki")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any(i["name"] == "python.md" for i in items)
