# src.nikhil.pravaha.domain.api.protocol.task_config_protocol

from enum import Enum
from typing import Protocol, Type


class TaskConfigProtocol(Protocol):
    UtilsType: Type[Enum]
    ApplicationType: Type[Enum]
    ExecutionTarget: Type[Enum]
