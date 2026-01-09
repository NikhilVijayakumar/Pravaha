import pytest
import os
from pathlib import Path
from pravaha_example.config.settings import ApplicationType, UtilsType


def test_get_config_returns_dict(bot_manager_with_config):
    """Test that get_config returns a dictionary for a task with registered config."""
    bot_manager, config_path = bot_manager_with_config
    
    config = bot_manager.get_config(ApplicationType.MATH_ASSISTANT)
    
    assert config is not None
    assert isinstance(config, dict)
    assert "crew_name" in config
    assert config["crew_name"] == "Math Bot Crew"
    assert "crews" in config
    assert "pipeline" in config


def test_get_config_returns_none_for_unregistered_task(bot_manager_with_config):
    """Test that get_config returns None for tasks without registered config."""
    bot_manager, _ = bot_manager_with_config
    
    # Calculator utility doesn't have a config registered
    config = bot_manager.get_config(UtilsType.CALCULATOR)
    
    assert config is None


def test_get_config_parses_yaml_correctly(bot_manager_with_config):
    """Test that YAML is correctly parsed into Python data structures."""
    bot_manager, _ = bot_manager_with_config
    
    config = bot_manager.get_config(ApplicationType.MATH_ASSISTANT)
    
    assert config["crews"]["math_crew"]["input"][0]["key_name"] == "expression"
    assert config["pipeline"] == ["math_crew"]


def test_get_config_handles_missing_file_gracefully(bot_manager):
    """Test that missing config files return None gracefully."""
    from pravaha_example.service.server import SimpleBotManager
    
    bot = SimpleBotManager()
    bot.config_paths[ApplicationType.MATH_ASSISTANT] = "non_existent_file.yaml"
    
    config = bot.get_config(ApplicationType.MATH_ASSISTANT)
    
    assert config is None


@pytest.fixture
def bot_manager():
    """Create a simple bot manager instance."""
    from pravaha_example.service.server import SimpleBotManager
    return SimpleBotManager()


@pytest.fixture
def bot_manager_with_config():
    """Create a bot manager with a test config file."""
    from pravaha_example.service.server import SimpleBotManager
    import tempfile
    import yaml
    
    # Create temporary config file
    config_data = {
        "crew_name": "Math Bot Crew",
        "usecase": "Mathematical Expression Evaluation",
        "module_name": "math_assistant",
        "crews": {
            "math_crew": {
                "input": [
                    {
                        "key_name": "expression",
                        "source": "direct",
                        "value": "2 + 2"
                    }
                ],
                "steps": [
                    {
                        "task_file": "data/crew/tasks/evaluate_task.yaml",
                        "agent_file": "data/crew/agents/math_agent.yaml"
                    }
                ]
            }
        },
        "pipeline": ["math_crew"]
    }
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name
    
    # Create bot manager with config
    bot = SimpleBotManager()
    bot.config_paths[ApplicationType.MATH_ASSISTANT] = temp_path
    
    yield bot, temp_path
    
    # Cleanup
    os.unlink(temp_path)
