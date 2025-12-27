from pravaha.domain.storage.model.storage_config_request import StorageConfigRequest
import pytest
from pydantic import ValidationError

def test_storage_config_request_valid():
    data = {
        "output_path": "/tmp/out",
        "intermediate_path": "/tmp/inter",
        "knowledge_path": "/tmp/know"
    }
    req = StorageConfigRequest(**data)
    assert req.output_path == "/tmp/out"
    assert req.intermediate_path == "/tmp/inter"
    assert req.knowledge_path == "/tmp/know"

def test_storage_config_request_missing_field():
    data = {
        "output_path": "/tmp/out"
    }
    with pytest.raises(ValidationError):
        StorageConfigRequest(**data)
