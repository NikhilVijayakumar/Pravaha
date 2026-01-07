import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import json
import sys
import os

# Adjust path
sys.path.append(os.path.abspath("src/nikhil"))
sys.modules["fastapi"] = MagicMock()
sys.modules["pydantic"] = MagicMock()

from pravaha.domain.storage.provider.knowledge_storage_provider import KnowledgeStorageProvider

class TestKnowledgeStorage(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_storage_manager = MagicMock()
        self.provider = KnowledgeStorageProvider(self.mock_storage_manager)

    async def test_browse_recursive(self):
        # Mock directory structure
        # root/
        #   FolderA/ (dir)
        #     file1.json
        #   file2.txt
        
        base_path = MagicMock(spec=Path)
        base_path.exists.return_value = True
        self.mock_storage_manager.get_path.return_value = base_path
        
        folder_a = MagicMock(spec=Path)
        folder_a.name = "FolderA"
        folder_a.is_dir.return_value = True
        folder_a.relative_to.return_value = Path("FolderA")
        
        file1 = MagicMock(spec=Path)
        file1.name = "file1.json"
        file1.is_dir.return_value = False
        file1.stat.return_value.st_size = 100
        file1.relative_to.return_value = Path("FolderA/file1.json")
        
        file2 = MagicMock(spec=Path)
        file2.name = "file2.txt"
        file2.is_dir.return_value = False
        file2.stat.return_value.st_size = 200
        file2.relative_to.return_value = Path("file2.txt")
        
        # Determine iterdir behavior
        # base_path.iterdir() -> [FolderA, file2]
        # folder_a.iterdir() -> [file1]
        
        base_path.iterdir.return_value = [folder_a, file2]
        folder_a.iterdir.return_value = [file1]
        
        # When checking iterdir on recursive call, we need proper mapping.
        # However, _list_directory takes (directory, base_path).
        # We can mock _list_directory logic if we want, OR trust iterdir mocks.
        # But iterdir returning different lists based on instance is tricky with simple Mocks if we don't control them well.
        # Let's side_effect iterdir? No, these are distinct objects.
        
        # We need to ensure folder_a.iterdir() works.
        # Since folder_a is returned by base_path.iterdir(), it is a Mock object.
        # We configured it above.
        
        result = await self.provider.browse()
        items = result["items"]
        
        # Sort order: Folders first, then files.
        # FolderA should be first.
        self.assertEqual(items[0]["name"], "FolderA")
        self.assertEqual(items[0]["type"], "folder")
        self.assertEqual(len(items[0]["children"]), 1, "FolderA should have 1 child")
        self.assertEqual(items[0]["children"][0]["name"], "file1.json")
        self.assertEqual(items[0]["children"][0]["path"], "FolderA/file1.json")
        
        self.assertEqual(items[1]["name"], "file2.txt")
        self.assertEqual(items[1]["type"], "file")
        self.assertEqual(items[1]["path"], "file2.txt")

    async def test_read_json(self):
        base_path = MagicMock(spec=Path)
        base_path.resolve.return_value = base_path # Root
        self.mock_storage_manager.get_path.return_value = base_path
        
        target_file = MagicMock(spec=Path)
        target_file.resolve.return_value = target_file
        target_file.exists.return_value = True
        target_file.is_file.return_value = True
        target_file.suffix = ".json"
        target_file.read_text.return_value = '{"key": "value"}'
        
        # Mock path construction
        # root / path -> target_file
        base_path.__truediv__.return_value = target_file
        
        # Security check: relative_to
        target_file.relative_to.return_value = Path("some/path.json")
        
        result = await self.provider.read("some/path.json")
        self.assertEqual(result["content"], {"key": "value"})

if __name__ == '__main__':
    unittest.main()
