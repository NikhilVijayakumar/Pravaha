import unittest
from typing import List
from pravaha.domain.storage.provider.storage_api_provider import StorageAPIProvider
from pravaha.domain.storage.model.artifact_metadata import GroupedArtifactMetadata

class TestStorageAPIGrouping(unittest.TestCase):
    def test_group_artifacts(self):
        # Mock artifacts
        artifacts = [
            {
                "feature": "feat1",
                "product": None,
                "model": "script",
                "version": 1,
                "stage": "intermediate",
                "path": "/path/to/script_1.json",
                "created_at": "2023-01-01",
                "display_name": "Script"
            },
            {
                "feature": "feat1",
                "product": None,
                "model": "script",
                "version": 2,
                "stage": "intermediate",
                "path": "/path/to/script_2.json",
                "created_at": "2023-01-02",
                "display_name": "Script"
            },
            {
                "feature": "feat1",
                "product": None,
                "model": "other",
                "version": 1,
                "stage": "intermediate",
                "path": "/path/to/other.json",
                "created_at": "2023-01-01",
                "display_name": "Other"
            }
        ]

        # Initialize provider (mocking dependencies as None since we only test the static-like method)
        provider = StorageAPIProvider(None, None, None, None)
        
        # Test grouping
        grouped = provider._group_artifacts(artifacts)
        
        self.assertEqual(len(grouped), 2)
        
        # Check Script group
        script_group = next(g for g in grouped if g["model"] == "script")
        self.assertEqual(script_group["latest_version"], 2)
        self.assertEqual(len(script_group["versions"]), 2)
        self.assertEqual(script_group["versions"][0]["version"], 2)  # Sorted descending
        self.assertEqual(script_group["versions"][1]["version"], 1)
        
        # Check Other group
        other_group = next(g for g in grouped if g["model"] == "other")
        self.assertEqual(other_group["latest_version"], 1)
        self.assertEqual(len(other_group["versions"]), 1)

if __name__ == "__main__":
    unittest.main()
