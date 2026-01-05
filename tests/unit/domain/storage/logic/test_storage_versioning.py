import unittest
from pathlib import Path
from typing import List
from datetime import datetime
from unittest.mock import MagicMock, patch
import sys
import os

# Adjust path and mock fastapi and pydantic
sys.path.append(os.path.abspath("src/nikhil"))
sys.modules["fastapi"] = MagicMock()
sys.modules["pydantic"] = MagicMock()

from pravaha.domain.storage.protocol.artifact_resolver_protocol import StorageStage
from pravaha.domain.storage.logic.version_resolver import ArtifactVersionResolver

class TestStorageVersioning(unittest.TestCase):
    def setUp(self):
        self.mock_storage = MagicMock()
        self.mock_llm = MagicMock()
        self.resolver = ArtifactVersionResolver(self.mock_storage, self.mock_llm)

    def test_intermediate_versions(self):
        """Test that timestamps are correctly sorted and converted to versions 1..N"""
        
        # Mock directory structure
        # Base dir: .Amsha/intermediate/MyFeature
        # Subdirs: output_20250101120000, output_20250102120000
        
        base_dir = MagicMock(spec=Path)
        base_dir.exists.return_value = True
        
        dir1 = MagicMock(spec=Path)
        dir1.name = "output_20250101120000"
        dir1.is_dir.return_value = True
        # File exists check
        file1 = MagicMock(spec=Path)
        file1.exists.return_value = True
        dir1.__truediv__.return_value = file1 # dir1 / "alias.json"
        
        dir2 = MagicMock(spec=Path)
        dir2.name = "output_20250102120000"
        dir2.is_dir.return_value = True
        file2 = MagicMock(spec=Path)
        file2.exists.return_value = True
        dir2.__truediv__.return_value = file2
        
        # Unrelated dir
        dir3 = MagicMock(spec=Path)
        dir3.name = "other_folder"
        dir3.is_dir.return_value = True

        base_dir.iterdir.return_value = [dir2, dir3, dir1] # Unsorted input
        
        # Call private method logic (we can check public too if we mock _get_base_directory)
        # But let's verify logic of _get_intermediate_versions
        versions = self.resolver._get_intermediate_versions(base_dir, "alias")
        
        # We expect 2 valid versions, so [1, 2]
        self.assertEqual(versions, [1, 2])
        
        # If we use get_latest_version
        with patch.object(self.resolver, '_get_base_directory', return_value=base_dir):
            with patch.object(self.resolver, '_resolve_model_alias', return_value="alias"):
                latest = self.resolver.get_latest_version(
                    StorageStage.INTERMEDIATE, "MyFeature", None, "model_key"
                )
                self.assertEqual(latest, 2)

    def test_multi_extension_support(self):
        """Test that different extensions (.md, .yaml) are detected"""
        base_dir = MagicMock(spec=Path)
        base_dir.exists.return_value = True
        
        # Folder with markdown
        dir1 = MagicMock(spec=Path)
        dir1.name = "output_20250101120000"
        dir1.is_dir.return_value = True
        # Mock finding alias.md
        # The logic iterates extensions. We need to mock __truediv__ to return exist=True for .md
        
        def truediv_side_effect(arg):
            m = MagicMock(spec=Path)
            if arg == "alias.md":
                m.exists.return_value = True
            else:
                m.exists.return_value = False
            return m
            
        dir1.__truediv__.side_effect = truediv_side_effect
        
        base_dir.iterdir.return_value = [dir1]
        
        versions = self.resolver._get_intermediate_versions(base_dir, "alias")
        self.assertEqual(versions, [1])

    def test_deduplication(self):
        """Test scanning deduplication via checking _group_artifacts logic"""
        # We need to test StorageAPIProvider._group_artifacts logic directly.
        # But import it first
        from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider
        
        # Partially mock
        provider = StorageAPIProvider(MagicMock(), MagicMock(), MagicMock(), MagicMock())
        
        # Duplicate entries
        artifacts = [
            {
                "feature": "F1",
                "product": None,
                "model": "m1",
                "version": 1,
                "stage": "final",
                "path": "path/v1.json",
                "created_at": "2025-01-01",
                "display_name": "M1.json"
            },
            {
                "feature": "F1",
                "product": None,
                "model": "m1",
                "version": 1,
                "stage": "final",
                "path": "path/v1.json", # Duplicate
                "created_at": "2025-01-01",
                "display_name": "M1.json"
            }
        ]
        
        grouped = provider._group_artifacts(artifacts)
        self.assertEqual(len(grouped), 1)
        self.assertEqual(len(grouped[0]["versions"]), 1)
        
        # Test diff features -> distinct groups
        artifacts_mixed = [
             {
                "feature": "F1",
                "product": None,
                "model": "m1",
                "version": 1,
                "stage": "final",
                "path": "p1",
                "created_at": "d1",
                "display_name": "n1"
            },
             {
                "feature": "F2",
                "product": None,
                "model": "m1",
                "version": 1,
                "stage": "final",
                "path": "p2",
                "created_at": "d2",
                "display_name": "n2"
            }
        ]
        grouped_mixed = provider._group_artifacts(artifacts_mixed)
        self.assertEqual(len(grouped_mixed), 2)

if __name__ == '__main__':
    unittest.main()
