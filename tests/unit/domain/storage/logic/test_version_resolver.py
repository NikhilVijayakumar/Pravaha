import pytest
from pathlib import Path
from unittest.mock import MagicMock

from pravaha.domain.storage.logic.version_resolver import ArtifactVersionResolver
from pravaha.domain.storage.protocol.artifact_resolver_protocol import StorageStage
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from pravaha.domain.storage.protocol.llm_config_protocol import LLMConfigManagerProtocol

@pytest.fixture
def mock_storage_manager():
    sm = MagicMock(spec=LocalStorageManager)
    # Mock get_path to return some temp paths
    sm.get_path.side_effect = lambda cat: Path(f"/tmp/pravaha/{cat}")
    return sm

@pytest.fixture
def mock_llm_config():
    cm = MagicMock(spec=LLMConfigManagerProtocol)
    return cm

@pytest.fixture
def resolver(mock_storage_manager, mock_llm_config):
    return ArtifactVersionResolver(mock_storage_manager, mock_llm_config)

def test_resolve_base_directory_intermediate_flat(resolver, mock_storage_manager, mock_llm_config):
    # Setup
    mock_llm_config.resolve_output_config.return_value = {"alias": "gemini-flash", "structure": "flat"}
    
    # Execute
    path = resolver._get_base_directory(StorageStage.INTERMEDIATE, "TestFeature", None, "gemini")
    
    # Assert
    # Intermediate root -> /tmp/pravaha/intermediate
    # Feature -> TestFeature
    # Flat -> No extra folder
    expected = Path("/tmp/pravaha/intermediate/TestFeature")
    assert path == expected

def test_resolve_base_directory_final_folder(resolver, mock_storage_manager, mock_llm_config):
    # Setup
    mock_llm_config.resolve_output_config.return_value = {
        "alias": "gpt-4", 
        "structure": "folder", 
        "folder_name": "openai_gpt"
    }
    
    # Execute
    path = resolver._get_base_directory(StorageStage.FINAL, "TestFeature", "TestProduct", "gpt")
    
    # Assert
    # Final root -> /tmp/pravaha/output
    # Product -> TestProduct
    # Feature -> TestFeature
    # Folder -> openai_gpt
    expected = Path("/tmp/pravaha/output/TestProduct/TestFeature/openai_gpt")
    assert path == expected

def test_get_next_version_no_files(resolver):
    # Mock _get_base_directory to return a non-existent path
    with pytest.MonkeyPatch.context() as m:
        m.setattr(resolver, "_get_base_directory", lambda *args: Path("/non/existent/path"))
        
        # Should start at 1
        version = resolver.get_next_version(StorageStage.INTERMEDIATE, "F", "P", "M")
        assert version == 1

def test_get_versions_parsing(resolver, tmp_path):
    # Create fake files
    (tmp_path / "model.json").touch() # v1
    (tmp_path / "model_1.json").touch() # v2
    (tmp_path / "model_5.json").touch() # v6
    (tmp_path / "other.json").touch() # Ignored
    
    versions = resolver._get_versions(tmp_path, "model")
    assert versions == [1, 2, 6]
    
    # Next version should be 7
    with pytest.MonkeyPatch.context() as m:
         m.setattr(resolver, "_get_base_directory", lambda *args: tmp_path)
         m.setattr(resolver, "_resolve_model_alias", lambda *args: "model")
         
         next_v = resolver.get_next_version(StorageStage.FINAL, "F", "P", "M")
         assert next_v == 7
