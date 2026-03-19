import pytest
import os
from unittest.mock import MagicMock, patch, mock_open
import yaml # added for patching
from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager
from pravaha.domain.logging.utils.rotation_utils import LogRotationUtils

# Mock Nibandha Logger Class
class MockNibandhaLogger:
    def __init__(self, *args, **kwargs):
        self.should_rotate = list()
        
    def bind(self):
        return self
    
    @property
    def logger(self):
        return MagicMock()

    def should_rotate(self):
        return False
    
    def rotate_logs(self):
        pass
    
    def cleanup_old_archives(self):
        return 0

@pytest.fixture
def clean_logging_manager():
    # Reset singleton
    PravphaLoggingManager._instance = None
    yield
    PravphaLoggingManager._instance = None

# --- Manager Tests ---
class TestPravphaLoggingManager:
    """Target: src/nikhil/pravaha/domain/logging/manager/logging_manager.py"""

    def test_singleton_instance(self, clean_logging_manager):
        """[UT-NIB-001] Verify singleton behavior."""
        with patch('pravaha.domain.logging.manager.logging_manager.Nibandha', MockNibandhaLogger):
             # Initialize first
             PravphaLoggingManager.initialize()
             inst1 = PravphaLoggingManager.get_instance()
             inst2 = PravphaLoggingManager.get_instance()
             assert inst1 is not None 
             assert inst1 is inst2

    def test_get_logger_auto_init(self, clean_logging_manager):
        """[UT-NIB-002/003] Verify get_logger auto-initializes and returns logger."""
        with patch('pravaha.domain.logging.manager.logging_manager.Nibandha', MockNibandhaLogger):
            logger = PravphaLoggingManager.get_logger()
            assert logger is not None
            # Check if instance is now created
            assert PravphaLoggingManager._instance is not None

# --- Utils Tests ---
class TestLogRotationUtils:
    """Target: src/nikhil/pravaha/domain/logging/utils/rotation_utils.py"""

    def test_setup_rotation_defaults(self):
        """[UT-NIB-004/005] Verify rotation setup with defaults."""
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.makedirs"):
                # Use a dummy path for config
                with patch("pravaha.domain.logging.utils.rotation_utils.Path") as mock_path:
                    mock_path.return_value.__truediv__.return_value = MagicMock()
                    
                    LogRotationUtils.setup_rotation()
                    
                    mock_file.assert_called_once()
                    handle = mock_file()
                    
                    # Verify YAML content by inspecting calls to yaml.dump OR file write
                    # yaml.dump writes to the file handle
                    # So handle.write() should be called
                    # But yaml.dump might split writes.
                    
                    # Instead, we can verify that yaml.dump was called with correct dict
                    with patch("yaml.dump") as mock_yaml_dump:
                        LogRotationUtils.setup_rotation()
                        args, _ = mock_yaml_dump.call_args
                        config_dict = args[0]
                        assert config_dict['max_size_mb'] == 50
                        assert config_dict['rotation_interval_hours'] == 24

    def test_check_and_rotate(self):
        """[UT-NIB-006] Verify rotation check delegation."""
        mock_nib = MagicMock()
        mock_nib.should_rotate.return_value = True
        
        rotated = LogRotationUtils.check_and_rotate(mock_nib)
        
        assert rotated is True
        mock_nib.should_rotate.assert_called_once()
        mock_nib.rotate_logs.assert_called_once()

    def test_cleanup_delegation(self):
        """[UT-NIB-007] Verify cleanup delegation."""
        mock_nib = MagicMock()
        mock_nib.cleanup_old_archives.return_value = 5
        
        deleted = LogRotationUtils.cleanup_old_logs(mock_nib)
        
        assert deleted == 5
        mock_nib.cleanup_old_archives.assert_called_once()
