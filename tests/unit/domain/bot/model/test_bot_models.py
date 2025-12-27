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

def test_utility_request_valid():
    req = UtilityRequest(task_name="util", inputs=[{"a": 1}])
    assert req.task_name == "util"
    assert req.inputs == [{"a": 1}]
