"""
Tests for logger propagation behavior.

Verifies that Pravaha logger does not propagate to root logger,
preventing log leakage in multi-application environments.
"""

import pytest
import logging
from pathlib import Path
import tempfile
import shutil

from pravaha.domain.logging.manager.logging_manager import PravphaLoggingManager


class TestLoggerPropagation:
    """Test suite for logger propagation behavior."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        # Reset singleton before each test
        PravphaLoggingManager._instance = None
        
        # Create temp directory for .Nibandha
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        import os
        os.chdir(self.test_dir)
        
        yield
        
        # Cleanup
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        PravphaLoggingManager._instance = None
    
    def test_logger_propagate_is_false(self):
        """Verify Pravaha logger has propagate=False."""
        logger = PravphaLoggingManager.get_logger()
        
        assert logger.propagate is False, \
            "Logger propagate must be False to prevent log leakage"
    
    def test_logger_has_handlers(self):
        """Verify logger has handlers attached directly."""
        logger = PravphaLoggingManager.get_logger()
        
        assert len(logger.handlers) > 0, \
            "Logger must have handlers attached"
        
        # Should have FileHandler and StreamHandler
        handler_types = [type(h).__name__ for h in logger.handlers]
        assert 'FileHandler' in handler_types, \
            "Logger should have FileHandler"
        assert 'StreamHandler' in handler_types, \
            "Logger should have StreamHandler"
    
    def test_root_logger_isolation(self):
        """Verify Pravaha logger doesn't add handlers to root logger."""
        root_logger = logging.getLogger()
        initial_handler_count = len(root_logger.handlers)
        
        # Initialize Pravaha logger
        pravaha_logger = PravphaLoggingManager.get_logger()
        pravaha_logger.info("Test message")
        
        # Root logger should not gain new handlers
        assert len(root_logger.handlers) == initial_handler_count, \
            "Root logger should not gain handlers from Pravaha initialization"
    
    def test_logger_name(self):
        """Verify logger has correct name."""
        logger = PravphaLoggingManager.get_logger()
        
        assert logger.name == "Pravaha", \
            "Logger name must be 'Pravaha'"
    
    def test_singleton_pattern(self):
        """Verify logger uses singleton pattern."""
        logger1 = PravphaLoggingManager.get_logger()
        logger2 = PravphaLoggingManager.get_logger()
        
        assert logger1 is logger2, \
            "get_logger() should return same instance (singleton)"
    
    def test_no_interactive_prompts(self):
        """Verify initialization doesn't prompt for user input."""
        # This test passes if it doesn't hang waiting for input
        import time
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Logger initialization hung - likely waiting for user input")
        
        # Set 5-second timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)
        
        try:
            logger = PravphaLoggingManager.get_logger()
            signal.alarm(0)  # Cancel alarm
            
            assert logger is not None, "Logger should initialize without prompts"
        except TimeoutError:
            pytest.fail("Logger initialization hung - interactive prompts detected")


class TestLogLevels:
    """Test suite for log level configuration."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        PravphaLoggingManager._instance = None
        
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        import os
        os.chdir(self.test_dir)
        
        yield
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        PravphaLoggingManager._instance = None
    
    def test_default_log_level(self):
        """Verify default log level is INFO."""
        logger = PravphaLoggingManager.get_logger()
        
        assert logger.level == logging.INFO, \
            "Default log level should be INFO"
    
    def test_custom_log_level(self):
        """Verify custom log level can be set."""
        PravphaLoggingManager.initialize(log_level="DEBUG")
        logger = PravphaLoggingManager.get_logger()
        
        assert logger.level == logging.DEBUG, \
            "Custom log level should be respected"
