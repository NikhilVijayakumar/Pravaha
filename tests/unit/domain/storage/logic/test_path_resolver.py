import pytest
from pathlib import Path
from unittest.mock import MagicMock

from pravaha.domain.storage.logic.path_resolver import StoragePathResolver
from pravaha.domain.storage.protocol.artifact_resolver_protocol import StorageStage, ArtifactVersionResolverProtocol
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from pravaha.domain.llm.protocol.llm_config_protocol import LLMConfigManagerProtocol

@pytest.fixture
def mock_storage_manager():
    sm = MagicMock(spec=LocalStorageManager)
    sm.get_path.side_effect = lambda cat: Path(f"/tmp/pravaha/{cat}")
    return sm

@pytest.fixture
def mock_llm_config():
    cm = MagicMock(spec=LLMConfigManagerProtocol)
    return cm

@pytest.fixture
def mock_version_resolver():
    vr = MagicMock(spec=ArtifactVersionResolverProtocol)
    return vr

@pytest.fixture
def resolver(mock_storage_manager, mock_llm_config, mock_version_resolver):
    return StoragePathResolver(mock_storage_manager, mock_llm_config, mock_version_resolver)

def test_resolve_output_path_v1(resolver, mock_llm_config, mock_version_resolver):
    # Setup
    mock_version_resolver.get_next_version.return_value = 1
    mock_llm_config.resolve_output_config.return_value = {"alias": "model-v1", "structure": "flat"}
    
    # Execute
    path = resolver.resolve_output_path(StorageStage.INTERMEDIATE, "Feature", None, "model")
    
    # Assert
    # Base: /tmp/pravaha/intermediate/Feature
    # Filename: model-v1.json (since v1)
    expected = Path("/tmp/pravaha/intermediate/Feature/model-v1.json")
    assert path == expected

def test_resolve_output_path_v3(resolver, mock_llm_config, mock_version_resolver):
    # Setup
    mock_version_resolver.get_next_version.return_value = 3
    mock_llm_config.resolve_output_config.return_value = {"alias": "model", "structure": "flat"}
    
    # Execute
    path = resolver.resolve_output_path(StorageStage.INTERMEDIATE, "Feature", None, "model")
    
    # Assert
    # Base: /tmp/pravaha/intermediate/Feature
    # Filename: model_2.json (v3 -> alias_2)
    expected = Path("/tmp/pravaha/intermediate/Feature/model_2.json")
    assert path == expected

def test_resolve_output_path_folder_structure(resolver, mock_llm_config, mock_version_resolver):
    # Setup
    mock_version_resolver.get_next_version.return_value = 2
    mock_llm_config.resolve_output_config.return_value = {
        "alias": "gpt", 
        "structure": "folder",
        "folder_name": "openai"
    }
    
    # Execute
    path = resolver.resolve_output_path(StorageStage.FINAL, "Feature", "Product", "gpt_model")
    
    # Assert
    # Base: /tmp/pravaha/output/Product/Feature/openai
    # Filename: gpt_1.json (v2)
    expected = Path("/tmp/pravaha/output/Product/Feature/openai/gpt_1.json")
    assert path == expected
