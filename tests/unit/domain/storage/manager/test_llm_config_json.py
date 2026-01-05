import unittest
import shutil
import json
import yaml
from pathlib import Path
from pravaha.domain.storage.manager.llm_config_manager import LLMConfigManager

class TestLLMConfigJSONCaching(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("tests/temp_config_test")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.dummy_yaml = self.test_dir / "dummy_config.yaml"
        
        # Create a dummy YAML file
        data = {
            "llm": {
                "category": {
                    "models": {
                        "test_model": {
                            "output_config": {
                                "display_name": "Test Model"
                            }
                        }
                    }
                }
            }
        }
        with open(self.dummy_yaml, "w") as f:
            yaml.dump(data, f)
            
        # Clear any existing cache
        self.cache_dir = Path.cwd() / ".Pravaha" / "config"
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        # Clean up cache created by test
        if self.cache_dir.exists():
             shutil.rmtree(self.cache_dir)

    def test_yaml_to_json_cache(self):
        # Initialize manager with YAML path
        manager = LLMConfigManager(self.dummy_yaml)
        
        # Verify JSON file exists
        json_cache = self.cache_dir / "llm_config.json"
        self.assertTrue(json_cache.exists(), "JSON cache file should be created")
        
        # Verify Content matches
        with open(json_cache, "r") as f:
            cached_data = json.load(f)
        
        self.assertEqual(cached_data["llm"]["category"]["models"]["test_model"]["output_config"]["display_name"], "Test Model")
        
        # Verify Manager loaded it
        config = manager.get_all_config()
        self.assertEqual(config["llm"]["category"]["models"]["test_model"]["output_config"]["display_name"], "Test Model")

    def test_load_existing_json_cache(self):
        # Manually create JSON cache
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        json_cache = self.cache_dir / "llm_config.json"
        data = {"foo": "bar"}
        with open(json_cache, "w") as f:
            json.dump(data, f)
            
        # Initialize without path
        manager = LLMConfigManager()
        
        # Verify it loaded from cache
        self.assertEqual(manager.get_all_config()["foo"], "bar")

if __name__ == "__main__":
    unittest.main()
