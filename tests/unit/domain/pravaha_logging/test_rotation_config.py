"""
Tests for log rotation configuration.

Verifies that rotation config uses daily timestamp format
and correct default values.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import yaml

from pravaha.domain.logging.utils.rotation_utils import LogRotationUtils


class TestRotationConfig:
    """Test suite for rotation configuration."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        # Create temp directory
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        import os
        os.chdir(self.test_dir)
        
        yield
        
        # Cleanup
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_rotation_config_created(self):
        """Verify rotation config file is created."""
        LogRotationUtils.setup_rotation()
        
        config_path = Path(".Nibandha/config/rotation_config.yaml")
        assert config_path.exists(), \
            "Rotation config file should be created"
    
    def test_timestamp_format_daily(self):
        """Verify timestamp format is daily (%Y-%m-%d), not per-restart."""
        LogRotationUtils.setup_rotation()
        
        config_path = Path(".Nibandha/config/rotation_config.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config['timestamp_format'] == '%Y-%m-%d', \
            "Timestamp format must be '%Y-%m-%d' to prevent file proliferation"
        
        assert config['timestamp_format'] != '%Y-%m-%d_%H-%M-%S', \
            "Timestamp format must NOT include time (causes new file per restart)"
    
    def test_default_rotation_values(self):
        """Verify default rotation configuration values."""
        LogRotationUtils.setup_rotation()
        
        config_path = Path(".Nibandha/config/rotation_config.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check defaults
        assert config['enabled'] is True
        assert config['max_size_mb'] == 50
        assert config['rotation_interval_hours'] == 24
        assert config['archive_retention_days'] == 30
        assert config['log_data_dir'] == 'logs/data'
        assert config['archive_dir'] == 'logs/archive'
    
    def test_custom_rotation_values(self):
        """Verify custom rotation values are respected."""
        LogRotationUtils.setup_rotation(
            max_size_mb=100,
            rotation_interval_hours=12,
            archive_retention_days=60
        )
        
        config_path = Path(".Nibandha/config/rotation_config.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config['max_size_mb'] == 100
        assert config['rotation_interval_hours'] == 12
        assert config['archive_retention_days'] == 60
    
    def test_config_directory_created(self):
        """Verify config directory is created if it doesn't exist."""
        config_dir = Path(".Nibandha/config")
        assert not config_dir.exists(), "Config dir should not exist initially"
        
        LogRotationUtils.setup_rotation()
        
        assert config_dir.exists(), "Config directory should be created"
        assert config_dir.is_dir(), "Config path should be a directory"
    
    def test_custom_config_path(self):
        """Verify custom config path is respected."""
        custom_path = Path("custom/location/rotation.yaml")
        
        LogRotationUtils.setup_rotation(config_path=custom_path)
        
        assert custom_path.exists(), "Custom config path should be created"
        
        with open(custom_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config['timestamp_format'] == '%Y-%m-%d'


class TestRotationOperations:
    """Test suite for rotation operations."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        import os
        os.chdir(self.test_dir)
        
        yield
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_check_and_rotate(self):
        """Verify check_and_rotate delegates to Nibandha."""
        from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager
        
        logger = PravphaLoggingManager.get_logger()
        nb = PravphaLoggingManager.get_instance()
        
        # Should not raise exception
        result = LogRotationUtils.check_and_rotate(nb)
        
        assert isinstance(result, bool), \
            "check_and_rotate should return boolean"
    
    def test_cleanup_old_logs(self):
        """Verify cleanup_old_logs delegates to Nibandha."""
        from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager
        
        logger = PravphaLoggingManager.get_logger()
        nb = PravphaLoggingManager.get_instance()
        
        # Should not raise exception
        count = LogRotationUtils.cleanup_old_logs(nb)
        
        assert isinstance(count, int), \
            "cleanup_old_logs should return integer count"
        assert count >= 0, \
            "Cleanup count should be non-negative"
