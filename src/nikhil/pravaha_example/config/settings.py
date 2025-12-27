from enum import Enum

class ApplicationType(str, Enum):
    MATH_ASSISTANT = "math_assistant"

class UtilsType(str, Enum):
    CALCULATOR = "calculator"

class ExecutionTarget(str, Enum):
    LOCAL = "local"
