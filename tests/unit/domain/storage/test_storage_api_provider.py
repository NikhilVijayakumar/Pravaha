import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from pathlib import Path

from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider

@pytest.fixture
def mock_storage_manager():
    return MagicMock()

@pytest.fixture
def client(mock_storage_manager):
    provider = StorageAPIProvider(mock_storage_manager)
    # create a mock app or just use the router 
    # TestClient works with router but best to mount it or use it as app if possible
    # We can use the provider.router directly but paths will be relative to "/" + prefix if we mount?
    # provider.router has prefix "/storage".
    # When passing router to TestClient, it treats it as app.
    # So if router has prefix "/storage", requests must include "/storage"? 
    # Actually TestClient(router) ignores the prefix defined in router init usually? 
    # No, APIRouter prefix is part of the route.
    return TestClient(provider.router)

def test_set_storage_config(client, mock_storage_manager):
    payload = {
        "output_path": "/out",
        "intermediate_path": "/inter",
        "knowledge_path": "/know"
    }
    response = client.post("/storage/config", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "Configured successfully"}
    
    mock_storage_manager.update_config.assert_called_once_with("/out", "/inter", "/know")

def test_list_folders_success(client, mock_storage_manager, tmp_path):
    # Mock get_path to return a tmp dir with some folders
    target_dir = tmp_path / "real_output"
    target_dir.mkdir()
    (target_dir / "folder1").mkdir()
    (target_dir / "folder2").mkdir()
    (target_dir / "file.txt").touch() # should be ignored
    
    mock_storage_manager.get_path.return_value = target_dir
    
    response = client.get("/storage/output/folders")
    assert response.status_code == 200
    data = response.json()
    assert data["folders"] == ["folder1", "folder2"]
    
    mock_storage_manager.get_path.assert_called_with("output")

import fastapi
def test_list_folders_missing_category(client, mock_storage_manager):
    # Mimic manager raising 400
    mock_storage_manager.get_path.side_effect = fastapi.HTTPException(status_code=400, detail="Category missing")
    
    response = client.get("/storage/badcat/folders")
    assert response.status_code == 400
    
def test_list_files_success(client, mock_storage_manager, tmp_path):
    target_dir = tmp_path / "base"
    target_dir.mkdir()
    folder_dir = target_dir / "myfolder"
    folder_dir.mkdir()
    (folder_dir / "file1.txt").touch()
    (folder_dir / "file2.json").touch()
    (folder_dir / "subfolder").mkdir() # should be ignored
    
    # get_path returns base
    mock_storage_manager.get_path.return_value = target_dir
    
    response = client.get("/storage/output/myfolder/files")
    assert response.status_code == 200
    files = response.json()["files"]
    names = sorted([f["name"] for f in files])
    assert names == ["file1.txt", "file2.json"]

def test_list_files_folder_not_found(client, mock_storage_manager, tmp_path):
    mock_storage_manager.get_path.return_value = tmp_path
    
    response = client.get("/storage/output/missing_folder/files")
    assert response.status_code == 404

def test_get_content_json(client, mock_storage_manager, tmp_path):
    target_dir = tmp_path / "base"
    target_dir.mkdir()
    folder_dir = target_dir / "myfolder"
    folder_dir.mkdir()
    file_path = folder_dir / "data.json"
    file_path.write_text('{"key": "value"}', encoding="utf-8")
    
    mock_storage_manager.get_path.return_value = target_dir
    
    response = client.get("/storage/output/myfolder/data.json")
    assert response.status_code == 200
    assert response.json() == {"content": {"key": "value"}}

def test_get_content_text(client, mock_storage_manager, tmp_path):
    target_dir = tmp_path / "base"
    target_dir.mkdir()
    folder_dir = target_dir / "myfolder"
    folder_dir.mkdir()
    file_path = folder_dir / "data.txt"
    file_path.write_text("hello world", encoding="utf-8")
    
    mock_storage_manager.get_path.return_value = target_dir
    
    response = client.get("/storage/output/myfolder/data.txt")
    assert response.status_code == 200
    # content handler returns {"content": ...}
    assert response.json() == {"content": "hello world"}
