import json
import pytest
from pathlib import Path
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from fastapi import HTTPException

@pytest.fixture
def temp_config_file(tmp_path):
    config_file = tmp_path / "storage_config.json"
    initial_config = {
        "output": str(tmp_path / "output"),
        "intermediate": str(tmp_path / "intermediate"),
        "knowledge": str(tmp_path / "knowledge")
    }
    with open(config_file, "w") as f:
        json.dump(initial_config, f)
    
    # Create the directories so get_path validation passes by default
    (tmp_path / "output").mkdir()
    (tmp_path / "intermediate").mkdir()
    (tmp_path / "knowledge").mkdir()
    
    return config_file, initial_config

def test_local_storage_manager_init_existing_config(temp_config_file):
    config_path, initial_config = temp_config_file
    manager = LocalStorageManager(config_file=str(config_path))
    assert manager.config_file == config_path
    # check that defaults were not overwritten implies config file remained same? 
    # Logic: _ensure_defaults runs only if not exists.

def test_local_storage_manager_get_path_valid(temp_config_file):
    config_path, initial_config = temp_config_file
    manager = LocalStorageManager(config_file=str(config_path))
    
    path = manager.get_path("output")
    assert path == Path(initial_config["output"])
    assert path.exists()

def test_local_storage_manager_get_path_missing_category(temp_config_file):
    config_path, _ = temp_config_file
    manager = LocalStorageManager(config_file=str(config_path))
    
    with pytest.raises(HTTPException) as excinfo:
        manager.get_path("non_existent")
    assert excinfo.value.status_code == 400

def test_local_storage_manager_get_path_path_does_not_exist(temp_config_file):
    config_path, initial_config = temp_config_file
    # Delete the directory
    Path(initial_config["output"]).rmdir()
    
    manager = LocalStorageManager(config_file=str(config_path))
    
    with pytest.raises(HTTPException) as excinfo:
        manager.get_path("output")
    assert excinfo.value.status_code == 500

def test_update_config(temp_config_file):
    config_path, _ = temp_config_file
    manager = LocalStorageManager(config_file=str(config_path))
    
    new_out = config_path.parent / "new_out"
    new_inter = config_path.parent / "new_inter"
    new_know = config_path.parent / "new_know"
    
    # Create them so validation passes if we were to test get_path immediately, 
    # although update_config doesn't validate existence, it just writes.
    
    manager.update_config(str(new_out), str(new_inter), str(new_know))
    
    # Verify file content
    with open(config_path, "r") as f:
        data = json.load(f)
    
    assert data["output"] == str(new_out.resolve())
    assert data["intermediate"] == str(new_inter.resolve())
    assert data["knowledge"] == str(new_know.resolve())

def test_ensure_defaults_creates_config(tmp_path):
    # Pass a non-existent config file
    config_file = tmp_path / "missing_config.json"
    manager = LocalStorageManager(config_file=str(config_file))
    
    assert config_file.exists()
    
    with open(config_file, "r") as f:
        data = json.load(f)
    
    assert "output" in data
    assert "intermediate" in data
    assert "knowledge" in data
    
    # Also defaults try to create directories relative to project_root.
    # Since project_root is derived from __file__, it points to real source location.
    # We cannot easily assert side effects on real filesystem unless we mock project_root.
    # But checking config file creation is a valid partial test.
