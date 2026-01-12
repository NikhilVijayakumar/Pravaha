import pytest
import json
import tempfile
import shutil
from pathlib import Path
from pravaha.domain.workflow.manager.local_workflow_manager import LocalWorkflowManager


class TestLocalWorkflowManager:
    """Test LocalWorkflowManager configuration and path management."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def workflow_manager(self, temp_dir, monkeypatch):
        """Create a workflow manager with a temporary directory."""
        monkeypatch.chdir(temp_dir)
        return LocalWorkflowManager()
    
    def test_default_configuration_creation(self, workflow_manager, temp_dir):
        """Test that default configuration is created correctly."""
        config_file = temp_dir / ".Pravaha" / "config" / "workflow.json"
        assert config_file.exists()
        
        with open(config_file) as f:
            config = json.load(f)
        
        assert "details" in config
        assert "run" in config
        assert config["details"] == ".Pravaha/workflow/details"
        assert config["run"] == ".Pravaha/workflow/run"
    
    def test_default_directories_created(self, workflow_manager, temp_dir):
        """Test that default directories are created."""
        details_dir = temp_dir / ".Pravaha" / "workflow" / "details"
        run_dir = temp_dir / ".Pravaha" / "workflow" / "run"
        
        assert details_dir.exists()
        assert run_dir.exists()
    
    def test_custom_defaults(self, temp_dir, monkeypatch):
        """Test workflow manager with custom defaults."""
        monkeypatch.chdir(temp_dir)
        
        custom_defaults = {
            "details": "custom/workflows",
            "run": "custom/runs"
        }
        
        manager = LocalWorkflowManager(defaults=custom_defaults)
        
        config_file = temp_dir / ".Pravaha" / "config" / "workflow.json"
        with open(config_file) as f:
            config = json.load(f)
        
        assert config["details"] == "custom/workflows"
        assert config["run"] == "custom/runs"
        
        # Verify directories were created
        assert (temp_dir / "custom" / "workflows").exists()
        assert (temp_dir / "custom" / "runs").exists()
    
    def test_get_path_details(self, workflow_manager, temp_dir):
        """Test getting the details path."""
        details_path = workflow_manager.get_path("details")
        expected_path = temp_dir / ".Pravaha" / "workflow" / "details"
        
        assert details_path == expected_path
        assert details_path.exists()
    
    def test_get_path_run(self, workflow_manager, temp_dir):
        """Test getting the run path."""
        run_path = workflow_manager.get_path("run")
        expected_path = temp_dir / ".Pravaha" / "workflow" / "run"
        
        assert run_path == expected_path
        assert run_path.exists()
    
    def test_update_config(self, workflow_manager, temp_dir):
        """Test updating configuration via API."""
        new_details = "new/workflow/details"
        new_run = "new/workflow/run"
        
        workflow_manager.update_config(new_details, new_run)
        
        config_file = temp_dir / ".Pravaha" / "config" / "workflow.json"
        with open(config_file) as f:
            config = json.load(f)
        
        assert config["details"] == new_details
        assert config["run"] == new_run
    
    def test_get_config(self, workflow_manager):
        """Test getting current configuration."""
        config = workflow_manager.get_config()
        
        assert isinstance(config, dict)
        assert "details" in config
        assert "run" in config
    
    def test_is_configured(self, workflow_manager):
        """Test checking if workflow is configured."""
        assert workflow_manager.is_configured() is True
    
    def test_path_creation_on_get(self, workflow_manager, temp_dir):
        """Test that non-existent paths are created when accessed."""
        # Update to a path that doesn't exist yet
        workflow_manager.update_config("brand/new/details", "brand/new/run")
        
        # Get the path - it should be created
        details_path = workflow_manager.get_path("details")
        
        assert details_path.exists()
        assert details_path == temp_dir / "brand" / "new" / "details"
    
    def test_absolute_path_handling(self, workflow_manager, temp_dir):
        """Test that absolute paths are handled correctly."""
        abs_details = str(temp_dir / "absolute" / "details")
        abs_run = str(temp_dir / "absolute" / "run")
        
        workflow_manager.update_config(abs_details, abs_run)
        
        details_path = workflow_manager.get_path("details")
        
        # Should handle absolute paths correctly
        assert details_path.exists()
