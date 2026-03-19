"""
Tests for AuthConfig.
"""

from pravaha.domain.auth.config.auth_config import AuthConfig

def test_auth_config_defaults():
    """Test default values."""
    config = AuthConfig.default()
    assert config.enabled is True
    assert "/health" in config.exempt_paths
    assert "/docs" in config.exempt_paths

def test_auth_config_disabled():
    """Test disabled factory method."""
    config = AuthConfig.disabled()
    assert config.enabled is False
    # Defaults should still be present even if disabled, though unrelated
    assert "/health" in config.exempt_paths
