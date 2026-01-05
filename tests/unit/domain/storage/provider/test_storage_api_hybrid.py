import pytest
import os
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path
from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider
from pravaha.domain.storage.manager.local_storage_manager import LocalStorageManager
from pravaha.domain.storage.protocol.llm_config_protocol import LLMConfigManagerProtocol
from pravaha.domain.storage.protocol.artifact_resolver_protocol import StoragePathResolverProtocol, ArtifactVersionResolverProtocol, StorageStage

@pytest.fixture
def mock_deps():
    storage = MagicMock(spec=LocalStorageManager)
    llm = MagicMock(spec=LLMConfigManagerProtocol)
    path = MagicMock(spec=StoragePathResolverProtocol)
    version = MagicMock(spec=ArtifactVersionResolverProtocol)
    
    # Setup Paths
    real_path_mock = MagicMock(spec=Path)
    # Important: make exists() return True on the path object itself
    real_path_mock.exists.return_value = True
    real_path_mock.resolve.return_value = Path("/tmp/pravaha/output")
    real_path_mock.__truediv__.side_effect = lambda other: Path(f"/tmp/pravaha/output/{other}")
    
    # When get_path is called, return this robust mock or a real Path that relies on patched filesystem
    # Simpler: Just rely on patching Path.exists everywhere if using real Path objects
    # But earlier failure suggested the path object created inside wasn't patched?
    # Let's use patch("pathlib.Path.exists") closer to the call or ensure it covers all usage.
    
    # Just return a real path, we will patch pathlib.Path methods globally in tests
    storage.get_path.side_effect = lambda cat: Path(f"/tmp/pravaha/{cat}")
    
    return storage, llm, path, version

@pytest.mark.asyncio
async def test_browse_knowledge_legacy(mock_deps):
    storage, llm, path, ver = mock_deps
    provider = StorageAPIProvider(storage, llm, path, ver)
    
    with patch("pathlib.Path.iterdir") as mock_iter:
        # Mock file system for knowledge
        mock_item = MagicMock()
        mock_item.name = "doc.md"
        mock_item.is_dir.return_value = False
        mock_item.is_file.return_value = True
        mock_item.stat.return_value.st_size = 100
        mock_iter.return_value = [mock_item]
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_dir", return_value=True), \
             patch("pathlib.Path.resolve", side_effect=lambda: Path("/tmp/pravaha/knowledge")):
                
            handler = provider._create_browse_handler("knowledge")
            result = await handler(path="")
            
            assert "items" in result
            assert result["items"][0]["name"] == "doc.md"

@pytest.mark.asyncio
async def test_browse_output_artifacts(mock_deps):
    storage, llm, path, ver = mock_deps
    provider = StorageAPIProvider(storage, llm, path, ver)
    
    # We mock _list_artifacts_logic directly to test routing, or mock scan_dir
    with patch.object(provider, "_scan_dir") as mock_scan:
        # Simulate scan_dir populating the list
        def side_effect(directory, artifacts, *args):
            artifacts.append({
                "model": "gpt",
                "version": 1,
                "display_name": "GPT Model",
                "path": "/tmp/out.json"
            })
        mock_scan.side_effect = side_effect
        
        # We need exists to return True for the base_root check
        # And iterdir to return something to scan
        mock_dir = MagicMock(spec=Path)
        mock_dir.is_dir.return_value = True
        mock_dir.name = "feature_x"
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.iterdir", return_value=[mock_dir]):
            
            handler = provider._create_browse_handler("output")
            result = await handler(path="")
            
            # Should be a list of artifacts
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["display_name"] == "GPT Model"

@pytest.mark.asyncio
async def test_read_knowledge_legacy(mock_deps):
    storage, _, _, _ = mock_deps
    provider = StorageAPIProvider(storage, MagicMock(), MagicMock(), MagicMock())
    
    with patch("pathlib.Path.read_text", return_value="content"), \
         patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.is_file", return_value=True), \
         patch("pathlib.Path.resolve") as mock_resolve:
         
        # Make sure resolve is safe
        mock_resolve.return_value = Path("/tmp/pravaha/knowledge/file.txt")
        
        handler = provider._create_read_handler("knowledge")
        result = await handler(path="file.txt")
        
        assert result["content"] == "content"
@pytest.mark.asyncio
async def test_read_output_artifact(mock_deps):
    storage, _, _, _ = mock_deps
    provider = StorageAPIProvider(storage, MagicMock(), MagicMock(), MagicMock())
    
    with patch("pathlib.Path.read_text", return_value='{"key": "val"}'), \
         patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.is_file", return_value=True), \
         patch("pathlib.Path.resolve") as mock_resolve:
         
        # Absolute path passed
        mock_resolve.return_value = Path("/tmp/pravaha/output/artifact.json")
        
        handler = provider._create_read_handler("output")
        result = await handler(path="/tmp/pravaha/output/artifact.json")
        
        assert result["content"] == {"key": "val"}

@pytest.mark.asyncio
async def test_llm_config_caching():
    # Setup temporary source config
    import tempfile
    import shutil
    import sys
    from unittest.mock import MagicMock
    
    # Mock yaml module since it might be missing in test env
    mock_yaml = MagicMock()
    mock_yaml.safe_load.return_value = {}
    
    with patch.dict(sys.modules, {"yaml": mock_yaml}):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            tmp.write("llm:\n  test: data")
            tmp_path = Path(tmp.name)
            
        try:
            # Initialize manager with source config
            # This should trigger copying to .Pravaha/config/llm_config.yaml
            
            with patch("pathlib.Path.cwd", return_value=Path("/tmp/pravaha_test_project")):
                 with patch("shutil.copy2") as mock_copy:
                     # Mock directory properties
                     with patch("pathlib.Path.mkdir"), \
                          patch("pathlib.Path.exists", side_effect=lambda: True): 
                         
                         # Import inside the patch context
                         from pravaha.domain.storage.manager.llm_config_manager import LLMConfigManager
                         
                         manager = LLMConfigManager(config_path=tmp_path)
                         
                         # Verify copy was called
                         # Expected target: /tmp/pravaha_test_project/.Pravaha/config/llm_config.yaml
                         mock_copy.assert_called_once()
                         args, _ = mock_copy.call_args
                         assert args[0] == tmp_path
                         assert str(args[1]).endswith("llm_config.yaml")

        finally:
            if tmp_path.exists():
                os.unlink(tmp_path)
