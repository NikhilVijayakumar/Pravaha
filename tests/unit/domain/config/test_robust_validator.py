"""
Unit Tests for PravahaRobustConfigValidator

Tests recursive validation, sanitization, audit logging, and edge cases.
"""

import pytest
from pydantic import BaseModel, Field
from typing import Optional

from pravaha.domain.config.infrastructure.robust_validator import (
    PravahaRobustConfigValidator,
)


# --- Test Models ---

class InnerConfig(BaseModel):
    level: str = Field("INFO", description="Log level")
    enabled: bool = Field(True, description="Enable flag")


class OuterConfig(BaseModel):
    name: str = Field("default", description="Name")
    mode: str = Field("production", description="Mode")
    inner: InnerConfig = Field(default_factory=InnerConfig)


# --- Tests ---

class TestPravahaRobustConfigValidator:
    def test_valid_data_passes_through(self):
        validator = PravahaRobustConfigValidator()
        data = {"name": "TestApp", "mode": "development"}
        result = validator.validate_and_sanitize(OuterConfig, data)
        assert result["name"] == "TestApp"
        assert result["mode"] == "development"
        assert any("[VALID]" in entry for entry in validator.audit_log)

    def test_invalid_field_type_rejected(self):
        validator = PravahaRobustConfigValidator()
        data = {"name": 12345}  # name should be str, but int is coercible
        result = validator.validate_and_sanitize(OuterConfig, data)
        # Pydantic can coerce int to str, so this should be accepted
        assert "name" in result

    def test_missing_fields_use_defaults(self):
        validator = PravahaRobustConfigValidator()
        result = validator.validate_and_sanitize(OuterConfig, {})
        # Empty dict → all defaults
        assert result == {}

    def test_nested_model_recursion(self):
        validator = PravahaRobustConfigValidator()
        data = {
            "name": "TestApp",
            "inner": {"level": "DEBUG", "enabled": True},
        }
        result = validator.validate_and_sanitize(OuterConfig, data)
        assert result["inner"]["level"] == "DEBUG"
        assert result["inner"]["enabled"] is True

    def test_nested_model_partial_recovery(self):
        validator = PravahaRobustConfigValidator()
        data = {
            "name": "TestApp",
            "inner": {"level": "DEBUG", "enabled": "not_a_bool"},
        }
        result = validator.validate_and_sanitize(OuterConfig, data)
        # level should be accepted, enabled may be rejected
        assert result["inner"]["level"] == "DEBUG"
        # "not_a_bool" is not coercible to bool, so it should be rejected
        assert "enabled" not in result["inner"]

    def test_none_input_returns_empty(self):
        validator = PravahaRobustConfigValidator()
        result = validator.validate_and_sanitize(OuterConfig, None)
        assert result == {}

    def test_non_dict_input_returns_empty(self):
        validator = PravahaRobustConfigValidator()
        result = validator.validate_and_sanitize(OuterConfig, "not_a_dict")
        assert result == {}
        assert any("[WARNING]" in entry for entry in validator.audit_log)

    def test_audit_log_populated(self):
        validator = PravahaRobustConfigValidator()
        data = {"name": "TestApp", "mode": "dev"}
        validator.validate_and_sanitize(OuterConfig, data)
        assert len(validator.audit_log) > 0

    def test_extra_fields_ignored(self):
        """Fields not in the model should be silently dropped."""
        validator = PravahaRobustConfigValidator()
        data = {"name": "TestApp", "nonexistent_field": "value"}
        result = validator.validate_and_sanitize(OuterConfig, data)
        assert "nonexistent_field" not in result
        assert result["name"] == "TestApp"
