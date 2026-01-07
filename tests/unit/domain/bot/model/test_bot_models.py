from pravaha.domain.bot.model.application_request import ApplicationRequest
from pravaha.domain.bot.model.utility_request import UtilityRequest
import pytest
from pydantic import ValidationError

def test_application_request_valid():
    req = ApplicationRequest(task_name="my_task", inputs=[{"k": "v"}])
    assert req.task_name == "my_task"
    assert req.inputs == [{"k": "v"}]

def test_application_request_missing_task_name():
    with pytest.raises(ValidationError):
        ApplicationRequest(inputs=[])

def test_application_request_with_llm_config_override():
    """Test that llm_config_override field is accepted and stored correctly"""
    llm_config = {
        "model_config": {"base_url": "http://localhost:1234/v1", "model": "test-model"},
        "llm_parameters": {"temperature": 0.8}
    }
    req = ApplicationRequest(task_name="my_task", llm_config_override=llm_config)
    assert req.task_name == "my_task"
    assert req.llm_config_override == llm_config

def test_application_request_without_llm_config_override():
    """Test that llm_config_override is optional and defaults to None"""
    req = ApplicationRequest(task_name="my_task")
    assert req.task_name == "my_task"
    assert req.llm_config_override is None

def test_application_request_full():
    """Test with all fields populated"""
    llm_config = {"model_config": {"model": "test"}}
    inputs = [{"scientific_concept": {"value": "test"}}]
    req = ApplicationRequest(
        task_name="generate_scientific_knowledge_application",
        inputs=inputs,
        llm_config_override=llm_config
    )
    assert req.task_name == "generate_scientific_knowledge_application"
    assert req.inputs == inputs
    assert req.llm_config_override == llm_config

def test_utility_request_valid():
    req = UtilityRequest(task_name="util", inputs=[{"a": 1}])
    assert req.task_name == "util"
    assert req.inputs == [{"a": 1}]

